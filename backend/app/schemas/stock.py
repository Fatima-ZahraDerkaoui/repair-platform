from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class StockBase(BaseModel):

    nom_piece: str

    reference: str | None = None

    categorie: str | None = None

    quantite: int = 0

    seuil_min: int = 5

    prix_unitaire: Decimal | None = None

    fournisseur: str | None = None


class StockCreate(StockBase):

    pass


class StockUpdate(BaseModel):

    nom_piece: str | None = None

    reference: str | None = None

    categorie: str | None = None

    quantite: int | None = None

    seuil_min: int | None = None

    prix_unitaire: Decimal | None = None

    fournisseur: str | None = None


class StockResponse(StockBase):

    id: int

    date_ajout: datetime

    class Config:

        from_attributes = True