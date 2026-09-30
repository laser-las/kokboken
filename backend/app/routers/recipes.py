import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.database import recipes_collection, users_collection
from app.routers.auth import current_user, optional_user

router = APIRouter(prefix="/api/recipes", tags=["Recipes"])

DIFFICULTIES = {"Lätt", "Medel", "Svår"}


class IngredientGroup(BaseModel):
    name: str = "Ingredienser"
    items: List[str] = Field(default_factory=list)


class RecipeCreate(BaseModel):
    title: str
    category: str = "Övrigt"
    time: str = ""
    image: str = ""
    description: str = ""
    ingredient_groups: List[IngredientGroup] = Field(default_factory=lambda: [IngredientGroup()])
    steps: List[str] = Field(default_factory=list)
    is_public: bool = True
    difficulty: str = "Medel"
    portions: int = 4


def slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = slug.replace("å", "a").replace("ä", "a").replace("ö", "o")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "recept"


async def author_names(docs: list) -> dict:
    emails = list({d.get("created_by") for d in docs if d.get("created_by")})
    if not emails:
        return {}
    users = await users_collection.find({"email": {"$in": emails}}, {"email": 1, "name": 1}).to_list(length=1000)
    return {u["email"]: (u.get("name") or u["email"].split("@")[0]) for u in users}


def serialize(doc: dict, names: Optional[dict] = None) -> dict:
    owner = doc.get("created_by", "") or ""
    groups = doc.get("ingredient_groups")
    if not groups:
        # Bakåtkompatibilitet: recept skapade innan grupperade ingredienser fanns
        legacy = doc.get("ingredients", [])
        groups = [{"name": "Ingredienser", "items": legacy}]
    return {
        "slug": doc["slug"],
        "title": doc["title"],
        "category": doc.get("category", ""),
        "time": doc.get("time", ""),
        "image": doc.get("image", ""),
        "description": doc.get("description", ""),
        "ingredientGroups": groups,
        "steps": doc.get("steps", []),
        "createdBy": owner,
        "authorName": (names or {}).get(owner) or (owner.split("@")[0] if owner else ""),
        "isPublic": doc.get("is_public", True),
        "difficulty": doc.get("difficulty") or "Medel",
        "portions": doc.get("portions") or 4,
        "createdAt": doc.get("created_at"),
        "updatedAt": doc.get("updated_at") or doc.get("created_at"),
    }


def can_view(doc: dict, user: Optional[dict]) -> bool:
    if doc.get("is_public", True) is not False:
        return True
    if not user:
        return False
    return user.get("email") == doc.get("created_by") or user.get("role") == "admin"


def clean_payload(recipe: RecipeCreate) -> dict:
    data = recipe.model_dump()
    if data["difficulty"] not in DIFFICULTIES:
        data["difficulty"] = "Medel"
    data["portions"] = max(1, min(50, data["portions"] or 4))
    groups = []
    for g in data["ingredient_groups"]:
        items = [i.strip() for i in g["items"] if i.strip()]
        if items:
            groups.append({"name": (g["name"] or "Ingredienser").strip()[:40] or "Ingredienser", "items": items})
    data["ingredient_groups"] = groups or [{"name": "Ingredienser", "items": []}]
    data["steps"] = [s.strip() for s in data["steps"] if s.strip()]
    return data


@router.get("/")
async def get_recipes(user: Optional[dict] = Depends(optional_user)):
    # Publikt flöde: visar bara recept som är markerade som publika.
    # Filtreras här i Python (inte i Mongo-frågan) så vi garanterat aldrig
    # missar ett privat recept oavsett exakt hur fältet råkar vara lagrat.
    docs = await recipes_collection.find({}).sort("_id", -1).to_list(length=500)
    visible_docs = docs if user and user.get("role") == "admin" else [d for d in docs if d.get("is_public", True) is not False]
    names = await author_names(visible_docs)
    return [serialize(d, names) for d in visible_docs]


@router.get("/mine")
async def get_my_recipes(user: dict = Depends(current_user)):
    # Egna recept, både publika och privata
    docs = await recipes_collection.find({"created_by": user["email"]}).sort("_id", -1).to_list(length=500)
    names = await author_names(docs)
    return [serialize(d, names) for d in docs]


@router.get("/{slug}")
async def get_recipe(slug: str, user: Optional[dict] = Depends(optional_user)):
    doc = await recipes_collection.find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Receptet hittades inte.")
    if not can_view(doc, user):
        raise HTTPException(status_code=403, detail="Det här receptet är privat.")
    return serialize(doc, await author_names([doc]))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe: RecipeCreate, user: dict = Depends(current_user)):
    base_slug = slugify(recipe.title)
    slug = base_slug
    counter = 2
    while await recipes_collection.find_one({"slug": slug}):
        slug = f"{base_slug}-{counter}"
        counter += 1

    doc = clean_payload(recipe)
    doc["slug"] = slug
    doc["created_by"] = user["email"]
    doc["created_at"] = datetime.now(timezone.utc)
    await recipes_collection.insert_one(doc)
    return serialize(doc, {user["email"]: user.get("name") or user["email"].split("@")[0]})


@router.put("/{slug}")
async def update_recipe(slug: str, recipe: RecipeCreate, user: dict = Depends(current_user)):
    existing = await recipes_collection.find_one({"slug": slug})
    if not existing:
        raise HTTPException(status_code=404, detail="Receptet hittades inte.")

    is_owner = existing.get("created_by") == user["email"]
    if not is_owner and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Du får bara redigera dina egna recept.")

    data = clean_payload(recipe)
    data["updated_at"] = datetime.now(timezone.utc)
    await recipes_collection.update_one({"slug": slug}, {"$set": data})
    updated = await recipes_collection.find_one({"slug": slug})
    return serialize(updated, await author_names([updated]))


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
