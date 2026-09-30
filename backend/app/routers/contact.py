from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr

from app.database import contact_collection
from app.routers.auth import optional_user, require_admin

router = APIRouter(prefix="/api/contact", tags=["Contact"])

# Enkel rate limit i minnet: en förfrågan per IP var 60:e sekund.
# (Räcker för att stoppa enkla spam-skript. Vid omstart av servern nollställs den.)
_last_submission: dict[str, float] = {}
RATE_LIMIT_SECONDS = 60


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
    # Dolt fält i formuläret (via CSS) - ska ALLTID vara tomt för en riktig
    # människa. Spam-robotar fyller ofta i alla fält automatiskt.
    website: str = ""


@router.post("/", status_code=status.HTTP_201_CREATED)
async def send_contact_message(payload: ContactMessage, request: Request, user: dict | None = Depends(optional_user)):
    if payload.website:
        # Honeypot-fältet var ifyllt -> troligen en spam-robot.
        # Låtsas att det gick bra så att roboten inte försöker igen med annan data.
        return {"message": "Tack för ditt meddelande!"}

    name = payload.name.strip()
    message = payload.message.strip()
    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Ange ditt namn.")
    if len(message) < 10:
        raise HTTPException(status_code=400, detail="Meddelandet är för kort.")
    if len(message) > 3000:
        raise HTTPException(status_code=400, detail="Meddelandet är för långt.")

    client_ip = request.client.host if request.client else "unknown"
    now = datetime.now(timezone.utc).timestamp()
    last = _last_submission.get(client_ip)
    if last and now - last < RATE_LIMIT_SECONDS:
        raise HTTPException(status_code=429, detail="Vänta en liten stund innan du skickar igen.")
    _last_submission[client_ip] = now

    await contact_collection.insert_one({
        "name": name,
        "email": user["email"] if user else payload.email,
        "user_email": user["email"] if user else None,
        "message": message,
        "created_at": datetime.now(timezone.utc),
        "ip": client_ip,
    })
    return {"message": "Tack för ditt meddelande! Vi återkommer så snart vi kan."}


@router.get("/admin")
async def list_contact_messages(_: dict = Depends(require_admin)):
    messages = await contact_collection.find({}).sort("created_at", -1).to_list(length=300)
    return [{
        "id": str(item["_id"]), "name": item["name"], "email": item["email"],
        "message": item["message"], "createdAt": item["created_at"],
    } for item in messages]
