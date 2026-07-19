from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.utilisateur import (
    UtilisateurCreate,
    UtilisateurUpdate,
    UtilisateurResponse
)

from app.crud.utilisateur import (
    create_utilisateur,
    get_utilisateurs,
    get_utilisateur,
    update_utilisateur,
    delete_utilisateur
)

router = APIRouter(
    prefix="/utilisateurs",
    tags=["Utilisateurs"]
)


@router.post("/", response_model=UtilisateurResponse)
def create(
    utilisateur: UtilisateurCreate,
    db: Session = Depends(get_db)
):
    return create_utilisateur(db, utilisateur)


@router.get("/", response_model=list[UtilisateurResponse])
def read_all(db: Session = Depends(get_db)):
    return get_utilisateurs(db)


@router.get("/{utilisateur_id}", response_model=UtilisateurResponse)
def read_one(
    utilisateur_id: int,
    db: Session = Depends(get_db)
):

    utilisateur = get_utilisateur(db, utilisateur_id)

    if not utilisateur:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    return utilisateur


@router.put("/{utilisateur_id}", response_model=UtilisateurResponse)
def update(
    utilisateur_id: int,
    data: UtilisateurUpdate,
    db: Session = Depends(get_db)
):

    utilisateur = update_utilisateur(
        db,
        utilisateur_id,
        data
    )

    if not utilisateur:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    return utilisateur


@router.delete("/{utilisateur_id}")
def delete(
    utilisateur_id: int,
    db: Session = Depends(get_db)
):

    utilisateur = delete_utilisateur(
        db,
        utilisateur_id
    )

    if not utilisateur:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    return {"message": "Utilisateur supprimé"}