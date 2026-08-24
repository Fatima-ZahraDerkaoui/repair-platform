from decimal import Decimal

from typing import Optional

from pydantic import BaseModel


# =========================================================
# CREATION
# =========================================================

class ReparationPieceCreate(BaseModel):

    piece_id: int

    quantite: int


# =========================================================
# INFORMATIONS PIECE
# =========================================================

class PieceInfo(BaseModel):

    id: int

    nom_piece: str

    reference: Optional[str] = None

    categorie: Optional[str] = None

    quantite: int

    prix_unitaire: Optional[Decimal] = None

    class Config:

        from_attributes = True


# =========================================================
# REPONSE
# =========================================================

class ReparationPieceResponse(BaseModel):

    id: int

    reparation_id: int

    piece_id: int

    quantite: int

    prix_utilise: Decimal

    piece: Optional[PieceInfo] = None

    class Config:

        from_attributes = True
        