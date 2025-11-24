# models/product.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Product(BaseModel):
    id: str
    name: str
    price: float
    description: Optional[str] = ""
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
