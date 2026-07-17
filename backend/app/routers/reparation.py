from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db

from app.schemas.reparation import (
    ReparationCreate,
    ReparationResponse
)

from app.crud.reparation import (
    create_reparation,
    get_reparations,
    get_reparation,
    update_reparation,
    delete_reparation
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


