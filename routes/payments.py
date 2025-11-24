from fastapi import APIRouter, HTTPException, Depends, Request
from config.database import db, serialize_doc, validate_object_id
from routes.auth import get_current_user
from bson import ObjectId
import requests
import hashlib
import hmac
import os

router = APIRouter()

PAYTECH_API_KEY = os.getenv("PAYTECH_API_KEY")
PAYTECH_SECRET_KEY = os.getenv("PAYTECH_SECRET_KEY")  # pour vérifier la signature
PAYTECH_BASE_URL = os.getenv("PAYTECH_API_URL", "https://paytech.sn/api/payment/request-initiate")

FRONTEND_SUCCESS = "https://kbsstore.vercel.app/success"
FRONTEND_CANCEL = "https://kbsstore.vercel.app/cancel"


# -----------------------------------------------------------------------------------------
# CRÉER LA SESSION DE PAIEMENT
# -----------------------------------------------------------------------------------------

@router.post("/create")
async def create_payment_session(data: dict, user=Depends(get_current_user)):
    """
    data = { "order_id": "...", "amount": 45000 }
    """
    order_id = data.get("order_id")
    amount = data.get("amount")

    if not order_id or not amount:
        raise HTTPException(status_code=400, detail="order_id ou amount manquant.")

    oid = validate_object_id(order_id)

    order = await db.orders.find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable.")

    # Vérifier que c'est la commande de l'utilisateur
    if order["user_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Cette commande ne vous appartient pas.")

    # Construire requête PayTech
    payload = {
        "item_name": f"KBS Store - Commande {order_id}",
        "item_price": amount,
        "currency": "XOF",
        "ref_command": str(order_id),
        "env": "test",           # PROD → "prod"
        "success_url": FRONTEND_SUCCESS,
        "cancel_url": FRONTEND_CANCEL,
        "ipn_url": "https://kbsstore-backend.onrender.com/payments/webhook",
        "api_key": PAYTECH_API_KEY
    }

    try:
        response = requests.post(PAYTECH_BASE_URL, data=payload)
        response_data = response.json()

        if not response_data.get("success"):
            raise HTTPException(status_code=400, detail="PayTech a rejeté la requête.")

        # URL de redirection PayTech
        payment_url = response_data["redirect_url"]

        return {
            "payment_url": payment_url,
            "message": "Redirection vers PayTech…"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur PayTech : {str(e)}")


# -----------------------------------------------------------------------------------------
# WEBHOOK PAYTECH (IPN)
# -----------------------------------------------------------------------------------------

@router.post("/webhook")
async def paytech_webhook(request: Request):
    """
    PayTech envoie :
    - ref_command
    - amount
    - status : completed / failed / canceled
    - signature HMAC-SHA256
    """
    data = await request.json()

    required_fields = ["ref_command", "amount", "status", "signature"]
    for f in required_fields:
        if f not in data:
            raise HTTPException(status_code=400, detail="Webhook invalide.")

    order_id = data["ref_command"]
    status = data["status"]
    signature = data["signature"]

    # Vérifier signature PayTech HMAC
    computed = hmac.new(
        PAYTECH_SECRET_KEY.encode(),
        msg=f"{order_id}{data['amount']}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if signature != computed:
        raise HTTPException(status_code=400, detail="Signature invalide.")

    # Mettre à jour la commande
    oid = validate_object_id(order_id)

    new_status = "paid" if status == "completed" else "failed"

    await db.orders.update_one(
        {"_id": oid},
        {"$set": {"status": new_status}}
    )

    return {"message": "Webhook reçu.", "status": new_status}


# -----------------------------------------------------------------------------------------
# VÉRIFIER LE STATUT D'UNE COMMANDE
# -----------------------------------------------------------------------------------------

@router.get("/status/{order_id}")
async def get_payment_status(order_id: str, user=Depends(get_current_user)):
    oid = validate_object_id(order_id)

    order = await db.orders.find_one({"_id": oid})

    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable.")

    if order["user_id"] != user["_id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé.")

    return {
        "order_id": order_id,
        "status": order["status"],
        "total": order["total"]
    }
