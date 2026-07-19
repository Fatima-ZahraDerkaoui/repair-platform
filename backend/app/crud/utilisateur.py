from sqlalchemy.orm import Session

from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurUpdate


def create_utilisateur(db: Session, utilisateur: UtilisateurCreate):

    nouveau = Utilisateur(**utilisateur.model_dump())

    db.add(nouveau)

    db.commit()

    db.refresh(nouveau)

    return nouveau


def get_utilisateurs(db: Session):

    return db.query(Utilisateur).all()


def get_utilisateur(db: Session, utilisateur_id: int):

    return db.query(Utilisateur).filter(
        Utilisateur.id == utilisateur_id
    ).first()


def update_utilisateur(
    db: Session,
    utilisateur_id: int,
    data: UtilisateurUpdate
):

    utilisateur = get_utilisateur(db, utilisateur_id)

    if not utilisateur:
        return None

    for key, value in data.model_dump().items():
        setattr(utilisateur, key, value)

    db.commit()

    db.refresh(utilisateur)

    return utilisateur


def delete_utilisateur(db: Session, utilisateur_id: int):

    utilisateur = get_utilisateur(db, utilisateur_id)

    if not utilisateur:
        return None

    db.delete(utilisateur)

    db.commit()

    return utilisateur