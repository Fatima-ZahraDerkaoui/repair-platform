from sqlalchemy.orm import Session

from app.models.stock import Stock
from app.models.reparation import Reparation
from app.models.reparation_piece import ReparationPiece


def utiliser_piece(

    db: Session,

    reparation_id: int,

    piece_id: int,

    quantite: int

):

    if quantite <= 0:

        raise ValueError(
            "La quantité doit être supérieure à zéro"
        )


    reparation = (

        db.query(Reparation)

        .filter(
            Reparation.id == reparation_id
        )

        .first()
    )


    if not reparation:

        return None


    piece = (

        db.query(Stock)

        .filter(
            Stock.id == piece_id
        )

        .first()
    )


    if not piece:

        raise ValueError(
            "Pièce introuvable"
        )


    if piece.quantite < quantite:

        raise ValueError(
            "Stock insuffisant"
        )


    piece.quantite -= quantite


    reparation_piece = ReparationPiece(

        reparation_id=reparation_id,

        piece_id=piece_id,

        quantite=quantite,

        prix_utilise=piece.prix_unitaire

    )


    db.add(reparation_piece)

    db.commit()

    db.refresh(reparation_piece)


    return reparation_piece