


from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import (
    Session,
    joinedload
)

from pathlib import Path


from app.database.database import (
    get_db
)


from app.models.reparation import (
    Reparation
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
    get_reparation_by_numero
)


from app.services.statut import (
    changer_statut
)


from app.services.reparation_piece import (
    utiliser_piece
)


from app.schemas.reparation_piece import (
    ReparationPieceCreate,
    ReparationPieceResponse
)


from app.services.fiche_pdf import (
    generer_fiche_pdf
)


router = APIRouter(
    prefix="/reparations",
    tags=["Réparations"]
)


# =====================================================
# CRÉER
# =====================================================

@router.post("/")
def create(
    data: ReparationCreate,
    db: Session = Depends(get_db)
):

    nouvelle = create_reparation(
        db=db,
        reparation=data
    )

    return {
        "id": nouvelle.id,
        "numero_dossier": nouvelle.numero_dossier,
        "qr_code": nouvelle.qr_code,
        "client_nom": nouvelle.client.nom,
        "client_telephone": nouvelle.client.telephone,
        "type_materiel": nouvelle.type_materiel,
        "statut": nouvelle.statut
    }


# =====================================================
# LIRE TOUTES
# =====================================================

@router.get(
    "/",
    response_model=list[ReparationResponse]
)
def read_all(
    db: Session = Depends(get_db)
):

    return get_reparations(db)


# =====================================================
# CHERCHER PAR NUMÉRO
# =====================================================

@router.get(
    "/numero/{numero_dossier}",
    response_model=ReparationResponse
)
def get_by_numero(
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


# =====================================================
# LIRE PAR ID
# =====================================================

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


# =====================================================
# MODIFIER STATUT
# =====================================================

@router.patch(
    "/{reparation_id}/statut",
    response_model=ReparationResponse
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

    # =================================================
    # RECHARGER LE CLIENT
    # =================================================

    reparation = (
        db.query(Reparation)
        .options(
            joinedload(
                Reparation.client
            )
        )
        .filter(
            Reparation.id == reparation_id
        )
        .first()
    )

    return reparation


# =====================================================
# AJOUTER UNE PIÈCE
# =====================================================

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


# =====================================================
# GÉNÉRER / TÉLÉCHARGER LA FICHE PDF
# =====================================================

@router.get(
    "/{reparation_id}/fiche"
)
def generer_fiche(
    reparation_id: int,
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
            Reparation.id == reparation_id
        )
        .first()
    )

    if not reparation:

        raise HTTPException(
            status_code=404,
            detail="Réparation introuvable"
        )

    dossier = Path(
        "uploads/fiches"
    )

    dossier.mkdir(
        parents=True,
        exist_ok=True
    )

    chemin_pdf = (
        dossier
        /
        f"{reparation.numero_dossier}.pdf"
    )

    generer_fiche_pdf(
        reparation=reparation,
        client=reparation.client,
        chemin_fichier=str(
            chemin_pdf
        )
    )

    return FileResponse(
        path=str(
            chemin_pdf
        ),
        media_type="application/pdf",
        filename=(
            f"{reparation.numero_dossier}.pdf"
        )
    )
