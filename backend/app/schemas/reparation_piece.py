from decimal import Decimal

from pydantic import BaseModel


class ReparationPieceCreate(BaseModel):

    piece_id: int

    quantite: int


class ReparationPieceResponse(BaseModel):

    id: int

    reparation_id: int

    piece_id: int

    quantite: int

    prix_utilise: Decimal

    class Config:

        from_attributes = True