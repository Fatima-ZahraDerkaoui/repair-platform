from pydantic import BaseModel
from typing import Optional


class UtilisateurBase(BaseModel):
    nom: str
    email: str
    password: str
    role: str
    telephone: Optional[str] = None


class UtilisateurCreate(UtilisateurBase):
    pass


class UtilisateurUpdate(UtilisateurBase):
    pass


class UtilisateurResponse(BaseModel):
    id: int
    nom: str
    email: str
    role: str
    telephone: Optional[str]

    class Config:
        from_attributes = True