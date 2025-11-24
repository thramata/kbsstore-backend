from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from datetime import datetime
from config.database import db
from schemas.order import OrderCreate, OrderOut, OrderItem
from utils import verify_token

router = APIRouter(prefix="/orders", tags=["Orders"])


# -----------------------------------------------------------------------------------------
# FONCTION : convertir ObjectId → str + nettoyer l'objet Mongo
# -----------------------------------------------------------------------------------------
def serialize_order(order):
    return {
        "id": str(order["_id"]),
        "user_id": order["user_id"],
        "items": order["items"],
        "total": order["total"],
        "status": order["status"],
        "created_at": order.get("created_at"),
        "updated_at": order.get("updated_at"),
    }


# -----------------------------------------------------------------------------------------
# ROUTE : CRÉER UNE COMMANDE (POST /orders)
# -----------------------------------------------------------------------------------------
@router.post("/", response_model=OrderOut)
def create_order(order_data: OrderCreate, user=Depends(verify_token)):

    # Calcul du total
    total_price = 0

    for item in order_data.items:
        product = db.products.find_one({"_id": ObjectId(item._id)})
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Produit introuvable : {item._id}"
            )

        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuffisant pour {product['name']}"
            )

        total_price += product["price"] * item.quantity

        # Mise à jour du stock
        db.products.update_one(
            {"_id": ObjectId(item._id)},
            {"$inc": {"stock": -item.quantity}}
        )

    # Création de la commande
    new_order = {
        "user_id": user["_id"],
        "items": [item.dict() for item in order_data.items],
        "total": total_price,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = db.orders.insert_one(new_order)
    saved_order = db.orders.find_one({"_id": result.inserted_id})

    return serialize_order(saved_order)


# -----------------------------------------------------------------------------------------
# ROUTE : OBTENIR MES COMMANDES (GET /orders/mine)
# -----------------------------------------------------------------------------------------
@router.get("/mine", response_model=List[OrderOut])
def my_orders(user=Depends(verify_token)):
    orders = db.orders.find({"user_id": user["_id"]})
    return [serialize_order(o) for o in orders]


# -----------------------------------------------------------------------------------------
# ROUTE : OBTENIR TOUTES LES COMMANDES (ADMIN)
# -----------------------------------------------------------------------------------------
@router.get("/", response_model=List[OrderOut])
def get_all_orders(user=Depends(verify_token)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")

    orders = db.orders.find().sort("created_at", -1)

    return [serialize_order(o) for o in orders]


# -----------------------------------------------------------------------------------------
# ROUTE : OBTENIR UNE COMMANDE PAR ID
# -----------------------------------------------------------------------------------------
@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, user=Depends(verify_token)):
    order = db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    if (order["user_id"] != user["_id"]) and (user["role"] != "admin"):
        raise HTTPException(status_code=403, detail="Accès refusé")

    return serialize_order(order)
