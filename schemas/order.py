from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# -----------------------------------------------------------------------------------------
# ITEM DE COMMANDE (produit + quantité)
# -----------------------------------------------------------------------------------------
class OrderItem(BaseModel):
    _id: str = Field(..., description="ID du produit")
    quantity: int = Field(..., ge=1, description="Quantité ≥ 1")


# -----------------------------------------------------------------------------------------
# SCHÉMA COMMANDE — CRÉATION
# utilisé par POST /orders/
# -----------------------------------------------------------------------------------------
class OrderCreate(BaseModel):
    items: List[OrderItem]


# -----------------------------------------------------------------------------------------
# SCHÉMA COMMANDE — SORTIE API (lecture)
# utilisé par GET /orders/, /orders/mine, /orders/{id}
# -----------------------------------------------------------------------------------------
class OrderOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    items: List[OrderItem]
    total: float
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
