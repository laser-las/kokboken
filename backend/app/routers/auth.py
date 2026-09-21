from fastapi import APIRouter, HTTPException
from app.models import UserRegister, UserLogin
from app.database import db
from passlib.hash import pbkdf2_sha256

router = APIRouter()

@router.post("/register")
async def register(user: UserRegister):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="E-post finns redan")

    hashed_password = pbkdf2_sha256.hash(user.password)
    new_user = {"email": user.email, "password": hashed_password}
    
    result = await db.users.insert_one(new_user)
    return {"message": "Användare skapad", "id": str(result.inserted_id)}