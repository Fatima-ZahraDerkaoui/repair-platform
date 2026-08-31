from decimal import Decimal
from pathlib import Path

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

from app.database.database import get_db
from app.models.reparation import Reparation
from app.models.reparation_piece import ReparationPiece
from app.models.stock import Stock

from app.schemas.reparation import (
    ReparationCreate,
    ReparationResponse,
    ReparationUpdate,
    StatutUpdate
)
from app.schemas.reparation_piece import (
    ReparationPieceCreate,
    ReparationPieceResponse
)

from app.crud.reparation import (
    create_reparation,
    get_reparations,
    get_reparation,
    update_reparation,
    delete_reparation
)

from app.services.statut import changer_statut
from app.services.reparation_piece import utiliser_piece
from app.services.fiche_pdf import generer_fiche_pdf
from app.services.ml.cout.cost_predictor import CostPredictor
from app.services.notification_service import notification_service

router = APIRouter(
    prefix="/reparations",
    tags=["Réparations"]
)

cost_predictor = CostPredictor()

# =====================================================
# FONCTION AUXILIAIRE : ENVOI NOTIFICATION CLIENT
# =====================================================

def verifier_et_envoyer_whatsapp(ancien_statut: str, nouveau_statut: str, reparation: Reparation):
    """Vérifie si le statut passe à Terminé et déclenche la notification (WhatsApp / Telegram)."""
    statuts_termines = {"TERMINÉ", "TERMINE", "TERMINÉE", "TERMINEE"}

    ancien_norm = (ancien_statut or "").strip().upper()
    nouveau_norm = (nouveau_statut or "").strip().upper()

    if nouveau_norm in statuts_termines and ancien_norm not in statuts_termines:
        client = reparation.client
        
        if client:
            designation_machine = f"{reparation.type_materiel or 'Machine'} {reparation.marque or ''} {reparation.modele or ''}".strip()
            
            # Récupération du chat_id Telegram (mettez votre ID réel de test ici si le champ n'existe pas en DB)
            telegram_id = getattr(client, "telegram_chat_id", None) or "6557139046"

            notification_service.notifier_client(
                nom_client=client.nom or "Client",
                telephone=client.telephone,
                nom_machine=designation_machine,
                numero_dossier=reparation.numero_dossier,
                telegram_chat_id=telegram_id
            )
        else:
            print(f"[NOTIFICATION] Annulé : aucun client associé à la réparation ID: {reparation.id}")

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
            joinedload(Reparation.client)
        )
        .filter(Reparation.numero_dossier == numero_dossier)
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
    reparation = get_reparation(db, id)

    if not reparation:
        raise HTTPException(
            status_code=404,
            detail="Réparation introuvable"
        )

    return reparation


# =====================================================
# MODIFIER STATUT SEUL
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
    reparation_existante = db.query(Reparation).filter(Reparation.id == reparation_id).first()
    if not reparation_existante:
        raise HTTPException(
            status_code=404,
            detail="Réparation introuvable"
        )

    ancien_statut = reparation_existante.statut

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

    reparation = (
        db.query(Reparation)
        .options(joinedload(Reparation.client))
        .filter(Reparation.id == reparation_id)
        .first()
    )

    # Déclenchement automatique WhatsApp
    verifier_et_envoyer_whatsapp(
        ancien_statut=ancien_statut,
        nouveau_statut=data.nouveau_statut,
        reparation=reparation
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
        piece = utiliser_piece(
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

    piece = (
        db.query(ReparationPiece)
        .options(joinedload(ReparationPiece.piece))
        .filter(ReparationPiece.id == piece.id)
        .first()
    )

    return piece


# =====================================================
# LIRE LES PIÈCES UTILISÉES
# =====================================================

@router.get(
    "/{reparation_id}/pieces",
    response_model=list[ReparationPieceResponse]
)
def lire_pieces(
    reparation_id: int,
    db: Session = Depends(get_db)
):
    reparation = db.query(Reparation).filter(Reparation.id == reparation_id).first()

    if not reparation:
        raise HTTPException(
            status_code=404,
            detail="Réparation introuvable"
        )

    pieces = (
        db.query(ReparationPiece)
        .options(joinedload(ReparationPiece.piece))
        .filter(ReparationPiece.reparation_id == reparation_id)
        .order_by(ReparationPiece.id.asc())
        .all()
    )

    return pieces


# =====================================================
# GÉNÉRER / TÉLÉCHARGER LA FICHE PDF
# =====================================================

@router.get("/{reparation_id}/fiche")
def generer_fiche(
    reparation_id: int,
    db: Session = Depends(get_db)
):
    reparation = (
        db.query(Reparation)
        .options(joinedload(Reparation.client))
        .filter(Reparation.id == reparation_id)
        .first()
    )

    if not reparation:
        raise HTTPException(
            status_code=404,
            detail="Réparation introuvable"
        )

    dossier = Path("uploads/fiches")
    dossier.mkdir(parents=True, exist_ok=True)

    chemin_pdf = dossier / f"{reparation.numero_dossier}.pdf"

    generer_fiche_pdf(
        reparation=reparation,
        client=reparation.client,
        chemin_fichier=str(chemin_pdf)
    )

    return FileResponse(
        path=str(chemin_pdf),
        media_type="application/pdf",
        filename=f"{reparation.numero_dossier}.pdf"
    )


# =====================================================
# MODIFIER LE DOSSIER (GLOBAL)
# =====================================================

@router.patch(
    "/{reparation_id}",
    response_model=ReparationResponse
)
def modifier_dossier(
    reparation_id: int,
    data: ReparationUpdate,
    db: Session = Depends(get_db)
):
    reparation_existante = db.query(Reparation).filter(Reparation.id == reparation_id).first()
    if not reparation_existante:
        raise HTTPException(
            status_code=404,
            detail="Réparation introuvable"
        )

    ancien_statut = reparation_existante.statut

    reparation = update_reparation(
        db=db,
        id=reparation_id,
        data=data
    )

    reparation = (
        db.query(Reparation)
        .options(joinedload(Reparation.client))
        .filter(Reparation.id == reparation_id)
        .first()
    )

    # Déclenchement automatique WhatsApp si le statut change dans la modification globale
    if data.statut is not None:
        verifier_et_envoyer_whatsapp(
            ancien_statut=ancien_statut,
            nouveau_statut=data.statut,
            reparation=reparation
        )

    return reparation


# =====================================================
# SUPPRIMER LE DOSSIER
# =====================================================

@router.delete("/{reparation_id}")
def supprimer_dossier(
    reparation_id: int,
    db: Session = Depends(get_db)
):
    try:
        reparation = delete_reparation(db=db, id=reparation_id)

        if not reparation:
            raise HTTPException(
                status_code=404,
                detail="Dossier de réparation introuvable."
            )

        return {
            "message": "Dossier supprimé avec succès.",
            "id": reparation_id
        }

    except HTTPException:
        raise
    except Exception as error:
        print(f"ERREUR SUPPRESSION DOSSIER {reparation_id}: {error}")
        raise HTTPException(
            status_code=500,
            detail="Impossible de supprimer le dossier."
        )


# =====================================================
# SUPPRIMER UNE PIÈCE UTILISÉE
# =====================================================

@router.delete("/{dossier_id}/pieces/{piece_utilisee_id}")
def supprimer_piece_utilisee(
    dossier_id: int,
    piece_utilisee_id: int,
    db: Session = Depends(get_db)
):
    reparation = db.query(Reparation).filter(Reparation.id == dossier_id).first()

    if not reparation:
        raise HTTPException(
            status_code=404,
            detail="Dossier de réparation introuvable."
        )

    piece_utilisee = (
        db.query(ReparationPiece)
        .filter(
            ReparationPiece.id == piece_utilisee_id,
            ReparationPiece.reparation_id == dossier_id
        )
        .first()
    )

    if not piece_utilisee:
        raise HTTPException(
            status_code=404,
            detail="Pièce utilisée introuvable pour ce dossier."
        )

    piece_id = piece_utilisee.piece_id
    quantite = piece_utilisee.quantite

    stock = db.query(Stock).filter(Stock.id == piece_id).first()

    if stock:
        stock.quantite += quantite

    db.delete(piece_utilisee)
    db.commit()

    return {
        "message": "Pièce supprimée avec succès.",
        "piece_utilisee_id": piece_utilisee_id,
        "piece_id": piece_id,
        "quantite_restituee": quantite
    }


# =====================================================
# PRÉDICTION DU COÛT & DÉLAI (ML)
# =====================================================

@router.post("/cout/predire")
def predire_cout(payload: dict):
    materiel = payload.get("type_materiel") or payload.get("materiel") or ""
    probleme = payload.get("probleme") or ""

    if not materiel or not probleme:
        raise HTTPException(
            status_code=400,
            detail="Le type de matériel et la description du problème sont requis."
        )

    try:
        prediction = cost_predictor.predict(
            materiel=materiel,
            probleme=probleme
        )

        if isinstance(prediction, dict):
            cout_estime = prediction.get("cout_estime") or prediction.get("predicted_cost") or 0.0
            delai_estime = prediction.get("delai_estime") or prediction.get("delai") or 1
        else:
            cout_estime = prediction
            delai_estime = 1

        return {
            "cout_estime": float(cout_estime),
            "delai_estime": int(delai_estime)
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du calcul de la prédiction ML : {str(error)}"
        )