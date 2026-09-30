import base64
import hashlib
import io
import os
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from typing import Optional
import bcrypt
import jwt
import pyotp
import qrcode
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from app.database import users_collection, activity_collection

router = APIRouter(tags=["Auth"])
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)
JWT_SECRET = os.getenv("JWT_SECRET", "local-development-secret-change-me")
ADMIN_EMAILS = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}
ONLINE_WINDOW_MINUTES = 3
CODE_TTL_MINUTES = 10
IS_DEVELOPMENT = os.getenv("APP_ENV", "development").lower() != "production"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
class UserLogin(UserRegister): pass
class RoleUpdate(BaseModel):
    role: str
class GoogleLogin(BaseModel):
    credential: str
class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
class EmailOnly(BaseModel):
    email: EmailStr
class TwoFactorVerify(BaseModel):
    email: EmailStr
    code: str
class TotpSetupVerify(BaseModel):
    code: str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
def token(email: str, role: str, scope: Optional[str] = None) -> str:
    payload = {"sub": email, "role": role, "exp": datetime.now(timezone.utc) + timedelta(hours=8)}
    if scope:
        payload["scope"] = scope
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def public_profile(u: dict) -> dict:
    return {
        "email": u["email"],
        "role": u.get("role", "user"),
        "name": u.get("name") or u["email"].split("@")[0],
        "avatar_url": u.get("avatar_url"),
    }

def send_email(to: str, subject: str, body: str) -> bool:
    # Om SMTP inte är konfigurerat (t.ex. under utveckling), skriv koden till
    # konsolen istället för att skicka den, så går flödet ändå att testa.
    host = os.getenv("SMTP_HOST")
    if not host:
        print(f"\n[E-POST SKULLE HA SKICKATS]\nTill: {to}\nÄmne: {subject}\n{body}\n"
              f"(Ingen SMTP_HOST i .env - koden visas bara här i serverkonsolen)\n")
        return False
    port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", smtp_user or "no-reply@koksboken.se")
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(sender, [to], msg.as_string())
        return True
    except Exception as exc:
        print(f"[E-POST-FEL] Kunde inte skicka till {to}: {exc}")
        return False

def as_aware(dt: Optional[datetime]) -> Optional[datetime]:
    # MongoDB (motor/pymongo) returnerar datetime utan tidszon (antas vara UTC).
    # Utan den här normaliseringen kraschar jämförelser mot tidszons-medvetna
    # "nu"-tider med "can't compare offset-naive and offset-aware datetimes".
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def issue_two_factor_code():
    code = f"{secrets.randbelow(900000) + 100000}"
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES)
    return code, code_hash, expires


def recovery_code_hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def create_recovery_codes() -> list[str]:
    return [secrets.token_hex(4).upper() for _ in range(8)]


def qr_data_url(uri: str) -> str:
    image = qrcode.make(uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

async def current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try: payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError: raise HTTPException(status_code=401, detail="Invalid or expired token.")
    if payload.get("scope"):
        raise HTTPException(status_code=403, detail="Slutför 2FA-installationen för att fortsätta.")
    user = await users_collection.find_one({"email": payload.get("sub")})
    if not user: raise HTTPException(status_code=401, detail="User not found.")
    return user


async def two_factor_setup_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Ogiltig eller utgången installationslänk.")
    if payload.get("scope") not in {None, "2fa_setup"}:
        raise HTTPException(status_code=403, detail="Otillräcklig behörighet.")
    user = await users_collection.find_one({"email": payload.get("sub")})
    if not user:
        raise HTTPException(status_code=401, detail="Användaren hittades inte.")
    return user
def require_admin(user=Depends(current_user)):
    if user.get("role", "user") != "admin": raise HTTPException(status_code=403, detail="Admin access required.")
    return user

async def optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return await users_collection.find_one({"email": payload.get("sub")})

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    email = user.email.lower()
    if await users_collection.find_one({"email": email}): raise HTTPException(status_code=400, detail="Användaren finns redan.")
    role = "admin" if email in ADMIN_EMAILS else "user"
    result = await users_collection.insert_one({
        "email": email,
        "password": hash_password(user.password),
        "role": role,
        "name": email.split("@")[0],
        "avatar_url": None,
        "created_at": datetime.now(timezone.utc),
        "two_factor_required": True,
    })
    return {"message": "Konto skapat. Ställ in Authenticator för att aktivera det.", "id": str(result.inserted_id), "email": email, "role": role, "setup_token": token(email, role, "2fa_setup")}

@router.post("/login")
async def login_user(user: UserLogin):
    email = user.email.lower(); existing = await users_collection.find_one({"email": email})
    if not existing or not existing.get("password") or not verify_password(user.password, existing["password"]): raise HTTPException(status_code=401, detail="Fel e-postadress eller lösenord.")
    if existing.get("two_factor_required") and not existing.get("totp_secret"):
        raise HTTPException(status_code=403, detail="Slutför 2FA-installationen innan du kan logga in.")
    role = "admin" if email in ADMIN_EMAILS else existing.get("role", "user")
    if role != existing.get("role", "user"): await users_collection.update_one({"_id": existing["_id"]}, {"$set": {"role": role}})

    if existing.get("totp_secret"):
        return {"requires_2fa": True, "email": email, "two_factor_method": "authenticator"}

    # Lösenordet var rätt - skicka en engångskod till mejlen innan inloggningen slutförs
    code, code_hash, expires = issue_two_factor_code()
    await users_collection.update_one({"_id": existing["_id"]}, {"$set": {"two_factor_code_hash": code_hash, "two_factor_expires": expires}})
    delivered = send_email(email, "Din inloggningskod till Köksboken", f"Din engångskod är: {code}\n\nDen gäller i {CODE_TTL_MINUTES} minuter. Skriv in den för att slutföra inloggningen.")
    response = {"requires_2fa": True, "email": email, "email_delivered": delivered}
    if IS_DEVELOPMENT and not delivered:
        response["development_code"] = code
    return response

@router.post("/verify-2fa")
async def verify_two_factor(payload: TwoFactorVerify):
    email = payload.email.lower()
    existing = await users_collection.find_one({"email": email})
    if not existing:
        raise HTTPException(status_code=400, detail="Ingen väntande inloggning. Börja om.")

    entered_code = payload.code.strip().upper()
    if existing.get("totp_secret"):
        totp_valid = pyotp.TOTP(existing["totp_secret"]).verify(entered_code, valid_window=1)
        recovery_hash = recovery_code_hash(entered_code)
        recovery_codes = existing.get("recovery_code_hashes", [])
        if not totp_valid and recovery_hash not in recovery_codes:
            raise HTTPException(status_code=400, detail="Fel kod.")
        if recovery_hash in recovery_codes:
            await users_collection.update_one({"_id": existing["_id"]}, {"$pull": {"recovery_code_hashes": recovery_hash}})
    else:
        if not existing.get("two_factor_code_hash"):
            raise HTTPException(status_code=400, detail="Ingen väntande inloggning. Börja om.")
        expires = as_aware(existing.get("two_factor_expires"))
        if not expires or datetime.now(timezone.utc) > expires:
            raise HTTPException(status_code=400, detail="Koden har gått ut. Börja om.")
        if hashlib.sha256(entered_code.encode()).hexdigest() != existing["two_factor_code_hash"]:
            raise HTTPException(status_code=400, detail="Fel kod.")

    now = datetime.now(timezone.utc)
    await users_collection.update_one(
        {"_id": existing["_id"]},
        {"$set": {"last_seen": now}, "$unset": {"two_factor_code_hash": "", "two_factor_expires": ""}},
    )
    session = await activity_collection.insert_one({"email": email, "timestamp": now, "login_time": now, "logout_time": None})
    role = existing.get("role", "user")
    return {
        "access_token": token(email, role),
        "token_type": "bearer",
        "email": email,
        "role": role,
        "name": existing.get("name") or email.split("@")[0],
        "avatar_url": existing.get("avatar_url"),
        "sessionId": str(session.inserted_id),
    }


@router.post("/logout")
async def logout_session(payload: dict):
    session_id = payload.get("sessionId")
    if session_id and ObjectId.is_valid(session_id):
        now = datetime.now(timezone.utc)
        await activity_collection.update_one({"_id": ObjectId(session_id)}, {"$set": {"logout_time": now}})
    return {"ok": True}


@router.get("/2fa/status")
async def two_factor_status(user: dict = Depends(current_user)):
    return {"enabled": bool(user.get("totp_secret"))}


@router.post("/2fa/setup")
async def setup_two_factor(user: dict = Depends(two_factor_setup_user)):
    secret = pyotp.random_base32()
    uri = pyotp.TOTP(secret).provisioning_uri(name=user["email"], issuer_name="Köksboken")
    await users_collection.update_one({"_id": user["_id"]}, {"$set": {"totp_pending_secret": secret}})
    return {"qrCode": qr_data_url(uri), "manualCode": secret}


@router.post("/2fa/setup/verify")
async def verify_two_factor_setup(payload: TotpSetupVerify, user: dict = Depends(two_factor_setup_user)):
    pending_secret = user.get("totp_pending_secret")
    if not pending_secret:
        raise HTTPException(status_code=400, detail="Starta 2FA-installationen igen.")
    if not pyotp.TOTP(pending_secret).verify(payload.code.strip(), valid_window=1):
        raise HTTPException(status_code=400, detail="Fel kod. Kontrollera tiden på mobilen och försök igen.")
    recovery_codes = create_recovery_codes()
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"totp_secret": pending_secret, "recovery_code_hashes": [recovery_code_hash(code) for code in recovery_codes]}, "$unset": {"totp_pending_secret": ""}},
    )
    role = user.get("role", "user")
    return {"message": "Authenticator-app har aktiverats.", "recoveryCodes": recovery_codes, "access_token": token(user["email"], role), "email": user["email"], "role": role}

@router.post("/resend-2fa")
async def resend_two_factor(payload: EmailOnly):
    email = payload.email.lower()
    existing = await users_collection.find_one({"email": email})
    if not existing or "two_factor_expires" not in existing:
        raise HTTPException(status_code=400, detail="Ingen väntande inloggning. Börja om.")
    code, code_hash, expires = issue_two_factor_code()
    await users_collection.update_one({"_id": existing["_id"]}, {"$set": {"two_factor_code_hash": code_hash, "two_factor_expires": expires}})
    delivered = send_email(email, "Din nya inloggningskod till Köksboken", f"Din nya engångskod är: {code}\n\nDen gäller i {CODE_TTL_MINUTES} minuter.")
    response = {"message": "Ny kod skickad.", "email_delivered": delivered}
    if IS_DEVELOPMENT and not delivered:
        response["development_code"] = code
    return response

@router.post("/google")
async def google_login(login: GoogleLogin):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=503, detail="Google login is not configured.")
    try:
        from google.auth.transport import requests
        from google.oauth2 import id_token
        identity = id_token.verify_oauth2_token(login.credential, requests.Request(), client_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Google verification failed.")
    email = identity.get("email", "").lower()
    if not email or not identity.get("email_verified"):
        raise HTTPException(status_code=401, detail="Google account email is not verified.")
    role = "admin" if email in ADMIN_EMAILS else "user"
    await users_collection.update_one(
        {"email": email},
        {"$setOnInsert": {"email": email, "google_id": identity["sub"], "name": email.split("@")[0], "avatar_url": identity.get("picture"), "created_at": datetime.now(timezone.utc)}, "$set": {"role": role}},
        upsert=True,
    )
    existing = await users_collection.find_one({"email": email})
    now = datetime.now(timezone.utc)
    await users_collection.update_one({"_id": existing["_id"]}, {"$set": {"last_seen": now}})
    session = await activity_collection.insert_one({"email": email, "timestamp": now, "login_time": now, "logout_time": None})
    return {
        "access_token": token(email, role),
        "token_type": "bearer",
        "email": email,
        "role": role,
        "name": existing.get("name") or email.split("@")[0],
        "avatar_url": existing.get("avatar_url"),
        "sessionId": str(session.inserted_id),
    }

@router.post("/heartbeat")
async def heartbeat(user: dict = Depends(current_user)):
    # Anropas regelbundet av frontend medan man är inloggad, så admin kan se
    # vem som är aktiv just nu och hur aktiviteten sett ut under dagen.
    now = datetime.now(timezone.utc)
    await users_collection.update_one({"_id": user["_id"]}, {"$set": {"last_seen": now}})
    await activity_collection.insert_one({"email": user["email"], "timestamp": now})
    return {"ok": True}

@router.get("/avatar/{email}")
async def get_avatar(email: str, request: Request):
    # Öppen endpoint så att alla besökare kan se en användares profilbild
    u = await users_collection.find_one({"email": email.lower()})
    data = (u or {}).get("avatar_url") or ""
    if data.startswith("http"):
        return RedirectResponse(data)
    if not data.startswith("data:") or "," not in data:
        raise HTTPException(status_code=404, detail="Ingen profilbild.")
    header, b64 = data.split(",", 1)
    mime = header[5:].split(";")[0] or "image/jpeg"
    try:
        raw = base64.b64decode(b64)
    except Exception:
        raise HTTPException(status_code=404, detail="Ogiltig profilbild.")
    etag = '"' + hashlib.md5(raw).hexdigest() + '"'
    headers = {"ETag": etag, "Cache-Control": "no-cache"}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(content=raw, media_type=mime, headers=headers)

@router.get("/me")
async def get_me(user: dict = Depends(current_user)):
    return public_profile(user)

@router.patch("/me")
async def update_me(update: ProfileUpdate, user: dict = Depends(current_user)):
    changes = {k: v for k, v in update.model_dump().items() if v is not None}
    if "name" in changes:
        changes["name"] = changes["name"].strip()[:40]
        if not changes["name"]:
            raise HTTPException(status_code=400, detail="Namnet får inte vara tomt.")
    if len(changes.get("avatar_url", "")) > 1_500_000:
        raise HTTPException(status_code=400, detail="Profilbilden är för stor.")
    if changes:
        await users_collection.update_one({"_id": user["_id"]}, {"$set": changes})
    updated = await users_collection.find_one({"_id": user["_id"]})
    return public_profile(updated)

@router.get("/users")
async def list_users(_: dict = Depends(require_admin)):
    users = await users_collection.find({}, {"password": 0}).to_list(length=100)
    return [{"email": u["email"], "role": u.get("role", "user")} for u in users]

@router.patch("/users/{email}/role")
async def update_role(email: str, update: RoleUpdate, _: dict = Depends(require_admin)):
    if update.role not in {"user", "admin"}: raise HTTPException(status_code=400, detail="Role must be user or admin.")
    result = await users_collection.update_one({"email": email.lower()}, {"$set": {"role": update.role}})
    if not result.matched_count: raise HTTPException(status_code=404, detail="User not found.")
    return {"email": email.lower(), "role": update.role}

@router.delete("/users/{email}")
async def delete_user(email: str, admin: dict = Depends(require_admin)):
    email = email.lower()
    if email == admin["email"]:
        raise HTTPException(status_code=400, detail="Du kan inte ta bort ditt eget konto.")
    target = await users_collection.find_one({"email": email})
    if not target:
        raise HTTPException(status_code=404, detail="Användaren hittades inte.")
    if target.get("role") == "admin":
        admin_count = await users_collection.count_documents({"role": "admin"})
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Kan inte ta bort den sista administratören.")
    await users_collection.delete_one({"email": email})
    return {"message": "Kontot borttaget."}

@router.get("/admin/online")
async def online_users(_: dict = Depends(require_admin)):
    threshold = datetime.now(timezone.utc) - timedelta(minutes=ONLINE_WINDOW_MINUTES)
    users = await users_collection.find({"last_seen": {"$gte": threshold}}, {"password": 0}).sort("last_seen", -1).to_list(length=500)
    return [{
        "email": u["email"],
        "name": u.get("name") or u["email"].split("@")[0],
        "role": u.get("role", "user"),
        "lastSeen": u["last_seen"].isoformat(),
    } for u in users]


@router.get("/chat/admins-online")
async def chat_admins_online(_: dict = Depends(current_user)):
    threshold = datetime.now(timezone.utc) - timedelta(minutes=ONLINE_WINDOW_MINUTES)
    count = await users_collection.count_documents({"role": "admin", "last_seen": {"$gte": threshold}})
    return {"count": count}


@router.get("/admin/login-log")
async def login_log(_: dict = Depends(require_admin)):
    rows = await activity_collection.find({"login_time": {"$exists": True}}).sort("login_time", -1).to_list(length=100)
    result = []
    for row in rows:
        started = as_aware(row.get("login_time"))
        ended = as_aware(row.get("logout_time"))
        seconds = int(((ended or datetime.now(timezone.utc)) - started).total_seconds()) if started else 0
        result.append({"id": str(row["_id"]), "email": row.get("email", ""), "loginTime": started.isoformat() if started else "", "logoutTime": ended.isoformat() if ended else None, "durationSeconds": max(0, seconds)})
    return result

@router.get("/admin/activity-today")
async def activity_today(_: dict = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    rows = await activity_collection.find({"timestamp": {"$gte": start}}, {"email": 1, "timestamp": 1}).to_list(length=20000)
    buckets = [set() for _ in range(24)]
    for row in rows:
        buckets[row["timestamp"].hour].add(row["email"])
    counts = [len(b) for b in buckets]
    peak = max(counts) if counts else 0
    return {"hours": counts, "peak": peak, "peakHour": counts.index(peak) if peak else None, "date": start.date().isoformat()}
