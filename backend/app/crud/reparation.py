from sqlalchemy.orm import Session

from app.models.reparation import Reparation
from app.schemas.reparation import ReparationCreate, ReparationUpdate
from app.services.dossier import generer_numero_dossier
from app.services.qr_code import generer_qr_code
from app.crud.historique_statut import (
    create_historique
)

def create_reparation(
    db: Session,
    reparation: ReparationCreate
):

    nouvelle = Reparation(**reparation.model_dump())

    db.add(nouvelle)

    # Premier commit : génère l'id
    db.commit()

    db.refresh(nouvelle)

    # Génération du numéro de dossier
    nouvelle.numero_dossier = generer_numero_dossier(nouvelle.id)
    
    nouvelle.qr_code = generer_qr_code(
        nouvelle.numero_dossier
    )
    # Sauvegarde du numéro
    db.commit()

    db.refresh(nouvelle)

    return nouvelle


# Lire toutes les réparations
def get_reparations(db: Session):
    return db.query(Reparation).all()

def get_reparation_by_numero(
    db: Session,
    numero_dossier: str
):

    return (
        db.query(Reparation)
        .filter(
            Reparation.numero_dossier
            == numero_dossier
        )
        .first()
    )

# Lire une réparation
def get_reparation(db: Session, id: int):
    return (
        db.query(Reparation)
        .filter(Reparation.id == id)
        .first()
    )


# Modifier
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


# Supprimer
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


def update_statut(

    db: Session,

    reparation_id: int,

    nouveau_statut: str,

    utilisateur_id: int | None = None

):

    reparation = get_reparation(

        db,

        reparation_id

    )

    if not reparation:

        return None

    ancien_statut = reparation.statut

    reparation.statut = nouveau_statut

    create_historique(

        db=db,

        reparation_id=reparation.id,

        ancien_statut=ancien_statut,

        nouveau_statut=nouveau_statut,

        utilisateur_id=utilisateur_id

    )

    db.commit()

    db.refresh(reparation)

    return reparation
