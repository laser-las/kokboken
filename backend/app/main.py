from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, recipes, categories, contact
from backend.app.database import categories_collection

app = FastAPI(title="Köksboken API")

# Tillåt Vue frontend (lägg till port 5174)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Koppla in rutter
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(recipes.router)
app.include_router(categories.router)
app.include_router(contact.router)

DEFAULT_CATEGORIES = ["Frukost", "Lunch", "Middag", "Fika", "Sallad"]

@app.on_event("startup")
async def seed_default_categories():
    # Lägger bara till standardkategorierna om databasen är helt tom på
    # kategorier - rör aldrig befintliga/borttagna kategorier.
    existing_count = await categories_collection.count_documents({})
    if existing_count == 0:
        await categories_collection.insert_many([{"name": name} for name in DEFAULT_CATEGORIES])

@app.get("/")
def read_root():
    return {"message": "Välkommen till Köksboken API!"}