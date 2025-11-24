from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# -----------------------------------------------------------------------------------------
# SCHÉMA UTILISATEUR POUR LECTURE
# -----------------------------------------------------------------------------------------
class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    role: str = "user"

    model_config = {
        "populate_by_name": True
    }


# -----------------------------------------------------------------------------------------
# SCHÉMA POUR CRÉATION UTILISATEUR
# -----------------------------------------------------------------------------------------
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)


# -----------------------------------------------------------------------------------------
# SCHÉMA POUR LOGIN
# -----------------------------------------------------------------------------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -----------------------------------------------------------------------------------------
# SCHÉMA POUR CHANGEMENT DE MOT DE PASSE
# -----------------------------------------------------------------------------------------
class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)
