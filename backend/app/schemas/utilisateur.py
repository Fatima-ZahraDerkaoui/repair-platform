from pydantic import BaseModel, EmailStr
from typing import Optional


class UtilisateurBase(BaseModel):
    nom: str
    email: str
    role: str
    telephone: Optional[str] = None


class UtilisateurCreate(UtilisateurBase):
    password: str = "123456"  # Valeur par défaut pour éviter l'erreur 422 si non fourni


class UtilisateurUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    telephone: Optional[str] = None
    password: Optional[str] = None


class UtilisateurResponse(BaseModel):
    id: int
    nom: str
    email: str
    role: str
    telephone: Optional[str] = None

    class Config:
        from_attributes = True
        