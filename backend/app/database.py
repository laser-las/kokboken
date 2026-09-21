import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Läs in miljövariabler från .env-filen
load_dotenv()

# Hämta MongoDB URI från .env (eller använd standard-URL för lokal MongoDB)
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

# Skapa databasanslutning
client = AsyncIOMotorClient(MONGO_URI)

# Välj databasnamn (byt 'kokboken' om du vill ha ett annat namn i MongoDB)
db = client.kokboken