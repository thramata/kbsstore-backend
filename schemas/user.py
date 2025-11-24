from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# -----------------------------------------------------------------------------------------
# SCHÉMA UTILISATEUR POUR LECTURE (RETOUR API)
# -----------------------------------------------------------------------------------------
class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    role: str = "user"

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


# -----------------------------------------------------------------------------------------
# SCHÉMA POUR CRÉATION UTILISATEUR
# (NE PAS METTRE LE MOT DE PASSE APRÈS CRÉATION)
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
