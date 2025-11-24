from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime

from config.database import db, serialize_doc, serialize_list, validate_object_id
from routes.auth import get_current_user, admin_required

router = APIRouter()


# -----------------------------------------------------------------------------------------
#  UTILITAIRE — CALCUL TOTAL COMMANDE
# -----------------------------------------------------------------------------------------

async def calculate_order_total(items):
    """
    items = [{"_id": "...", "quantity": 2}, ...]
    """
    total = 0

    for item in items:
        product_id = validate_object_id(item["_id"])
        quantity = item.get("quantity", 1)

        product = await db.products.find_one({"_id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail=f"Produit introuvable : {item['_id']}")

        total += product["price"] * quantity

    return total


# -----------------------------------------------------------------------------------------
#  CREATION COMMANDE (client)
# -----------------------------------------------------------------------------------------

@router.post("/")
async def create_order(data: dict, user=Depends(get_current_user)):
    """
    data = {
        "items": [
            {"_id": "id produit", "quantity": 2},
            ...
        ]
    }
    """
    items = data.get("items", [])

    if not items or not isinstance(items, list):
        raise HTTPException(status_code=400, detail="Items invalides.")

    # Calcul total
    total = await calculate_order_total(items)

    order = {
        "user_id": user["_id"],
        "items": items,
        "total": total,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    res = await db.orders.insert_one(order)

    return {
        "message": "Commande créée.",
        "order_id": str(res.inserted_id),
        "total": total
    }


# -----------------------------------------------------------------------------------------
#  MES COMMANDES (client)
# -----------------------------------------------------------------------------------------

@router.get("/mine")
async def my_orders(user=Depends(get_current_user)):
    orders = await db.orders.find({"user_id": user["_id"]}).sort("created_at", -1).to_list(100)
    return serialize_list(orders)


# -----------------------------------------------------------------------------------------
#  TOUTES LES COMMANDES (admin)
# -----------------------------------------------------------------------------------------

@router.get("/")
async def get_all_orders(user=Depends(admin_required)):
    orders = await db.orders.find().sort("created_at", -1).to_list(200)
    return serialize_list(orders)


# -----------------------------------------------------------------------------------------
#  DETAILS COMMANDE
# -----------------------------------------------------------------------------------------

@router.get("/{order_id}")
async def get_order(order_id: str, user=Depends(get_current_user)):
    oid = validate_object_id(order_id)

    order = await db.orders.find_one({"_id": oid})

    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable.")

    # Si utilisateur normal → ne peut voir que ses commandes
    if user["role"] != "admin" and order["user_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Accès refusé.")

    return serialize_doc(order)
