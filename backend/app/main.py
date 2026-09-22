from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, recipes

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

@app.get("/")
def read_root():
    return {"message": "Välkommen till Köksboken API!"}