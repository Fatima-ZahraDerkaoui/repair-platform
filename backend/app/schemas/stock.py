from pydantic import BaseModel
from typing import Optional


class StockBase(BaseModel):
    nom_piece: str
    reference: Optional[str] = None
    categorie: Optional[str] = None
    quantite: int
    seuil_min: int
    prix_unitaire: float
    fournisseur: Optional[str] = None


class StockCreate(StockBase):
    pass


class StockUpdate(StockBase):
    pass


class StockResponse(StockBase):
    id: int

    class Config:
        from_attributes = True