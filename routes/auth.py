from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from datetime import datetime, timedelta
from config.database import db, serialize_doc
from passlib.hash import argon2
from bson import ObjectId
import os

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise Exception("❌ ERREUR : JWT_SECRET non défini dans les variables d'environnement.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ChangePwdSchema(BaseModel):
    old_password: str
    new_password: str

def create_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur inexistant")
        return serialize_doc(user)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expiré ou invalide")

def admin_required(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux admins")
    return user

@router.post("/register")
async def register(data: RegisterSchema):
    exists = await db.users.find_one({"email": data.email})
    if exists:
        raise HTTPException(status_code=400, detail="Cet email existe déjà.")
    hashed_pwd = argon2.hash(data.password)
    new_user = {
        "name": data.name,
        "email": data.email,
        "password": hashed_pwd,
        "role": "user",
        "created_at": datetime.utcnow()
    }
    res = await db.users.insert_one(new_user)
    token = create_token({"user_id": str(res.inserted_id), "email": data.email})
    return {
        "message": "Compte créé avec succès.",
        "token": token,
        "user": {
            "_id": str(res.inserted_id),
            "name": data.name,
            "email": data.email,
            "role": "user"
        }
    }

@router.post("/login")
async def login(data: LoginSchema):
    user = await db.users.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect.")
    if not argon2.verify(data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect.")
    token = create_token({"user_id": str(user["_id"]), "email": user["email"]})
    return {
        "message": "Connexion réussie.",
        "token": token,
        "user": serialize_doc(user)
    }

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user

@router.post("/change-password")
async def change_password(data: ChangePwdSchema, user=Depends(get_current_user)):
    # user is serialized, but we need the raw user document to access stored password
    raw_user = await db.users.find_one({"_id": ObjectId(user["_id"])})
    if not raw_user or not argon2.verify(data.old_password, raw_user["password"]):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect.")
    hashed_pwd = argon2.hash(data.new_password)
    await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"password": hashed_pwd}})
    return {"message": "Mot de passe modifié avec succès."}
