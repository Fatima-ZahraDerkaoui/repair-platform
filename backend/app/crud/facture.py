from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.facture import Facture
from app.models.facture_ligne import FactureLigne
from app.models.fournisseur import Fournisseur
from app.models.stock import Stock

from app.schemas.facture import (
    FactureCreate,
    FactureUpdate
)

from app.schemas.facture_ligne import (
    FactureLigneCreate,
    FactureLigneUpdate
)


# ==========================================================
# UTILITAIRE
# ==========================================================

def _normaliser_texte(
    valeur: str | None
) -> str:

    if not valeur:
        return ""

    return " ".join(
        str(valeur).strip().upper().split()
    )


# ==========================================================
# CONVERSION FOURNISSEUR
# ==========================================================

def _supplier_to_dict(
    fournisseur_data: Any
) -> dict | None:

    if fournisseur_data is None:
        return None

    # ------------------------------------------------------
    # Déjà dictionnaire
    # ------------------------------------------------------

    if isinstance(
        fournisseur_data,
        dict
    ):
        return fournisseur_data

    # ------------------------------------------------------
    # Pydantic
    # ------------------------------------------------------

    if hasattr(
        fournisseur_data,
        "model_dump"
    ):

        return fournisseur_data.model_dump(
            exclude_none=True
        )

    # ------------------------------------------------------
    # Ancienne version Pydantic
    # ------------------------------------------------------

    if hasattr(
        fournisseur_data,
        "dict"
    ):

        return fournisseur_data.dict(
            exclude_none=True
        )

    return None


# ==========================================================
# FOURNISSEUR
# ==========================================================

def _get_ou_creer_fournisseur(
    db: Session,
    fournisseur_data: dict | None,
    fournisseur_id: int | None = None
) -> Fournisseur | None:

    # ======================================================
    # NORMALISATION
    # ======================================================

    fournisseur_data = _supplier_to_dict(
        fournisseur_data
    )

    # ======================================================
    # 1. FOURNISSEUR ID DEJA FOURNI
    # ======================================================

    if fournisseur_id is not None:

        fournisseur = db.get(
            Fournisseur,
            fournisseur_id
        )

        if fournisseur is not None:

            print(
                "[FOURNISSEUR] Trouvé par ID :",
                fournisseur.id
            )

            return fournisseur

        print(
            "[FOURNISSEUR] ID fourni mais introuvable :",
            fournisseur_id
        )

    # ======================================================
    # 2. AUCUNE INFORMATION
    # ======================================================

    if not fournisseur_data:

        print(
            "[FOURNISSEUR] Aucune information fournisseur."
        )

        return None

    # ======================================================
    # DEBUG
    # ======================================================

    print(
        "[FOURNISSEUR] Données reçues :",
        fournisseur_data
    )

    # ======================================================
    # 3. NOM
    # ======================================================

    nom = (
        fournisseur_data.get("name")
        or fournisseur_data.get("nom")
    )

    nom = (
        str(nom).strip()
        if nom
        else None
    )

    if not nom:

        print(
            "[FOURNISSEUR] Nom fournisseur introuvable."
        )

        return None

    nom_normalise = _normaliser_texte(
        nom
    )

    # ======================================================
    # 4. IDENTIFIANTS
    # ======================================================

    ice = fournisseur_data.get(
        "ice"
    )

    if ice:
        ice = str(
            ice
        ).strip()

    email = fournisseur_data.get(
        "email"
    )

    if email:
        email = str(
            email
        ).strip()

    rc = fournisseur_data.get(
        "rc"
    )

    if rc:
        rc = str(
            rc
        ).strip()

    identifiant_fiscal = (
        fournisseur_data.get("if")
        or fournisseur_data.get(
            "identifiant_fiscal"
        )
    )

    if identifiant_fiscal:
        identifiant_fiscal = str(
            identifiant_fiscal
        ).strip()

    # ======================================================
    # 5. RECHERCHE PAR ICE
    # ======================================================

    if ice:

        fournisseur = (
            db.query(Fournisseur)
            .filter(
                Fournisseur.ice == ice
            )
            .first()
        )

        if fournisseur is not None:

            print(
                "[FOURNISSEUR] Trouvé par ICE :",
                fournisseur.id
            )

            return fournisseur

    # ======================================================
    # 6. RECHERCHE PAR EMAIL
    # ======================================================

    if email:

        fournisseur = (
            db.query(Fournisseur)
            .filter(
                Fournisseur.email.ilike(
                    email
                )
            )
            .first()
        )

        if fournisseur is not None:

            print(
                "[FOURNISSEUR] Trouvé par email :",
                fournisseur.id
            )

            return fournisseur

    # ======================================================
    # 7. RECHERCHE PAR RC
    # ======================================================

    if rc:

        fournisseur = (
            db.query(Fournisseur)
            .filter(
                Fournisseur.rc == rc
            )
            .first()
        )

        if fournisseur is not None:

            print(
                "[FOURNISSEUR] Trouvé par RC :",
                fournisseur.id
            )

            return fournisseur

    # ======================================================
    # 8. RECHERCHE PAR IF
    # ======================================================

    if identifiant_fiscal:

        fournisseur = (
            db.query(Fournisseur)
            .filter(
                Fournisseur.identifiant_fiscal
                == identifiant_fiscal
            )
            .first()
        )

        if fournisseur is not None:

            print(
                "[FOURNISSEUR] Trouvé par IF :",
                fournisseur.id
            )

            return fournisseur

    # ======================================================
    # 9. RECHERCHE PAR NOM
    # ======================================================

    fournisseurs = (
        db.query(Fournisseur)
        .all()
    )

    for fournisseur in fournisseurs:

        if (
            _normaliser_texte(
                fournisseur.nom
            )
            == nom_normalise
        ):

            print(
                "[FOURNISSEUR] Trouvé par nom :",
                fournisseur.id
            )

            return fournisseur

    # ======================================================
    # 10. CREATION
    # ======================================================

    print(
        "[FOURNISSEUR] Création du fournisseur :",
        nom
    )

    fournisseur = Fournisseur(

        nom=nom,

        adresse=(
            fournisseur_data.get("address")
            or fournisseur_data.get("adresse")
        ),

        ville=(
            fournisseur_data.get("city")
            or fournisseur_data.get("ville")
        ),

        pays=(
            fournisseur_data.get("country")
            or fournisseur_data.get("pays")
        ),

        telephone=(
            fournisseur_data.get("phone")
            or fournisseur_data.get("telephone")
        ),

        fax=fournisseur_data.get(
            "fax"
        ),

        email=email,

        site_web=(
            fournisseur_data.get("website")
            or fournisseur_data.get("site_web")
        ),

        ice=ice,

        identifiant_fiscal=identifiant_fiscal,

        rc=rc,

        patente=fournisseur_data.get(
            "patente"
        ),

        cnss=fournisseur_data.get(
            "cnss"
        ),

        rib=fournisseur_data.get(
            "rib"
        )
    )

    db.add(
        fournisseur
    )

    db.flush()

    print(
        "[FOURNISSEUR] Nouveau fournisseur ID :",
        fournisseur.id
    )

    print(
        "[FOURNISSEUR] Nom :",
        fournisseur.nom
    )

    return fournisseur


# ==========================================================
# STOCK
# ==========================================================

def _get_ou_creer_stock(
    db: Session,
    ligne_data,
    fournisseur: Fournisseur | None = None
) -> Stock:

    reference = ligne_data.reference

    designation = ligne_data.designation

    # ======================================================
    # 1. RECHERCHE REFERENCE
    # ======================================================

    stock = None

    if reference:

        reference_normalisee = (
            reference.strip().upper()
        )

        stock = (
            db.query(Stock)
            .filter(
                Stock.reference
                == reference_normalisee
            )
            .first()
        )

        if stock is not None:

            print(
                "[STOCK] Article trouvé par référence :",
                reference,
                "→ ID :",
                stock.id
            )

    # ======================================================
    # 2. RECHERCHE DESIGNATION
    # ======================================================

    if stock is None and designation:

        designation_normalisee = (
            _normaliser_texte(
                designation
            )
        )

        stocks = (
            db.query(Stock)
            .all()
        )

        for piece in stocks:

            if (
                _normaliser_texte(
                    piece.nom_piece
                )
                == designation_normalisee
            ):

                stock = piece

                print(
                    "[STOCK] Article trouvé par désignation :",
                    stock.id
                )

                break

    # ======================================================
    # 3. ARTICLE EXISTANT
    # ======================================================

    if stock is not None:

        quantite_facture = (
            ligne_data.quantite
        )

        if quantite_facture is not None:

            ancienne_quantite = (
                stock.quantite
            )

            stock.quantite = (
                stock.quantite
                + int(quantite_facture)
            )

            print(
                "[STOCK] Quantité :",
                ancienne_quantite,
                "+",
                int(quantite_facture),
                "=",
                stock.quantite
            )

        if (
            ligne_data.prix_unitaire
            is not None
        ):

            stock.prix_unitaire = (
                ligne_data.prix_unitaire
            )

        if fournisseur is not None:

            stock.fournisseur = (
                fournisseur.nom
            )

        db.flush()

        return stock

    # ======================================================
    # 4. NOUVEL ARTICLE
    # ======================================================

    quantite_initiale = 0

    if ligne_data.quantite is not None:

        quantite_initiale = int(
            ligne_data.quantite
        )

    nom_piece = (
        designation
        if designation
        else (
            reference
            if reference
            else "ARTICLE SANS NOM"
        )
    )

    reference_stock = None

    if reference:

        reference_stock = (
            reference.strip().upper()
        )

    stock = Stock(

        nom_piece=nom_piece,

        reference=reference_stock,

        categorie=None,

        quantite=quantite_initiale,

        seuil_min=5,

        prix_unitaire=(
            ligne_data.prix_unitaire
        ),

        fournisseur=(
            fournisseur.nom
            if fournisseur is not None
            else None
        )
    )

    db.add(
        stock
    )

    db.flush()

    print(
        "[STOCK] Nouvel article :",
        nom_piece
    )

    print(
        "[STOCK] Nouvel article ID :",
        stock.id
    )

    return stock


# ==========================================================
# CREATE FACTURE
# ==========================================================

def create(
    db: Session,
    data: FactureCreate
) -> Facture:

    try:

        print()
        print("=" * 80)
        print("ENREGISTREMENT FACTURE")
        print("=" * 80)

        # ==================================================
        # 1. FOURNISSEUR
        # ==================================================

        fournisseur = (
            _get_ou_creer_fournisseur(

                db=db,

                fournisseur_data=(
                    data.fournisseur
                ),

                fournisseur_id=(
                    data.fournisseur_id
                )
            )
        )

        # ==================================================
        # 2. FACTURE
        # ==================================================

        facture = Facture(

            fournisseur_id=(
                fournisseur.id
                if fournisseur is not None
                else None
            ),

            numero=data.numero,

            date_facture=data.date_facture,

            total_ht=data.total_ht,

            total_tva=data.total_tva,

            total_ttc=data.total_ttc,

            statut=data.statut,

            texte_ocr=data.texte_ocr,

            chemin_document=data.chemin_document
        )

        db.add(
            facture
        )

        db.flush()

        print(
            "[FACTURE] ID temporaire :",
            facture.id
        )

        print(
            "[FACTURE] Fournisseur ID :",
            facture.fournisseur_id
        )

        # ==================================================
        # 3. LIGNES
        # ==================================================

        for index, ligne_data in enumerate(
            data.lignes,
            start=1
        ):

            print()
            print(
                f"[LIGNE {index}]"
            )

            print(
                "  Référence :",
                ligne_data.reference
            )

            print(
                "  Désignation :",
                ligne_data.designation
            )

            print(
                "  Quantité :",
                ligne_data.quantite
            )

            stock = (
                _get_ou_creer_stock(

                    db=db,

                    ligne_data=ligne_data,

                    fournisseur=fournisseur
                )
            )

            ligne = FactureLigne(

                facture_id=facture.id,

                stock_id=stock.id,

                designation=(
                    ligne_data.designation
                ),

                reference=(
                    ligne_data.reference
                ),

                quantite=(
                    ligne_data.quantite
                ),

                prix_unitaire=(
                    ligne_data.prix_unitaire
                ),

                total=(
                    ligne_data.total
                )
            )

            facture.lignes.append(
                ligne
            )

            print(
                "  Stock ID :",
                stock.id
            )

        # ==================================================
        # 4. COMMIT
        # ==================================================

        db.commit()

        # ==================================================
        # 5. RECHARGER AVEC RELATIONS
        # ==================================================

        facture = get_by_id(
            db,
            facture.id
        )

        if facture is None:

            raise RuntimeError(
                "La facture a été créée mais "
                "impossible de la recharger."
            )

        print()
        print("=" * 80)
        print("FACTURE ENREGISTREE")
        print("=" * 80)

        print(
            "FACTURE ID :",
            facture.id
        )

        print(
            "FOURNISSEUR ID :",
            facture.fournisseur_id
        )

        print(
            "FOURNISSEUR :",
            (
                facture.fournisseur.nom
                if facture.fournisseur
                else None
            )
        )

        print(
            "NUMERO :",
            facture.numero
        )

        print(
            "LIGNES :",
            len(facture.lignes)
        )

        print("=" * 80)

        return facture

    except Exception:

        db.rollback()

        print()
        print(
            "[FACTURE] ERREUR → ROLLBACK"
        )

        raise


# ==========================================================
# GET BY ID
# ==========================================================

def get_by_id(
    db: Session,
    facture_id: int
) -> Facture | None:

    result = db.execute(

        select(Facture)

        .options(

            selectinload(
                Facture.lignes
            ),

            selectinload(
                Facture.fournisseur
            )
        )

        .where(
            Facture.id == facture_id
        )
    )

    return result.scalar_one_or_none()


# ==========================================================
# GET ALL
# ==========================================================

def get_all(
    db: Session
) -> list[Facture]:

    result = db.execute(

        select(Facture)

        .options(

            selectinload(
                Facture.lignes
            ),

            selectinload(
                Facture.fournisseur
            )
        )

        .order_by(
            Facture.id.desc()
        )
    )

    return list(
        result.scalars()
        .unique()
        .all()
    )


# ==========================================================
# GET BY NUMERO
# ==========================================================

def get_by_numero(
    db: Session,
    numero: str
) -> Facture | None:

    result = db.execute(

        select(Facture)

        .options(

            selectinload(
                Facture.lignes
            ),

            selectinload(
                Facture.fournisseur
            )
        )

        .where(
            Facture.numero == numero
        )
    )

    return result.scalar_one_or_none()


# ==========================================================
# UPDATE FACTURE
# ==========================================================

def update(
    db: Session,
    facture: Facture,
    data: FactureUpdate
) -> Facture:

    values = data.model_dump(
        exclude_unset=True
    )

    for field, value in values.items():

        setattr(
            facture,
            field,
            value
        )

    db.commit()

    return get_by_id(
        db,
        facture.id
    )


# ==========================================================
# DELETE FACTURE
# ==========================================================

def delete(
    db: Session,
    facture: Facture
) -> None:

    db.delete(
        facture
    )

    db.commit()


# ==========================================================
# AJOUTER LIGNE
# ==========================================================

def add_ligne(
    db: Session,
    facture_id: int,
    data: FactureLigneCreate
) -> FactureLigne:

    ligne = FactureLigne(

        facture_id=facture_id,

        **data.model_dump()
    )

    db.add(
        ligne
    )

    db.commit()

    db.refresh(
        ligne
    )

    return ligne


# ==========================================================
# GET LIGNE
# ==========================================================

def get_ligne(
    db: Session,
    ligne_id: int
) -> FactureLigne | None:

    return db.get(
        FactureLigne,
        ligne_id
    )


# ==========================================================
# UPDATE LIGNE
# ==========================================================

def update_ligne(
    db: Session,
    ligne: FactureLigne,
    data: FactureLigneUpdate
) -> FactureLigne:

    values = data.model_dump(
        exclude_unset=True
    )

    for field, value in values.items():

        setattr(
            ligne,
            field,
            value
        )

    db.commit()

    db.refresh(
        ligne
    )

    return ligne


# ==========================================================
# DELETE LIGNE
# ==========================================================

def delete_ligne(
    db: Session,
    ligne: FactureLigne
) -> None:

    db.delete(
        ligne
    )

    db.commit()
    