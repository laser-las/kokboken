import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Ladda variabler från .env-filen
load_dotenv()

# Hämta MONGODB_URI från .env
MONGO_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URL)
db = client.koksboken

users_collection = db.get_collection("users")
recipes_collection = db.get_collection("recipes")
categories_collection = db.get_collection("categories")
contact_collection = db.get_collection("contact_messages")