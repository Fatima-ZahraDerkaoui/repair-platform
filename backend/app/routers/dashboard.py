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

def get_period_dates(periode: str):
    maintenant = datetime.utcnow()
    periode = periode.lower().strip()

    if periode == "7j":
        debut = maintenant - timedelta(days=7)
    elif periode == "30j":
        debut = maintenant - timedelta(days=30)
    elif periode == "3m" or periode == "90j":
        debut = maintenant - timedelta(days=90)
    elif periode == "6m":
        debut = maintenant - timedelta(days=180)
    elif periode == "1an":
        debut = maintenant - timedelta(days=365)
    elif periode == "tout":
        debut = None
    else:
        debut = maintenant - timedelta(days=30)

    return debut, maintenant


def decimal_to_float(value):
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def normalize_status(status):
    if status is None:
        return "Inconnu"

    value = str(status).strip()
    upper = value.upper()

    if upper in STATUTS_ANNULE:
        return "Annulé"

    if upper in STATUTS_TERMINE or any(kw in upper for kw in ["TERMIN", "LIVR", "CLOTUR", "RECUP"]):
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

@router.get("/stats")
def dashboard_stats(
    periode: str = Query(
        default="30j",
        description="Période : 7j, 30j, 3m, 6m, 1an ou tout"
    ),
    db: Session = Depends(get_db)
):

    # =====================================================
    # DATES
    # =====================================================

    date_debut, date_fin = get_period_dates(periode)

    # =====================================================
    # KPI - RÉPARATIONS
    # =====================================================

    total_reparations = (
        db.query(func.count(Reparation.id)).scalar() or 0
    )

    query_reparations_periode = db.query(func.count(Reparation.id))
    if date_debut is not None:
        query_reparations_periode = query_reparations_periode.filter(
            Reparation.date_reception >= date_debut,
            Reparation.date_reception <= date_fin
        )
    reparations_periode = query_reparations_periode.scalar() or 0

    # =====================================================
    # DOSSIERS OUVERTS & STATUTS
    # =====================================================

    # Condition souple pour détecter les réparations terminées (insensible à la casse/accents)
    condition_terminee = or_(
        func.upper(Reparation.statut).in_(STATUTS_TERMINE),
        func.lower(Reparation.statut).like("%termin%"),
        func.lower(Reparation.statut).like("%livr%"),
        func.lower(Reparation.statut).like("%clotur%"),
        func.lower(Reparation.statut).like("%recup%")
    )

    condition_annulee = or_(
        func.upper(Reparation.statut).in_(STATUTS_ANNULE),
        func.lower(Reparation.statut).like("%annul%")
    )

    dossiers_ouverts = (
        db.query(func.count(Reparation.id))
        .filter(~condition_terminee, ~condition_annulee)
        .scalar() or 0
    )

    reparations_attente = (
        db.query(func.count(Reparation.id))
        .filter(Reparation.statut.ilike("%attente%"))
        .scalar() or 0
    )

    reparations_en_cours = (
        db.query(func.count(Reparation.id))
        .filter(~condition_terminee, ~condition_annulee, ~Reparation.statut.ilike("%attente%"))
        .scalar() or 0
    )

    # -----------------------------------------------------
    # RÉPARATIONS TERMINÉES (CORRIGÉ)
    # -----------------------------------------------------
    reparations_terminees = (
        db.query(func.count(Reparation.id))
        .filter(condition_terminee)
        .scalar() or 0
    )

    reparations_annulees = (
        db.query(func.count(Reparation.id))
        .filter(condition_annulee)
        .scalar() or 0
    )

    # =====================================================
    # CHIFFRE D'AFFAIRES RÉPARATIONS (CORRIGÉ)
    # =====================================================

    query_ca_reparations = db.query(
        func.coalesce(
            func.sum(
                func.coalesce(Reparation.cout_reel, Reparation.cout_estime, 0)
            ),
            0
        )
    )

    if date_debut is not None:
        query_ca_reparations = query_ca_reparations.filter(
            Reparation.date_reception >= date_debut,
            Reparation.date_reception <= date_fin
        )

    ca_reparations_total = query_ca_reparations.scalar() or Decimal("0")

    # =====================================================
    # KPI - FACTURES
    # =====================================================

    total_factures = db.query(func.count(Facture.id)).scalar() or 0

    query_factures_periode = db.query(func.count(Facture.id))
    query_total_ht = db.query(func.coalesce(func.sum(Facture.total_ht), 0))
    query_total_ttc = db.query(func.coalesce(func.sum(Facture.total_ttc), 0))

    if date_debut is not None:
        query_factures_periode = query_factures_periode.filter(
            Facture.date_facture >= date_debut,
            Facture.date_facture <= date_fin
        )
        query_total_ht = query_total_ht.filter(
            Facture.date_facture >= date_debut,
            Facture.date_facture <= date_fin
        )
        query_total_ttc = query_total_ttc.filter(
            Facture.date_facture >= date_debut,
            Facture.date_facture <= date_fin
        )

    factures_periode = query_factures_periode.scalar() or 0
    montant_factures_ht = query_total_ht.scalar() or Decimal("0")
    montant_factures_ttc = query_total_ttc.scalar() or Decimal("0")

    # =====================================================
    # KPI - STOCK & CLIENTS
    # =====================================================

    total_produits = db.query(func.count(Stock.id)).scalar() or 0
    quantite_stock = db.query(func.coalesce(func.sum(Stock.quantite), 0)).scalar() or 0

    stock_faible_count = (
        db.query(func.count(Stock.id))
        .filter(Stock.quantite <= Stock.seuil_min, Stock.quantite > 0)
        .scalar() or 0
    )

    stock_rupture_count = (
        db.query(func.count(Stock.id))
        .filter(Stock.quantite <= 0)
        .scalar() or 0
    )

    total_clients = db.query(func.count(Client.id)).scalar() or 0

    # =====================================================
    # RÉPARTITION ET SÉRIES DE DONNÉES
    # =====================================================

    status_rows = (
        db.query(Reparation.statut, func.count(Reparation.id))
        .group_by(Reparation.statut)
        .order_by(func.count(Reparation.id).desc())
        .all()
    )

    reparations_par_statut = [
        {"statut": normalize_status(s), "nombre": n} for s, n in status_rows
    ]

    reparations_par_jour = []
    if date_debut is not None:
        date_expression = func.date(Reparation.date_reception)
        rows = (
            db.query(
                date_expression.label("date"),
                func.count(Reparation.id).label("nombre"),
                func.coalesce(
                    func.sum(func.coalesce(Reparation.cout_reel, Reparation.cout_estime, 0)),
                    0
                ).label("cout_reel")
            )
            .filter(
                Reparation.date_reception >= date_debut,
                Reparation.date_reception <= date_fin
            )
            .group_by(date_expression)
            .order_by(date_expression)
            .all()
        )

        for date_value, nombre, cout_reel in rows:
            reparations_par_jour.append({
                "date": date_value.isoformat() if date_value else None,
                "nombre": nombre,
                "cout_reel": decimal_to_float(cout_reel)
            })

    factures_par_jour = []
    if date_debut is not None:
        date_expression = func.date(Facture.date_facture)
        rows = (
            db.query(
                date_expression.label("date"),
                func.count(Facture.id).label("nombre"),
                func.coalesce(func.sum(Facture.total_ttc), 0).label("montant")
            )
            .filter(
                Facture.date_facture >= date_debut,
                Facture.date_facture <= date_fin
            )
            .group_by(date_expression)
            .order_by(date_expression)
            .all()
        )

        for date_value, nombre, montant in rows:
            factures_par_jour.append({
                "date": date_value.isoformat() if date_value else None,
                "nombre": nombre,
                "montant": decimal_to_float(montant)
            })

    # Alertes Stock
    stock_alertes_rows = (
        db.query(Stock)
        .filter(Stock.quantite <= Stock.seuil_min)
        .order_by(Stock.quantite.asc())
        .limit(20)
        .all()
    )

    stock_alertes = []
    for piece in stock_alertes_rows:
        niveau = "rupture" if piece.quantite <= 0 else "faible"
        stock_alertes.append({
            "id": piece.id,
            "nom": piece.nom_piece,
            "reference": piece.reference,
            "categorie": piece.categorie,
            "quantite": piece.quantite,
            "seuil_min": piece.seuil_min,
            "prix_unitaire": decimal_to_float(piece.prix_unitaire),
            "fournisseur": piece.fournisseur,
            "niveau": niveau
        })

    # Top Achats Produit
    top_rows = (
        db.query(
            FactureLigne.stock_id,
            FactureLigne.designation,
            FactureLigne.reference,
            func.coalesce(func.sum(FactureLigne.quantite), 0).label("quantite"),
            func.coalesce(func.sum(FactureLigne.total), 0).label("montant")
        )
        .group_by(FactureLigne.stock_id, FactureLigne.designation, FactureLigne.reference)
        .order_by(func.sum(FactureLigne.quantite).desc())
        .limit(10)
        .all()
    )

    top_produits_achats = [
        {
            "stock_id": s_id,
            "designation": des,
            "reference": ref,
            "quantite": decimal_to_float(qty),
            "montant": decimal_to_float(mnt)
        }
        for s_id, des, ref, qty, mnt in top_rows
    ]

    # Produits sans mouvement
    date_limite_mouvement = datetime.utcnow() - timedelta(days=150)
    derniere_facture = (
        db.query(
            FactureLigne.stock_id.label("stock_id"),
            func.max(Facture.date_facture).label("derniere_date")
        )
        .join(Facture, Facture.id == FactureLigne.facture_id)
        .filter(FactureLigne.stock_id.isnot(None))
        .group_by(FactureLigne.stock_id)
        .subquery()
    )

    produits_sans_mouvement_rows = (
        db.query(Stock, derniere_facture.c.derniere_date)
        .outerjoin(derniere_facture, derniere_facture.c.stock_id == Stock.id)
        .filter(
            or_(
                derniere_facture.c.derniere_date.is_(None),
                derniere_facture.c.derniere_date < date_limite_mouvement
            )
        )
        .order_by(Stock.date_ajout.asc())
        .limit(20)
        .all()
    )

    produits_sans_mouvement = [
        {
            "id": p.id,
            "nom": p.nom_piece,
            "reference": p.reference,
            "quantite": p.quantite,
            "derniere_date": d.isoformat() if d else None,
            "jours_sans_mouvement": (datetime.utcnow() - d).days if d else None
        }
        for p, d in produits_sans_mouvement_rows
    ]

    # Clients récents
    clients_query = db.query(Client).order_by(Client.date_creation.desc()).limit(10).all()
    clients_recents = [
        {
            "id": c.id,
            "nom": c.nom,
            "telephone": c.telephone,
            "email": c.email,
            "adresse": c.adresse,
            "date_creation": c.date_creation.isoformat() if c.date_creation else None
        }
        for c in clients_query
    ]

    # Réparations récentes
    reparations_query = db.query(Reparation).order_by(Reparation.date_reception.desc()).limit(10).all()
    reparations_recentes = [
        {
            "id": r.id,
            "numero_dossier": r.numero_dossier,
            "client": r.client.nom if r.client else None,
            "type_materiel": r.type_materiel,
            "statut": normalize_status(r.statut),
            "urgent": bool(r.urgent),
            "date_reception": r.date_reception.isoformat() if r.date_reception else None,
            "cout_estime": decimal_to_float(r.cout_estime),
            "cout_reel": decimal_to_float(r.cout_reel)
        }
        for r in reparations_query
    ]

    # Types matériel
    materiel_rows = (
        db.query(Reparation.type_materiel, func.count(Reparation.id).label("nombre"))
        .filter(Reparation.type_materiel.isnot(None))
        .group_by(Reparation.type_materiel)
        .order_by(func.count(Reparation.id).desc())
        .limit(10)
        .all()
    )
    reparations_par_materiel = [{"type_materiel": m, "nombre": n} for m, n in materiel_rows]

    # Urgences
    reparations_urgentes = (
        db.query(func.count(Reparation.id))
        .filter(Reparation.urgent.is_(True), ~condition_terminee, ~condition_annulee)
        .scalar() or 0
    )

    # Coûts généraux
    cout_estime_total = db.query(func.coalesce(func.sum(Reparation.cout_estime), 0)).scalar() or Decimal("0")
    cout_reel_total = db.query(func.coalesce(func.sum(Reparation.cout_reel), 0)).scalar() or Decimal("0")

    # Délais
    reparations_avec_fin = (
        db.query(Reparation.date_reception, Reparation.date_fin)
        .filter(Reparation.date_fin.isnot(None), Reparation.date_reception.isnot(None))
        .all()
    )

    durees = [
        (fin - rec).total_seconds() / 86400
        for rec, fin in reparations_avec_fin if fin > rec
    ]
    delai_moyen_jours = round(sum(durees) / len(durees), 2) if durees else 0

    # =====================================================
    # RÉPONSE RENVOYÉE
    # =====================================================

    valeur_ca_reparations = decimal_to_float(ca_reparations_total)

    return {
        "periode": {
            "code": periode,
            "date_debut": date_debut.isoformat() if date_debut else None,
            "date_fin": date_fin.isoformat() if date_fin else None
        },
        "kpis": {
            "reparations": total_reparations,
            "reparations_periode": reparations_periode,
            "dossiers_ouverts": dossiers_ouverts,
            "reparations_attente": reparations_attente,
            "reparations_en_cours": reparations_en_cours,
            "reparations_terminees": reparations_terminees,
            "reparations_annulees": reparations_annulees,
            "reparations_urgentes": reparations_urgentes,
            "ca_reparations": valeur_ca_reparations,
            "ca_ttc": valeur_ca_reparations,
            "factures": total_factures,
            "factures_periode": factures_periode,
            "montant_factures_ht": decimal_to_float(montant_factures_ht),
            "montant_factures_ttc": decimal_to_float(montant_factures_ttc),
            "produits": total_produits,
            "quantite_stock": quantite_stock,
            "stock_faible": stock_faible_count,
            "stock_rupture": stock_rupture_count,
            "clients": total_clients,
            "cout_estime_reparations": decimal_to_float(cout_estime_total),
            "cout_reel_reparations": decimal_to_float(cout_reel_total),
            "delai_moyen_jours": delai_moyen_jours
        },
        "reparations": {
            "par_statut": reparations_par_statut,
            "par_jour": reparations_par_jour,
            "par_materiel": reparations_par_materiel,
            "recentes": reparations_recentes
        },
        "factures": {
            "par_jour": factures_par_jour
        },
        "stock": {
            "alertes": stock_alertes,
            "top_produits_achats": top_produits_achats,
            "sans_mouvement_5_mois": produits_sans_mouvement
        },
        "clients": {
            "recents": clients_recents
        },
        "alertes": {
            "stock_faible": stock_faible_count,
            "stock_rupture": stock_rupture_count,
            "reparations_urgentes": reparations_urgentes,
            "dossiers_ouverts": dossiers_ouverts
        },
        "ventes": {
            "disponible": False,
            "message": "Le module ventes n'est pas encore présent dans la base de données."
        }
    }