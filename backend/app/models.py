from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class RecipeModel(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    created_by: Optional[str] = None