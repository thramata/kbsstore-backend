# models/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: str
    email: EmailStr
    role: str = "client"
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
