from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import (
    func,
    case,
    or_,
    and_
)
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.reparation import Reparation
from app.models.facture import Facture
from app.models.facture_ligne import FactureLigne
from app.models.stock import Stock
from app.models.client import Client


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# =========================================================
# CONSTANTES
# =========================================================

STATUTS_TERMINE = [
    "TERMINE",
    "TERMINEE",
    "TERMINÉ",
    "TERMINÉE",
    "LIVRE",
    "LIVREE",
    "LIVRÉ",
    "LIVRÉE",
]

STATUTS_ANNULE = [
    "ANNULE",
    "ANNULEE",
    "ANNULÉ",
    "ANNULÉE",
]


# =========================================================
# UTILITAIRES
# =========================================================

def get_period_dates(
    periode: str
):
    """
    Retourne la date de début et la date de fin
    correspondant à la période demandée.
    """

    maintenant = datetime.utcnow()

    periode = periode.lower().strip()

    if periode == "7j":

        debut = maintenant - timedelta(days=7)

    elif periode == "30j":

        debut = maintenant - timedelta(days=30)

    elif periode == "3m":

        debut = maintenant - timedelta(days=90)

    elif periode == "6m":

        debut = maintenant - timedelta(days=180)

    elif periode == "1an":

        debut = maintenant - timedelta(days=365)

    elif periode == "tout":

        debut = None

    else:

        # Par défaut
        debut = maintenant - timedelta(days=30)

    return debut, maintenant


def decimal_to_float(
    value
):
    """
    Convertit Decimal en float pour JSON.
    """

    if value is None:
        return 0.0

    if isinstance(
        value,
        Decimal
    ):
        return float(value)

    return float(value)


def normalize_status(
    status
):
    """
    Normalise légèrement les statuts
    pour les statistiques.
    """

    if status is None:
        return "Inconnu"

    value = str(status).strip()

    upper = value.upper()

    if upper in STATUTS_ANNULE:
        return "Annulé"

    if upper in STATUTS_TERMINE:
        return "Terminé"

    if "ATTENTE" in upper:
        return "En attente"

    if (
        "COURS" in upper
        or "INTERVENTION" in upper
        or "DIAGNOSTIC" in upper
    ):
        return "En cours"

    if (
        "PIECE" in upper
        or "PIÈCE" in upper
    ):
        return "En attente pièce"

    return value


# =========================================================
# ROUTE PRINCIPALE
# =========================================================

@router.get(
    "/stats"
)
def dashboard_stats(
    periode: str = Query(
        default="30j",
        description=(
            "Période : "
            "7j, 30j, 3m, 6m, 1an ou tout"
        )
    ),
    db: Session = Depends(get_db)
):

    # =====================================================
    # DATES
    # =====================================================

    date_debut, date_fin = get_period_dates(
        periode
    )

    # =====================================================
    # KPI - RÉPARATIONS
    # =====================================================

    total_reparations = (
        db.query(
            func.count(
                Reparation.id
            )
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Réparations sur la période
    # -----------------------------------------------------

    query_reparations_periode = db.query(
        func.count(
            Reparation.id
        )
    )

    if date_debut is not None:

        query_reparations_periode = (
            query_reparations_periode
            .filter(
                Reparation.date_reception >= date_debut,
                Reparation.date_reception <= date_fin
            )
        )

    reparations_periode = (
        query_reparations_periode.scalar()
        or 0
    )

    # =====================================================
    # DOSSIERS OUVERTS
    # =====================================================

    dossiers_ouverts = (
        db.query(
            func.count(
                Reparation.id
            )
        )
        .filter(
            ~Reparation.statut.in_(
                STATUTS_TERMINE
                + STATUTS_ANNULE
            )
        )
        .scalar()
        or 0
    )

    # =====================================================
    # EN ATTENTE
    # =====================================================

    reparations_attente = (
        db.query(
            func.count(
                Reparation.id
            )
        )
        .filter(
            Reparation.statut.ilike(
                "%attente%"
            )
        )
        .scalar()
        or 0
    )

    # =====================================================
    # EN COURS
    # =====================================================

    reparations_en_cours = (
        db.query(
            func.count(
                Reparation.id
            )
        )
        .filter(
            and_(
                ~Reparation.statut.in_(
                    STATUTS_TERMINE
                    + STATUTS_ANNULE
                ),
                ~Reparation.statut.ilike(
                    "%attente%"
                )
            )
        )
        .scalar()
        or 0
    )

    # =====================================================
    # TERMINÉES
    # =====================================================

    reparations_terminees = (
        db.query(
            func.count(
                Reparation.id
            )
        )
        .filter(
            Reparation.statut.in_(
                STATUTS_TERMINE
            )
        )
        .scalar()
        or 0
    )

    # =====================================================
    # ANNULÉES
    # =====================================================

    reparations_annulees = (
        db.query(
            func.count(
                Reparation.id
            )
        )
        .filter(
            Reparation.statut.in_(
                STATUTS_ANNULE
            )
        )
        .scalar()
        or 0
    )

    # =====================================================
    # KPI - FACTURES
    # =====================================================

    total_factures = (
        db.query(
            func.count(
                Facture.id
            )
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Factures période
    # -----------------------------------------------------

    query_factures_periode = db.query(
        func.count(
            Facture.id
        )
    )

    if date_debut is not None:

        query_factures_periode = (
            query_factures_periode
            .filter(
                Facture.date_facture >= date_debut,
                Facture.date_facture <= date_fin
            )
        )

    factures_periode = (
        query_factures_periode.scalar()
        or 0
    )

    # =====================================================
    # MONTANTS FACTURES
    # =====================================================

    query_total_ht = db.query(
        func.coalesce(
            func.sum(
                Facture.total_ht
            ),
            0
        )
    )

    query_total_ttc = db.query(
        func.coalesce(
            func.sum(
                Facture.total_ttc
            ),
            0
        )
    )

    if date_debut is not None:

        query_total_ht = (
            query_total_ht
            .filter(
                Facture.date_facture >= date_debut,
                Facture.date_facture <= date_fin
            )
        )

        query_total_ttc = (
            query_total_ttc
            .filter(
                Facture.date_facture >= date_debut,
                Facture.date_facture <= date_fin
            )
        )

    montant_factures_ht = (
        query_total_ht.scalar()
        or Decimal("0")
    )

    montant_factures_ttc = (
        query_total_ttc.scalar()
        or Decimal("0")
    )

    # =====================================================
    # KPI - STOCK
    # =====================================================

    total_produits = (
        db.query(
            func.count(
                Stock.id
            )
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Quantité totale
    # -----------------------------------------------------

    quantite_stock = (
        db.query(
            func.coalesce(
                func.sum(
                    Stock.quantite
                ),
                0
            )
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Stock faible
    # -----------------------------------------------------

    stock_faible_count = (
        db.query(
            func.count(
                Stock.id
            )
        )
        .filter(
            Stock.quantite <= Stock.seuil_min,
            Stock.quantite > 0
        )
        .scalar()
        or 0
    )

    # -----------------------------------------------------
    # Rupture
    # -----------------------------------------------------

    stock_rupture_count = (
        db.query(
            func.count(
                Stock.id
            )
        )
        .filter(
            Stock.quantite <= 0
        )
        .scalar()
        or 0
    )

    # =====================================================
    # KPI - CLIENTS
    # =====================================================

    total_clients = (
        db.query(
            func.count(
                Client.id
            )
        )
        .scalar()
        or 0
    )

    # =====================================================
    # RÉPARTITION DES STATUTS
    # =====================================================

    status_rows = (
        db.query(
            Reparation.statut,
            func.count(
                Reparation.id
            )
        )
        .group_by(
            Reparation.statut
        )
        .order_by(
            func.count(
                Reparation.id
            ).desc()
        )
        .all()
    )

    reparations_par_statut = []

    for statut, nombre in status_rows:

        reparations_par_statut.append({
            "statut": normalize_status(
                statut
            ),
            "nombre": nombre
        })

    # =====================================================
    # RÉPARATIONS PAR JOUR
    # =====================================================

    reparations_par_jour = []

    if date_debut is not None:

        # PostgreSQL
        date_expression = func.date(
            Reparation.date_reception
        )

        rows = (
            db.query(
                date_expression.label(
                    "date"
                ),
                func.count(
                    Reparation.id
                ).label(
                    "nombre"
                )
            )
            .filter(
                Reparation.date_reception >= date_debut,
                Reparation.date_reception <= date_fin
            )
            .group_by(
                date_expression
            )
            .order_by(
                date_expression
            )
            .all()
        )

        for date_value, nombre in rows:

            reparations_par_jour.append({
                "date": (
                    date_value.isoformat()
                    if date_value
                    else None
                ),
                "nombre": nombre
            })

    # =====================================================
    # FACTURES PAR JOUR
    # =====================================================

    factures_par_jour = []

    if date_debut is not None:

        date_expression = func.date(
            Facture.date_facture
        )

        rows = (
            db.query(
                date_expression.label(
                    "date"
                ),
                func.count(
                    Facture.id
                ).label(
                    "nombre"
                ),
                func.coalesce(
                    func.sum(
                        Facture.total_ttc
                    ),
                    0
                ).label(
                    "montant"
                )
            )
            .filter(
                Facture.date_facture >= date_debut,
                Facture.date_facture <= date_fin
            )
            .group_by(
                date_expression
            )
            .order_by(
                date_expression
            )
            .all()
        )

        for (
            date_value,
            nombre,
            montant
        ) in rows:

            factures_par_jour.append({
                "date": (
                    date_value.isoformat()
                    if date_value
                    else None
                ),
                "nombre": nombre,
                "montant": decimal_to_float(
                    montant
                )
            })

    # =====================================================
    # ALERTES STOCK
    # =====================================================

    stock_alertes_rows = (
        db.query(
            Stock
        )
        .filter(
            Stock.quantite <= Stock.seuil_min
        )
        .order_by(
            Stock.quantite.asc()
        )
        .limit(20)
        .all()
    )

    stock_alertes = []

    for piece in stock_alertes_rows:

        if piece.quantite <= 0:

            niveau = "rupture"

        elif piece.quantite <= piece.seuil_min:

            niveau = "faible"

        else:

            niveau = "normal"

        stock_alertes.append({
            "id": piece.id,
            "nom": piece.nom_piece,
            "reference": piece.reference,
            "categorie": piece.categorie,
            "quantite": piece.quantite,
            "seuil_min": piece.seuil_min,
            "prix_unitaire": decimal_to_float(
                piece.prix_unitaire
            ),
            "fournisseur": piece.fournisseur,
            "niveau": niveau
        })

    # =====================================================
    # TOP PRODUITS - ACHATS
    # =====================================================
    #
    # IMPORTANT :
    # Ceci n'est PAS le top des produits vendus.
    #
    # Avec la structure actuelle, FactureLigne représente
    # les lignes des factures fournisseurs.
    #
    # On calcule donc les produits les plus présents dans
    # les factures d'achat.
    #
    # Le véritable "produit le plus vendu" sera ajouté
    # après création des tables Vente / VenteLigne.
    # =====================================================

    top_produits_achats = []

    top_rows = (
        db.query(
            FactureLigne.stock_id,
            FactureLigne.designation,
            FactureLigne.reference,
            func.coalesce(
                func.sum(
                    FactureLigne.quantite
                ),
                0
            ).label(
                "quantite"
            ),
            func.coalesce(
                func.sum(
                    FactureLigne.total
                ),
                0
            ).label(
                "montant"
            )
        )
        .group_by(
            FactureLigne.stock_id,
            FactureLigne.designation,
            FactureLigne.reference
        )
        .order_by(
            func.sum(
                FactureLigne.quantite
            ).desc()
        )
        .limit(10)
        .all()
    )

    for (
        stock_id,
        designation,
        reference,
        quantite,
        montant
    ) in top_rows:

        top_produits_achats.append({
            "stock_id": stock_id,
            "designation": designation,
            "reference": reference,
            "quantite": decimal_to_float(
                quantite
            ),
            "montant": decimal_to_float(
                montant
            )
        })

    # =====================================================
    # PRODUITS SANS MOUVEMENT RÉCENT
    # =====================================================

    # On prend 5 mois comme valeur par défaut.
    date_limite_mouvement = (
        datetime.utcnow()
        - timedelta(
            days=150
        )
    )

    # Dernière facture connue pour chaque produit
    #
    # On utilise une sous-requête pour récupérer
    # la dernière date de facture.
    #

    derniere_facture = (
        db.query(
            FactureLigne.stock_id.label(
                "stock_id"
            ),
            func.max(
                Facture.date_facture
            ).label(
                "derniere_date"
            )
        )
        .join(
            Facture,
            Facture.id
            == FactureLigne.facture_id
        )
        .filter(
            FactureLigne.stock_id.isnot(None)
        )
        .group_by(
            FactureLigne.stock_id
        )
        .subquery()
    )

    produits_sans_mouvement_rows = (
        db.query(
            Stock,
            derniere_facture.c.derniere_date
        )
        .outerjoin(
            derniere_facture,
            derniere_facture.c.stock_id
            == Stock.id
        )
        .filter(
            or_(
                derniere_facture.c.derniere_date.is_(None),
                derniere_facture.c.derniere_date
                < date_limite_mouvement
            )
        )
        .order_by(
            Stock.date_ajout.asc()
        )
        .limit(20)
        .all()
    )

    produits_sans_mouvement = []

    for (
        piece,
        derniere_date
    ) in produits_sans_mouvement_rows:

        if derniere_date:

            jours = (
                datetime.utcnow()
                - derniere_date
            ).days

        else:

            jours = None

        produits_sans_mouvement.append({
            "id": piece.id,
            "nom": piece.nom_piece,
            "reference": piece.reference,
            "quantite": piece.quantite,
            "derniere_date": (
                derniere_date.isoformat()
                if derniere_date
                else None
            ),
            "jours_sans_mouvement": jours
        })

    # =====================================================
    # CLIENTS RÉCENTS
    # =====================================================

    clients_query = (
        db.query(
            Client
        )
        .order_by(
            Client.date_creation.desc()
        )
        .limit(10)
        .all()
    )

    clients_recents = []

    for client in clients_query:

        clients_recents.append({
            "id": client.id,
            "nom": client.nom,
            "telephone": client.telephone,
            "email": client.email,
            "adresse": client.adresse,
            "date_creation": (
                client.date_creation.isoformat()
                if client.date_creation
                else None
            )
        })

    # =====================================================
    # RÉPARATIONS RÉCENTES
    # =====================================================

    reparations_query = (
        db.query(
            Reparation
        )
        .order_by(
            Reparation.date_reception.desc()
        )
        .limit(10)
        .all()
    )

    reparations_recentes = []

    for reparation in reparations_query:

        client_nom = None

        if reparation.client:

            client_nom = (
                reparation.client.nom
            )

        reparations_recentes.append({
            "id": reparation.id,
            "numero_dossier": (
                reparation.numero_dossier
            ),
            "client": client_nom,
            "type_materiel": (
                reparation.type_materiel
            ),
            "statut": (
                normalize_status(
                    reparation.statut
                )
            ),
            "urgent": bool(
                reparation.urgent
            ),
            "date_reception": (
                reparation.date_reception.isoformat()
                if reparation.date_reception
                else None
            ),
            "cout_estime": decimal_to_float(
                reparation.cout_estime
            ),
            "cout_reel": decimal_to_float(
                reparation.cout_reel
            )
        })

    # =====================================================
    # STATISTIQUES RÉPARATION PAR TYPE DE MATÉRIEL
    # =====================================================

    materiel_rows = (
        db.query(
            Reparation.type_materiel,
            func.count(
                Reparation.id
            ).label(
                "nombre"
            )
        )
        .filter(
            Reparation.type_materiel.isnot(None)
        )
        .group_by(
            Reparation.type_materiel
        )
        .order_by(
            func.count(
                Reparation.id
            ).desc()
        )
        .limit(10)
        .all()
    )

    reparations_par_materiel = []

    for (
        type_materiel,
        nombre
    ) in materiel_rows:

        reparations_par_materiel.append({
            "type_materiel": type_materiel,
            "nombre": nombre
        })

    # =====================================================
    # RÉPARATIONS URGENTES
    # =====================================================

    reparations_urgentes = (
        db.query(
            func.count(
                Reparation.id
            )
        )
        .filter(
            Reparation.urgent.is_(True),
            ~Reparation.statut.in_(
                STATUTS_TERMINE
                + STATUTS_ANNULE
            )
        )
        .scalar()
        or 0
    )

    # =====================================================
    # COÛTS DE RÉPARATION
    # =====================================================

    cout_estime_total = (
        db.query(
            func.coalesce(
                func.sum(
                    Reparation.cout_estime
                ),
                0
            )
        )
        .scalar()
        or Decimal("0")
    )

    cout_reel_total = (
        db.query(
            func.coalesce(
                func.sum(
                    Reparation.cout_reel
                ),
                0
            )
        )
        .scalar()
        or Decimal("0")
    )

    # =====================================================
    # TEMPS MOYEN DE RÉPARATION
    # =====================================================

    reparations_avec_fin = (
        db.query(
            Reparation.date_reception,
            Reparation.date_fin
        )
        .filter(
            Reparation.date_fin.isnot(None),
            Reparation.date_reception.isnot(None)
        )
        .all()
    )

    durees = []

    for (
        date_reception,
        date_fin
    ) in reparations_avec_fin:

        if date_fin > date_reception:

            duree = (
                date_fin
                - date_reception
            ).total_seconds() / 86400

            durees.append(
                duree
            )

    if durees:

        delai_moyen_jours = round(
            sum(durees)
            / len(durees),
            2
        )

    else:

        delai_moyen_jours = 0

    # =====================================================
    # RÉPONSE
    # =====================================================

    return {

        # =================================================
        # META
        # =================================================

        "periode": {
            "code": periode,
            "date_debut": (
                date_debut.isoformat()
                if date_debut
                else None
            ),
            "date_fin": (
                date_fin.isoformat()
                if date_fin
                else None
            )
        },

        # =================================================
        # KPI
        # =================================================

        "kpis": {

            "reparations": total_reparations,

            "reparations_periode": (
                reparations_periode
            ),

            "dossiers_ouverts": (
                dossiers_ouverts
            ),

            "reparations_attente": (
                reparations_attente
            ),

            "reparations_en_cours": (
                reparations_en_cours
            ),

            "reparations_terminees": (
                reparations_terminees
            ),

            "reparations_annulees": (
                reparations_annulees
            ),

            "reparations_urgentes": (
                reparations_urgentes
            ),

            "factures": total_factures,

            "factures_periode": (
                factures_periode
            ),

            "montant_factures_ht": (
                decimal_to_float(
                    montant_factures_ht
                )
            ),

            "montant_factures_ttc": (
                decimal_to_float(
                    montant_factures_ttc
                )
            ),

            "produits": total_produits,

            "quantite_stock": (
                quantite_stock
            ),

            "stock_faible": (
                stock_faible_count
            ),

            "stock_rupture": (
                stock_rupture_count
            ),

            "clients": total_clients,

            "cout_estime_reparations": (
                decimal_to_float(
                    cout_estime_total
                )
            ),

            "cout_reel_reparations": (
                decimal_to_float(
                    cout_reel_total
                )
            ),

            "delai_moyen_jours": (
                delai_moyen_jours
            )
        },

        # =================================================
        # RÉPARATIONS
        # =================================================

        "reparations": {

            "par_statut": (
                reparations_par_statut
            ),

            "par_jour": (
                reparations_par_jour
            ),

            "par_materiel": (
                reparations_par_materiel
            ),

            "recentes": (
                reparations_recentes
            )
        },

        # =================================================
        # FACTURES
        # =================================================

        "factures": {

            "par_jour": (
                factures_par_jour
            )
        },

        # =================================================
        # STOCK
        # =================================================

        "stock": {

            "alertes": (
                stock_alertes
            ),

            "top_produits_achats": (
                top_produits_achats
            ),

            "sans_mouvement_5_mois": (
                produits_sans_mouvement
            )
        },

        # =================================================
        # CLIENTS
        # =================================================

        "clients": {

            "recents": (
                clients_recents
            )
        },

        # =================================================
        # ALERTES
        # =================================================

        "alertes": {

            "stock_faible": (
                stock_faible_count
            ),

            "stock_rupture": (
                stock_rupture_count
            ),

            "reparations_urgentes": (
                reparations_urgentes
            ),

            "dossiers_ouverts": (
                dossiers_ouverts
            )
        },

        # =================================================
        # MODULE VENTES
        # =================================================

        "ventes": {

            "disponible": False,

            "message": (
                "Le module ventes n'est pas encore "
                "présent dans la base de données."
            )
        }
    }
