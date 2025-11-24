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

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


# -----------------------------------------------------------------------------------------
# SCHÉMA PRODUIT — CRÉATION
# (utilisé lors de POST /products)
# -----------------------------------------------------------------------------------------
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2)
    price: float = Field(..., ge=0, description="Le prix doit être ≥ 0")
    stock: int = Field(..., ge=0, description="Le stock doit être ≥ 0")
    description: Optional[str] = ""
    # image uploadée avec multipart → pas dans le schema


# -----------------------------------------------------------------------------------------
# SCHÉMA PRODUIT — UPDATE
# (utilisé lors de PUT /products/{id})
# -----------------------------------------------------------------------------------------
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    # image uploadée → gérée via UploadFile dans products.py
