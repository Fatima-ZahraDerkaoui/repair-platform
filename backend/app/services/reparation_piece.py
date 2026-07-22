from sqlalchemy.orm import Session

from app.models.stock import Stock

from app.models.reparation import Reparation

from app.models.reparation_piece import ReparationPiece

from app.models.alerte_stock import AlerteStock


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

        raise ValueError(

            "Réparation introuvable"

        )


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


    # CAS 1 : STOCK INSUFFISANT

    if piece.quantite < quantite:

        alerte = AlerteStock(

            piece_id=piece.id,

            reparation_id=reparation.id,

            quantite_demandee=quantite,

            quantite_disponible=piece.quantite,

            message=(

                f"Stock insuffisant pour "

                f"{piece.nom_piece}. "

                f"Disponible : {piece.quantite}, "

                f"Demandé : {quantite}"

            ),

            statut="NON_LUE"

        )

        db.add(alerte)

        db.commit()

        raise ValueError(

            "Stock insuffisant. "

            "Une alerte a été créée."

        )


    # CAS 2 : STOCK DISPONIBLE

    piece.quantite -= quantite


    reparation_piece = ReparationPiece(

        reparation_id=reparation.id,

        piece_id=piece.id,

        quantite=quantite,

        prix_utilise=piece.prix_unitaire

    )


    db.add(reparation_piece)

    db.commit()

    db.refresh(reparation_piece)


    return reparation_piece