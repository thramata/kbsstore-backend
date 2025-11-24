from pydantic import BaseModel, Field
from typing import Optional

# -----------------------------------------------------------------------------------------
# SCHÉMA PRODUIT — SORTIE API (lecture)
# -----------------------------------------------------------------------------------------
class ProductOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    price: float
    stock: int
    description: Optional[str] = ""
    image: Optional[str] = None

    model_config = {
        "populate_by_name": True
    }


# -----------------------------------------------------------------------------------------
# SCHÉMA PRODUIT — CRÉATION
# -----------------------------------------------------------------------------------------
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2)
    price: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    description: Optional[str] = ""


# -----------------------------------------------------------------------------------------
# SCHÉMA PRODUIT — UPDATE
# -----------------------------------------------------------------------------------------
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
