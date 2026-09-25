from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.app.database import categories_collection
from app.routers.auth import require_admin

router = APIRouter(prefix="/api/categories", tags=["Categories"])


class CategoryCreate(BaseModel):
    name: str


@router.get("/")
async def list_categories():
    docs = await categories_collection.find({}).sort("name", 1).to_list(length=200)
    return [d["name"] for d in docs]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, _: dict = Depends(require_admin)):
    name = category.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Kategorinamn krävs.")
    if await categories_collection.find_one({"name": name}):
        raise HTTPException(status_code=400, detail="Kategorin finns redan.")
    await categories_collection.insert_one({"name": name})
    return {"name": name}


@router.delete("/{name}")
async def delete_category(name: str, _: dict = Depends(require_admin)):
    result = await categories_collection.delete_one({"name": name})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="Kategorin hittades inte.")
    return {"message": "Kategori borttagen."}