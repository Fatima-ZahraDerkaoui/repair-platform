from sqlalchemy.orm import Session, joinedload

from app.models.reparation import Reparation
from app.models.reparation_piece import ReparationPiece
from app.models.historique_statut import HistoriqueStatut
from app.models.alerte_stock import AlerteStock
from app.models.stock import Stock
from app.models.client import Client

from app.schemas.reparation import (
    ReparationCreate,
    ReparationUpdate
)

from app.services.dossier import (
    generer_numero_dossier
)

from app.services.qr_code import (
    generer_qr_code
)

from app.services.fiche_pdf import (
    generer_fiche_pdf
)

from app.crud.historique_statut import (
    create_historique
)

import os


# =====================================================
# CRÉER UNE RÉPARATION
# =====================================================

def create_reparation(
    db: Session,
    reparation: ReparationCreate
):

    nouvelle = Reparation(
        **reparation.model_dump()
    )

    db.add(nouvelle)
    db.commit()
    db.refresh(nouvelle)

    # -------------------------------------------------
    # Numéro du dossier
    # -------------------------------------------------

    nouvelle.numero_dossier = generer_numero_dossier(
        nouvelle.id
    )

    # -------------------------------------------------
    # QR Code
    # -------------------------------------------------

    nouvelle.qr_code = generer_qr_code(
        nouvelle.numero_dossier
    )

    db.commit()
    db.refresh(nouvelle)

    # -------------------------------------------------
    # Client
    # -------------------------------------------------

    client = nouvelle.client

    # -------------------------------------------------
    # Génération du PDF
    # -------------------------------------------------

    dossier_fiches = "uploads/fiches"

    os.makedirs(
        dossier_fiches,
        exist_ok=True
    )

    chemin_fiche = os.path.join(
        dossier_fiches,
        f"{nouvelle.numero_dossier}.pdf"
    )

    generer_fiche_pdf(
        reparation=nouvelle,
        client=client,
        chemin_fichier=chemin_fiche
    )

    return nouvelle


# =====================================================
# LIRE TOUTES LES RÉPARATIONS
# =====================================================

def get_reparations(
    db: Session
):

    return (
        db.query(Reparation)
        .options(
            joinedload(Reparation.client)
        )
        .all()
    )


# =====================================================
# LIRE UNE RÉPARATION PAR ID
# =====================================================

def get_reparation(
    db: Session,
    id: int
):

    return (
        db.query(Reparation)
        .options(
            joinedload(Reparation.client)
        )
        .filter(
            Reparation.id == id
        )
        .first()
    )


# =====================================================
# LIRE UNE RÉPARATION PAR NUMÉRO
# =====================================================

def get_reparation_by_numero(
    db: Session,
    numero_dossier: str
):

    return (
        db.query(Reparation)
        .options(
            joinedload(Reparation.client)
        )
        .filter(
            Reparation.numero_dossier == numero_dossier
        )
        .first()
    )


# =====================================================
# MODIFIER UNE RÉPARATION
# =====================================================

def update_reparation(
    db: Session,
    id: int,
    data: ReparationUpdate
):

    reparation = get_reparation(
        db,
        id
    )

    if not reparation:
        return None

    # =================================================
    # DONNÉES REÇUES
    # =================================================

    values = data.model_dump(
        exclude_unset=True
    )

    # =================================================
    # DONNÉES CLIENT
    # =================================================

    client = reparation.client

    client_modified = False

    if "client_nom" in values:
        client.nom = values["client_nom"]
        client_modified = True

    if "client_telephone" in values:
        client.telephone = values["client_telephone"]
        client_modified = True

    if "client_email" in values:
        client.email = values["client_email"]
        client_modified = True

    # =================================================
    # DONNÉES RÉPARATION
    # =================================================

    champs_reparation = [
        "type_materiel",
        "marque",
        "modele",
        "numero_serie",
        "probleme",
        "diagnostic",
        "intervention",
        "pieces_defectueuses",
        "accessoires",
        "remarques",
        "cout_reel",
        "date_fin"
    ]

    for champ in champs_reparation:

        if champ in values:

            setattr(
                reparation,
                champ,
                values[champ]
            )

    # =================================================
    # STATUT
    # =================================================

    if "statut" in values:

        nouveau_statut = values["statut"]

        ancien_statut = reparation.statut

        if nouveau_statut != ancien_statut:

            reparation.statut = nouveau_statut

            create_historique(
                db=db,
                reparation_id=reparation.id,
                ancien_statut=ancien_statut,
                nouveau_statut=nouveau_statut,
                utilisateur_id=None
            )

    # =================================================
    # SAUVEGARDE
    # =================================================

    db.commit()

    db.refresh(reparation)

    return reparation


# =====================================================
# SUPPRIMER UNE RÉPARATION
# =====================================================

def delete_reparation(
    db: Session,
    id: int
):

    reparation = (
        db.query(Reparation)
        .filter(
            Reparation.id == id
        )
        .first()
    )

    if not reparation:
        return None

    try:

        # =================================================
        # 1. RÉCUPÉRER LES PIÈCES UTILISÉES
        # =================================================

        pieces_utilisees = (
            db.query(ReparationPiece)
            .filter(
                ReparationPiece.reparation_id == id
            )
            .all()
        )

        # =================================================
        # 2. RESTAURER LE STOCK
        # =================================================

        for ligne in pieces_utilisees:

            piece = (
                db.query(Stock)
                .filter(
                    Stock.id == ligne.piece_id
                )
                .first()
            )

            if piece:

                piece.quantite += ligne.quantite

        # =================================================
        # 3. SUPPRIMER LES ALERTES STOCK
        # =================================================

        db.query(AlerteStock).filter(
            AlerteStock.reparation_id == id
        ).delete(
            synchronize_session=False
        )

        # =================================================
        # 4. SUPPRIMER LES PIÈCES UTILISÉES
        # =================================================

        db.query(ReparationPiece).filter(
            ReparationPiece.reparation_id == id
        ).delete(
            synchronize_session=False
        )

        # =================================================
        # 5. SUPPRIMER L'HISTORIQUE DES STATUTS
        # =================================================

        db.query(HistoriqueStatut).filter(
            HistoriqueStatut.reparation_id == id
        ).delete(
            synchronize_session=False
        )

        # =================================================
        # 6. SUPPRIMER LE DOSSIER
        # =================================================

        numero_dossier = reparation.numero_dossier

        db.delete(reparation)

        db.commit()

        # =================================================
        # 7. SUPPRIMER LE PDF
        # =================================================

        if numero_dossier:

            chemin_pdf = os.path.join(
                "uploads",
                "fiches",
                f"{numero_dossier}.pdf"
            )

            if os.path.exists(chemin_pdf):

                try:
                    os.remove(chemin_pdf)

                except OSError:
                    pass

        return reparation

    except Exception:

        db.rollback()

        raise


# =====================================================
# MODIFIER LE STATUT
# =====================================================

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
