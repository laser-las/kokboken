from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, recipes

app = FastAPI()

# Tillåt Vue frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Koppla in rutter
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["Recipes"])

@app.get("/")
def read_root():
    return {"message": "Välkommen till Köksboken API!"}