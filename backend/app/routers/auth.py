import bcrypt
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.database import users_collection

router = APIRouter(tags=["Auth"])

class UserRegister(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    # Omvandla lösenordet till bytes och hasha det med bcrypt
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verifiera lösenord vid inloggning
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    # 1. Kontrollera om e-postadressen redan finns i databasen
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="En användare med denna e-postadress finns redan."
        )

    # 2. Hasha lösenordet och skapa användarobjektet
    hashed_pwd = hash_password(user.password)
    user_doc = {
        "email": user.email,
        "password": hashed_pwd
    }

    # 3. Spara i MongoDB
    result = await users_collection.insert_one(user_doc)

    return {
        "message": "Konto skapat framgångsrikt!",
        "id": str(result.inserted_id),
        "email": user.email
    }