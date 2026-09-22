import os
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from app.database import users_collection

router = APIRouter(tags=["Auth"])
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "local-development-secret-change-me")
ADMIN_EMAILS = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}

class UserRegister(BaseModel):
    email: EmailStr
    password: str
class UserLogin(UserRegister): pass
class RoleUpdate(BaseModel):
    role: str
class GoogleLogin(BaseModel):
    credential: str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
def token(email: str, role: str) -> str:
    return jwt.encode({"sub": email, "role": role, "exp": datetime.now(timezone.utc) + timedelta(hours=8)}, JWT_SECRET, algorithm="HS256")

async def current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try: payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError: raise HTTPException(status_code=401, detail="Invalid or expired token.")
    user = await users_collection.find_one({"email": payload.get("sub")})
    if not user: raise HTTPException(status_code=401, detail="User not found.")
    return user
def require_admin(user=Depends(current_user)):
    if user.get("role", "user") != "admin": raise HTTPException(status_code=403, detail="Admin access required.")
    return user

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    email = user.email.lower()
    if await users_collection.find_one({"email": email}): raise HTTPException(status_code=400, detail="Användaren finns redan.")
    role = "admin" if email in ADMIN_EMAILS else "user"
    result = await users_collection.insert_one({"email": email, "password": hash_password(user.password), "role": role, "created_at": datetime.now(timezone.utc)})
    return {"message": "Konto skapat.", "id": str(result.inserted_id), "email": email, "role": role}

@router.post("/login")
async def login_user(user: UserLogin):
    email = user.email.lower(); existing = await users_collection.find_one({"email": email})
    if not existing or not existing.get("password") or not verify_password(user.password, existing["password"]): raise HTTPException(status_code=401, detail="Fel e-postadress eller lösenord.")
    role = "admin" if email in ADMIN_EMAILS else existing.get("role", "user")
    if role != existing.get("role", "user"): await users_collection.update_one({"_id": existing["_id"]}, {"$set": {"role": role}})
    return {"access_token": token(email, role), "token_type": "bearer", "email": email, "role": role}

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
        {"$setOnInsert": {"email": email, "google_id": identity["sub"], "created_at": datetime.now(timezone.utc)}, "$set": {"role": role}},
        upsert=True,
    )
    return {"access_token": token(email, role), "token_type": "bearer", "email": email, "role": role}

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
