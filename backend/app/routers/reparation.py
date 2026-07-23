from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.database.database import get_db
from app.models.reparation import Reparation
from app.schemas.reparation import (
    ReparationCreate,
    ReparationResponse,
    StatutUpdate
)

from app.crud.reparation import (
    create_reparation,
    get_reparations,
    get_reparation,
    get_reparation_by_numero
)

from app.schemas.reparation_piece import (
    ReparationPieceCreate,
    ReparationPieceResponse
)

from app.services.reparation_piece import (
    utiliser_piece
)

from app.services.statut import (
    changer_statut
)


router = APIRouter(
    prefix="/reparations",
    tags=["Réparations"]
)


# ==========================================
# CRÉER UNE RÉPARATION
# ==========================================

@router.post(
    "/",
    response_model=ReparationResponse
)
def create(
    reparation: ReparationCreate,
    db: Session = Depends(get_db)
):

    return create_reparation(
        db,
        reparation
    )


# ==========================================
# LIRE TOUTES LES RÉPARATIONS
# ==========================================

@router.get(
    "/",
    response_model=list[ReparationResponse]
)
def read_all(
    db: Session = Depends(get_db)
):

    return get_reparations(db)


# ==========================================
# CHERCHER PAR NUMÉRO DE DOSSIER
# IMPORTANT : AVANT /{id}
# ==========================================
@router.get(
    "/numero/{numero_dossier}",
    response_model=ReparationResponse
)
def get_reparation_by_numero(

    numero_dossier: str,

    db: Session = Depends(get_db)

):

    reparation = (

        db.query(Reparation)

        .filter(

            Reparation.numero_dossier

            == numero_dossier

        )

        .first()

    )


    if not reparation:

        raise HTTPException(

            status_code=404,

            detail="Dossier introuvable"

        )


    return reparation

#===========================================

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

            detail="Dossier de réparation introuvable"

        )


    return reparation


# ==========================================
# LIRE UNE RÉPARATION PAR ID
# ==========================================

@router.get(
    "/{id}",
    response_model=ReparationResponse
)
def read_one(

    id: int,

    db: Session = Depends(get_db)

):

    reparation = get_reparation(

        db,

        id

    )


    if not reparation:

        raise HTTPException(

            status_code=404,

            detail="Réparation introuvable"

        )


    return reparation


# ==========================================
# MODIFIER LE STATUT
# ==========================================

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

            nouveau_statut=data.nouveau_statut,

            utilisateur_id=data.utilisateur_id

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

        "ancien_statut":

        reparation.statut,

        "nouveau_statut":

        reparation.statut

    }


# ==========================================
# AJOUTER UNE PIÈCE À UNE RÉPARATION
# ==========================================

@router.post(

    "/{reparation_id}/pieces",

    response_model=ReparationPieceResponse

)
def ajouter_piece(

    reparation_id: int,

    data: ReparationPieceCreate,

    db: Session = Depends(get_db)

):

    try:

        return utiliser_piece(

            db=db,

            reparation_id=reparation_id,

            piece_id=data.piece_id,

            quantite=data.quantite

        )


    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)

        )


@router.get(
    "/numero/{numero_dossier}",
    response_model=ReparationResponse
)
def get_reparation_by_numero(

    numero_dossier: str,

    db: Session = Depends(get_db)

):

    reparation = (

        db.query(Reparation)

        .options(

            joinedload(

                Reparation.client

            )

        )

        .filter(

            Reparation.numero_dossier

            == numero_dossier

        )

        .first()

    )


    if not reparation:

        raise HTTPException(

            status_code=404,

            detail="Dossier introuvable"

        )


    return reparation