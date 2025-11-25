from fastapi import APIRouter, HTTPException, Depends
from config.database import db, serialize_doc
from bson import ObjectId
from datetime import datetime
from routes.auth import get_current_user
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/orders")

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class OrderSchema(BaseModel):
    user_id: str
    items: List[OrderItem]

@router.post("")
async def create_order(data: OrderSchema, user=Depends(get_current_user)):
    # validate and compute total
    items_stored = []
    total = 0
    for it in data.items:
        if not ObjectId.is_valid(it.product_id):
            raise HTTPException(status_code=400, detail="ID produit invalide")
        product = await db.products.find_one({"_id": ObjectId(it.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Produit introuvable")
        amount = product.get("price", 0) * it.quantity
        total += amount
        items_stored.append({"product_id": ObjectId(it.product_id), "quantity": it.quantity, "price": product.get("price", 0)})

    order = {
        "user_id": ObjectId(data.user_id),
        "items": items_stored,
        "total": total,
        "created_at": datetime.utcnow()
    }
    res = await db.orders.insert_one(order)
    o = await db.orders.find_one({"_id": res.inserted_id})
    return serialize_doc(o)

@router.get("/user/{user_id}")
async def get_orders_by_user(user_id: str, user=Depends(get_current_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID invalide")
    cursor = db.orders.find({"user_id": ObjectId(user_id)})
    orders = await cursor.to_list(length=1000)
    return [serialize_doc(o) for o in orders]

@router.get("")
async def get_all_orders(user=Depends(get_current_user)):
    # admin only? add admin_required if needed
    cursor = db.orders.find({})
    orders = await cursor.to_list(length=1000)
    return [serialize_doc(o) for o in orders]
