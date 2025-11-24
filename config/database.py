from pymongo import MongoClient
from bson import ObjectId
from fastapi import HTTPException
import os

# -----------------------------------------------------------------------------------------
# MONGO CONNECTION
# -----------------------------------------------------------------------------------------

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ ERREUR : MONGO_URI non défini dans les variables d'environnement.")

client = MongoClient(MONGO_URI)
db = client["kbsstore"]  # Nom de la base


# -----------------------------------------------------------------------------------------
# UTILITAIRES BSON → JSON
# -----------------------------------------------------------------------------------------

def serialize_id(id):
    """Convert ObjectId en string."""
    return str(id)


def serialize_doc(doc):
    """Convertir un document MongoDB en JSON compatible."""
    if not doc:
        return None

    doc["_id"] = str(doc["_id"])

    # Convertir les clés enfants
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        if isinstance(value, list):
            doc[key] = [serialize_doc(item) if isinstance(item, dict) else item for item in value]

    return doc


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
