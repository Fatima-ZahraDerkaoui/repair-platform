from sqlalchemy.orm import Session

from app.models.alerte_stock import AlerteStock


def get_alertes_stock(
    db: Session
):

    return (

        db.query(AlerteStock)

        .order_by(
            AlerteStock.date_creation.desc()
        )

        .all()

    )


def get_alertes_non_lues(
    db: Session
):

    return (

        db.query(AlerteStock)

        .filter(
            AlerteStock.statut == "NON_LUE"
        )

        .order_by(
            AlerteStock.date_creation.desc()
        )

        .all()

    )


def marquer_alerte_lue(

    db: Session,

    alerte_id: int

):

    alerte = (

        db.query(AlerteStock)

        .filter(
            AlerteStock.id == alerte_id
        )

        .first()

    )

    if not alerte:

        return None

    alerte.statut = "LUE"

    db.commit()

    db.refresh(alerte)

    return alerte