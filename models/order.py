# models/order.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Order(BaseModel):
    id: str
    order_id: str
    user_id: str
    amount: float
    status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
