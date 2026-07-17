from pydantic import BaseModel, EmailStr
from typing import Optional


class ClientBase(BaseModel):
    nom: str
    telephone: str
    email: Optional[EmailStr] = None
    adresse: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: int

    class Config:
        from_attributes = True