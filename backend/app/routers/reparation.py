from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.historique_statut import (
    ChangerStatutRequest
)
from app.services.statut import (
    changer_statut
)
from app.schemas.reparation import (
    ReparationCreate,
    ReparationResponse,
    StatutUpdate
)

from app.crud.reparation import (
    create_reparation,
    get_reparations,
    get_reparation,
    get_reparation_by_numero,
    update_reparation,
    delete_reparation,
    update_statut
)

router = APIRouter(
    prefix="/reparations",
    tags=["Réparations"]
)

@router.post(
    "/",
    response_model=ReparationResponse
)
def create(
    reparation: ReparationCreate,
    db: Session = Depends(get_db)
):

    return create_reparation(db, reparation)


@router.get(
    "/",
    response_model=list[ReparationResponse]
)
def read_all(
    db: Session = Depends(get_db)
):

    return get_reparations(db)


@router.get(
    "/{id}",
    response_model=ReparationResponse
)
def read_one(
    id: int,
    db: Session = Depends(get_db)
):

    rep = get_reparation(db, id)

    if not rep:
        raise HTTPException(
            status_code=404,
            detail="Réparation introuvable"
        )

    return rep

@router.get(
    "/numero/{numero_dossier}",
    response_model=ReparationResponse
)
def get_by_numero(
    numero_dossier: str,
    db: Session = Depends(get_db)
):

    reparation = get_reparation_by_numero(
        db,
        numero_dossier
    )

    if not reparation:

        raise HTTPException(
            status_code=404,
            detail="Réparation introuvable"
        )

    return reparation


@router.patch(
    "/{reparation_id}/statut"
)
def modifier_statut(

    reparation_id: int,

    data: StatutUpdate,

    db: Session = Depends(get_db)

):

    try:

        reparation = changer_statut(

            db=db,

            reparation_id=reparation_id,

            nouveau_statut=data.nouveau_statut

        )

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)

        )


    if not reparation:

        raise HTTPException(

            status_code=404,

            detail="Réparation introuvable"

        )


    return {

        "message":
        "Statut modifié avec succès",

        "reparation_id":
        reparation.id,

        "nouveau_statut":
        reparation.statut

    }