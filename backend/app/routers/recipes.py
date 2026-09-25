import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.database import recipes_collection
from app.routers.auth import current_user, optional_user

router = APIRouter(prefix="/api/recipes", tags=["Recipes"])


class RecipeCreate(BaseModel):
    title: str
    category: str = "Övrigt"
    time: str = ""
    image: str = ""
    description: str = ""
    ingredients: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    is_public: bool = True


def slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = slug.replace("å", "a").replace("ä", "a").replace("ö", "o")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "recept"


def serialize(doc: dict) -> dict:
    return {
        "slug": doc["slug"],
        "title": doc["title"],
        "category": doc.get("category", ""),
        "time": doc.get("time", ""),
        "image": doc.get("image", ""),
        "description": doc.get("description", ""),
        "ingredients": doc.get("ingredients", []),
        "steps": doc.get("steps", []),
        "createdBy": doc.get("created_by", ""),
        "isPublic": doc.get("is_public", True),
    }


def can_view(doc: dict, user: Optional[dict]) -> bool:
    if doc.get("is_public", True) is not False:
        return True
    if not user:
        return False
    return user.get("email") == doc.get("created_by") or user.get("role") == "admin"


@router.get("/")
async def get_recipes():
    # Publikt flöde: visar bara recept som är markerade som publika.
    # Filtreras här i Python (inte i Mongo-frågan) så vi garanterat aldrig
    # missar ett privat recept oavsett exakt hur fältet råkar vara lagrat.
    docs = await recipes_collection.find({}).sort("_id", -1).to_list(length=500)
    public_docs = [d for d in docs if d.get("is_public", True) is not False]
    return [serialize(d) for d in public_docs]


@router.get("/mine")
async def get_my_recipes(user: dict = Depends(current_user)):
    # Egna recept, både publika och privata
    docs = await recipes_collection.find({"created_by": user["email"]}).sort("_id", -1).to_list(length=500)
    return [serialize(d) for d in docs]


@router.get("/{slug}")
async def get_recipe(slug: str, user: Optional[dict] = Depends(optional_user)):
    doc = await recipes_collection.find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Receptet hittades inte.")
    if not can_view(doc, user):
        raise HTTPException(status_code=403, detail="Det här receptet är privat.")
    return serialize(doc)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe: RecipeCreate, user: dict = Depends(current_user)):
    base_slug = slugify(recipe.title)
    slug = base_slug
    counter = 2
    while await recipes_collection.find_one({"slug": slug}):
        slug = f"{base_slug}-{counter}"
        counter += 1

    doc = recipe.model_dump()
    doc["slug"] = slug
    doc["created_by"] = user["email"]
    doc["created_at"] = datetime.now(timezone.utc)
    await recipes_collection.insert_one(doc)
    return serialize(doc)


@router.put("/{slug}")
async def update_recipe(slug: str, recipe: RecipeCreate, user: dict = Depends(current_user)):
    existing = await recipes_collection.find_one({"slug": slug})
    if not existing:
        raise HTTPException(status_code=404, detail="Receptet hittades inte.")

    is_owner = existing.get("created_by") == user["email"]
    if not is_owner and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Du får bara redigera dina egna recept.")

    await recipes_collection.update_one({"slug": slug}, {"$set": recipe.model_dump()})
    updated = await recipes_collection.find_one({"slug": slug})
    return serialize(updated)


@router.delete("/{slug}")
async def delete_recipe(slug: str, user: dict = Depends(current_user)):
    existing = await recipes_collection.find_one({"slug": slug})
    if not existing:
        raise HTTPException(status_code=404, detail="Receptet hittades inte.")

    is_owner = existing.get("created_by") == user["email"]
    if not is_owner and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Du får bara ta bort dina egna recept (adminroll kan ta bort alla).")

    await recipes_collection.delete_one({"slug": slug})
    return {"message": "Recept borttaget."}