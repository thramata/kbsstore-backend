# src/config/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi import HTTPException
import os

# -----------------------------------------------------------------------------------------
# MONGO CONNECTION (Motor - Async)
# -----------------------------------------------------------------------------------------

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("❌ ERREUR : MONGO_URI non défini dans les variables d'environnement.")

# Async client
client = AsyncIOMotorClient(MONGO_URI)
db = client["kbsstore"]  # Nom de la base

# -----------------------------------------------------------------------------------------
# UTILITAIRES BSON → JSON (compatible Motor)
# -----------------------------------------------------------------------------------------

def serialize_id(id):
    """Convert ObjectId en string."""
    return str(id)

def serialize_doc(doc):
    """Convertir un document MongoDB en JSON compatible."""
    if not doc:
        return None

    # Faire une copie minimale pour ne pas muter l'original
    result = dict(doc)
    # _id
    if "_id" in result:
        result["_id"] = str(result["_id"])

    # Convertir éventuellement ObjectId dans les sous-champs
    for key, value in result.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(serialize_doc(item))
                else:
                    new_list.append(item)
            result[key] = new_list

    return result

def serialize_list(docs):
    """Convertir une liste de documents en JSON."""
    return [serialize_doc(doc) for doc in docs]

# -----------------------------------------------------------------------------------------
# VERIFICATION OBJET
# -----------------------------------------------------------------------------------------
def validate_object_id(id: str):
    """Vérifie si un ID est valide sinon lève une exception propre."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalide.")
    return ObjectId(id)
