from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from bson import ObjectId
from config.database import db, serialize_doc, serialize_list, validate_object_id
from routes.auth import admin_required
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# -----------------------------------------------------------------------------------------
#  UTILITAIRE – SAUVEGARDE IMAGE
# -----------------------------------------------------------------------------------------

def save_image(file: UploadFile):
    """Enregistre l’image uploadée dans /uploads."""
    if not file:
        return None

    filename = f"{ObjectId()}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename


# -----------------------------------------------------------------------------------------
# GET ALL PRODUCTS
# -----------------------------------------------------------------------------------------

@router.get("/")
async def get_products():
    products = await db.products.find().to_list(500)
    return serialize_list(products)


# -----------------------------------------------------------------------------------------
# GET PRODUCT BY ID
# -----------------------------------------------------------------------------------------

@router.get("/{product_id}")
async def get_product(product_id: str):
    oid = validate_object_id(product_id)
    product = await db.products.find_one({"_id": oid})

    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable.")

    return serialize_doc(product)


# -----------------------------------------------------------------------------------------
# CREATE PRODUCT (ADMIN)
# -----------------------------------------------------------------------------------------

@router.post("/")
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    description: str = Form(""),
    image: UploadFile = File(None),
    user=Depends(admin_required),
):
    # Validation
    if price < 0:
        raise HTTPException(status_code=400, detail="Le prix doit être positif.")

    if stock < 0:
        raise HTTPException(status_code=400, detail="Le stock doit être positif.")

    filename = save_image(image) if image else None

    new_product = {
        "name": name,
        "price": price,
        "stock": stock,
        "description": description,
        "image": filename,
        "created_at": None,
    }

    res = await db.products.insert_one(new_product)

    return {
        "message": "Produit créé avec succès.",
        "product_id": str(res.inserted_id),
    }


# -----------------------------------------------------------------------------------------
# UPDATE PRODUCT (ADMIN)
# -----------------------------------------------------------------------------------------

@router.put("/{product_id}")
async def update_product(
    product_id: str,
    name: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    description: str = Form(""),
    image: UploadFile = File(None),
    user=Depends(admin_required),
):
    oid = validate_object_id(product_id)

    product = await db.products.find_one({"_id": oid})
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable.")

    if price < 0 or stock < 0:
        raise HTTPException(status_code=400, detail="Valeurs invalides.")

    update_data = {
        "name": name,
        "price": price,
        "stock": stock,
        "description": description,
    }

    # Nouvelle image ?
    if image:
        filename = save_image(image)
        update_data["image"] = filename

    await db.products.update_one(
        {"_id": oid},
        {"$set": update_data}
    )

    return {"message": "Produit mis à jour avec succès."}


# -----------------------------------------------------------------------------------------
# DELETE PRODUCT (ADMIN)
# -----------------------------------------------------------------------------------------

@router.delete("/{product_id}")
async def delete_product(product_id: str, user=Depends(admin_required)):
    oid = validate_object_id(product_id)

    product = await db.products.find_one({"_id": oid})
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable.")

    # Supprimer image du dossier uploads
    if product.get("image"):
        img_path = os.path.join(UPLOAD_DIR, product["image"])
        if os.path.exists(img_path):
            os.remove(img_path)

    await db.products.delete_one({"_id": oid})

    return {"message": "Produit supprimé avec succès."}
