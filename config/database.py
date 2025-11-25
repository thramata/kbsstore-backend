# config/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi import HTTPException
import os

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("❌ ERREUR : MONGO_URI non défini dans les variables d'environnement.")

client = AsyncIOMotorClient(MONGO_URI)
db = client["kbsstore"]

def serialize_id(id):
    return str(id)

def serialize_doc(doc):
    if not doc:
        return None
    result = dict(doc)
    if "_id" in result:
        result["_id"] = str(result["_id"])
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
    return [serialize_doc(doc) for doc in docs]

def validate_object_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalide.")
    return ObjectId(id)
