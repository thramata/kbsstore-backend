from fastapi import APIRouter, HTTPException, Depends
from config.database import db, serialize_doc, serialize_list
from routes.auth import admin_required
from bson import ObjectId

router = APIRouter()


# -----------------------------------------------------------------------------------------
# 📊 STATISTIQUES ADMIN — Dashboard
# -----------------------------------------------------------------------------------------

@router.get("/stats")
async def admin_stats(user=Depends(admin_required)):
    """
    Dashboard :
    - Total utilisateurs
    - Total produits
    - Total commandes
    - Chiffre d’affaires total
    """

    users = await db.users.count_documents({})
    products = await db.products.count_documents({})
    orders = await db.orders.count_documents({})

    # Total des revenus via agrégation Mongo
    revenue_pipeline = [
        {"$match": {"status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]

    revenue_result = await db.orders.aggregate(revenue_pipeline).to_list(length=1)
    revenue = revenue_result[0]["total"] if revenue_result else 0

    return {
        "users": users,
        "products": products,
        "orders": orders,
        "revenue": revenue
    }


# -----------------------------------------------------------------------------------------
# 👥 LISTE UTILISATEURS — Admin
# -----------------------------------------------------------------------------------------

@router.get("/users")
async def admin_get_users(user=Depends(admin_required)):
    """
    Retourne tous les utilisateurs (SANS mot de passe).
    """
    users = await db.users.find({}, {"password": 0}).to_list(1000)
    return serialize_list(users)


# -----------------------------------------------------------------------------------------
# 📉 PRODUITS STOCK FAIBLE (≤ 3)
# -----------------------------------------------------------------------------------------

@router.get("/low-stock")
async def low_stock(user=Depends(admin_required)):
    """
    Retourne les produits dont le stock est faible.
    """
    products = await db.products.find({"stock": {"$lte": 3}}).to_list(200)
    return serialize_list(products)


# -----------------------------------------------------------------------------------------
# 📦 COMMANDES PAR JOUR (pour graph)
# -----------------------------------------------------------------------------------------

@router.get("/orders-by-day")
async def orders_by_day(user=Depends(admin_required)):
    """
    Agrégation MongoDB :
    Renvoie le CA par date (yyyy-mm-dd)
    """

    pipeline = [
        {"$match": {"status": "paid"}},
        {
            "$group": {
                "_id": {"$substr": ["$created_at", 0, 10]},
                "total": {"$sum": "$total"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]

    data = await db.orders.aggregate(pipeline).to_list(length=200)
    result = [{"date": d["_id"], "total": d["total"], "count": d["count"]} for d in data]
    return result
