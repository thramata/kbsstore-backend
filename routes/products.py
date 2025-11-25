from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from config.database import db, serialize_doc
from fastapi import status
from datetime import datetime
from bson import ObjectId
from routes.auth import get_current_user, admin_required
import os
from typing import List

router = APIRouter(prefix="/products")

@router.get("", status_code=200)
async def get_products():
    cursor = db.products.find({})
    products = await cursor.to_list(length=1000)
    return [serialize_doc(p) for p in products]

@router.get("/{product_id}")
async def get_product(product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID invalide")
    prod = await db.products.find_one({"_id": ObjectId(product_id)})
    if not prod:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return serialize_doc(prod)

@router.post("", dependencies=[Depends(admin_required)])
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(None)
):
    image_url = None
    if image:
        # Exemple : sauvegarde locale (temp) — pour production, utilise S3/Cloudinary
        save_path = f"/tmp/{image.filename}"
        with open(save_path, "wb") as f:
            f.write(await image.read())
        # ici on peut uploader sur un CDN et récupérer URL
        image_url = f"/static/{image.filename}"

    new_prod = {
        "name": name,
        "price": price,
        "image_url": image_url,
        "created_at": datetime.utcnow()
    }
    res = await db.products.insert_one(new_prod)
    prod = await db.products.find_one({"_id": res.inserted_id})
    return serialize_doc(prod)

@router.put("/{product_id}", dependencies=[Depends(admin_required)])
async def update_product(product_id: str, payload: dict):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID invalide")
    await db.products.update_one({"_id": ObjectId(product_id)}, {"$set": payload})
    prod = await db.products.find_one({"_id": ObjectId(product_id)})
    return serialize_doc(prod)

@router.delete("/{product_id}", dependencies=[Depends(admin_required)])
async def delete_product(product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID invalide")
    await db.products.delete_one({"_id": ObjectId(product_id)})
    return {"message": "Produit supprimé."}
