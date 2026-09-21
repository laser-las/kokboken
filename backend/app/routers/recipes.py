from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/recipes", tags=["Recipes"])

# Pydantic-modell för recept
class RecipeCreate(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str

@router.get("/")
async def get_recipes():
    # Hämta alla recept från databasen
    return {"message": "Här kommer alla recept att visas"}

@router.post("/")
async def create_recipe(recipe: RecipeCreate):
    # Skapa ett nytt recept
    return {"message": "Recept skapat", "recipe": recipe}