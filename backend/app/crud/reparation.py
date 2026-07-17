from sqlalchemy.orm import Session

from app.models.reparation import Reparation
from app.schemas.reparation import ReparationCreate , ReparationUpdate

def create_reparation(
    db: Session,
    reparation: ReparationCreate
):

    nouvelle = Reparation(**reparation.model_dump())

    db.add(nouvelle)

    db.commit()

    db.refresh(nouvelle)

    return nouvelle

#Lire toutes les réparations
def get_reparations(db: Session):

    return db.query(Reparation).all()

#Lire une réparation
def get_reparation(
    db: Session,
    id: int
):

    return (
        db.query(Reparation)
        .filter(Reparation.id == id)
        .first()
    )

#Modifier
def update_reparation(
    db: Session,
    id: int,
    data: ReparationUpdate
):

    reparation = get_reparation(db, id)

    if not reparation:
        return None

    for key, value in data.model_dump().items():
        setattr(reparation, key, value)

    db.commit()

    db.refresh(reparation)

    return reparation

#Supprimer
def delete_reparation(
    db: Session,
    id: int
):

    reparation = get_reparation(db, id)

    if not reparation:
        return None

    db.delete(reparation)

    db.commit()

    return reparation

