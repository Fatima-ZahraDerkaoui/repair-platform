from decimal import Decimal, InvalidOperation
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.fournisseur import Fournisseur
from app.models.facture import Facture
from app.models.facture_ligne import FactureLigne
from app.models.stock import Stock


class FactureImportService:

    # ==========================================================
    # INITIALISATION
    # ==========================================================

    def __init__(self, db: Session):

        self.db = db

    # ==========================================================
    # CONVERSION DECIMAL
    # ==========================================================

    @staticmethod
    def to_decimal(value):

        if value is None:
            return None

        if isinstance(value, Decimal):
            return value

        try:

            if isinstance(value, str):

                value = value.strip()

                if not value:
                    return None

                # Gestion formats :
                # 1234.50
                # 1234,50
                # 1 234,50
                # 1.234,50

                value = value.replace(" ", "")

                if "," in value and "." in value:

                    if value.rfind(",") > value.rfind("."):
                        value = value.replace(".", "")
                        value = value.replace(",", ".")

                    else:
                        value = value.replace(",", "")

                else:

                    value = value.replace(",", ".")

            return Decimal(str(value))

        except (InvalidOperation, ValueError, TypeError):

            return None

    # ==========================================================
    # PARSE DATE
    # ==========================================================

    @staticmethod
    def parse_date(value):

        if not value:
            return None

        if isinstance(value, datetime):
            return value

        value = str(value).strip()

        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%d/%m/%y",
            "%d-%m-%y",
        ]

        for fmt in formats:

            try:
                return datetime.strptime(value, fmt)

            except ValueError:
                continue

        return None

    # ==========================================================
    # NORMALISATION TEXTE
    # ==========================================================

    @staticmethod
    def normalize_text(value):

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        return value

    # ==========================================================
    # RECHERCHE FOURNISSEUR
    # ==========================================================

    def find_fournisseur(
        self,
        fournisseur_data
    ):

        if not fournisseur_data:
            return None

        name = self.normalize_text(
            fournisseur_data.get("name")
        )

        ice = self.normalize_text(
            fournisseur_data.get("ice")
        )

        email = self.normalize_text(
            fournisseur_data.get("email")
        )

        # ------------------------------------------------------
        # Recherche prioritaire par ICE
        # ------------------------------------------------------

        if ice:

            fournisseur = (
                self.db.query(Fournisseur)
                .filter(Fournisseur.ice == ice)
                .first()
            )

            if fournisseur:
                return fournisseur

        # ------------------------------------------------------
        # Recherche par email
        # ------------------------------------------------------

        if email:

            fournisseur = (
                self.db.query(Fournisseur)
                .filter(Fournisseur.email == email)
                .first()
            )

            if fournisseur:
                return fournisseur

        # ------------------------------------------------------
        # Recherche par nom
        # ------------------------------------------------------

        if name:

            fournisseur = (
                self.db.query(Fournisseur)
                .filter(Fournisseur.name.ilike(name))
                .first()
            )

            if fournisseur:
                return fournisseur

        return None

    # ==========================================================
    # CREATION FOURNISSEUR
    # ==========================================================

    def create_fournisseur(
        self,
        fournisseur_data
    ):

        if not fournisseur_data:
            return None

        fournisseur = self.find_fournisseur(
            fournisseur_data
        )

        if fournisseur:

            return fournisseur

        phones = fournisseur_data.get("phone")

        # ------------------------------------------------------
        # Le modèle fournisseur doit avoir un champ téléphone
        # adapté à ta structure.
        # ------------------------------------------------------

        if isinstance(phones, list):

            telephone = ", ".join(
                str(phone)
                for phone in phones
                if phone
            )

        else:

            telephone = phones

        fournisseur = Fournisseur(

            name=self.normalize_text(
                fournisseur_data.get("name")
            ),

            address=self.normalize_text(
                fournisseur_data.get("address")
            ),

            city=self.normalize_text(
                fournisseur_data.get("city")
            ),

            country=self.normalize_text(
                fournisseur_data.get("country")
            ),

            phone=self.normalize_text(
                telephone
            ),

            fax=self.normalize_text(
                fournisseur_data.get("fax")
            ),

            email=self.normalize_text(
                fournisseur_data.get("email")
            ),

            website=self.normalize_text(
                fournisseur_data.get("website")
            ),

            ice=self.normalize_text(
                fournisseur_data.get("ice")
            ),

            if_=self.normalize_text(
                fournisseur_data.get("if")
            ),

            rc=self.normalize_text(
                fournisseur_data.get("rc")
            ),

            patente=self.normalize_text(
                fournisseur_data.get("patente")
            ),

            cnss=self.normalize_text(
                fournisseur_data.get("cnss")
            ),

            rib=self.normalize_text(
                fournisseur_data.get("rib")
            )
        )

        self.db.add(fournisseur)

        self.db.flush()

        return fournisseur

    # ==========================================================
    # RECHERCHE ARTICLE STOCK
    # ==========================================================

    def find_stock_article(
        self,
        reference=None,
        designation=None
    ):

        reference = self.normalize_text(reference)
        designation = self.normalize_text(designation)

        # ------------------------------------------------------
        # 1. Recherche par référence
        # ------------------------------------------------------

        if reference:

            article = (
                self.db.query(Stock)
                .filter(
                    Stock.reference == reference
                )
                .first()
            )

            if article:
                return article

        # ------------------------------------------------------
        # 2. Recherche par désignation
        # ------------------------------------------------------

        if designation:

            article = (
                self.db.query(Stock)
                .filter(
                    Stock.nom_piece.ilike(designation)
                )
                .first()
            )

            if article:
                return article

        return None

    # ==========================================================
    # CREATION LIGNE FACTURE
    # ==========================================================

    def create_facture_ligne(
        self,
        facture,
        article_data
    ):

        reference = self.normalize_text(
            article_data.get("reference")
        )

        designation = self.normalize_text(
            article_data.get("designation")
        )

        quantite = self.to_decimal(
            article_data.get("quantite")
        )

        prix_unitaire = self.to_decimal(
            article_data.get("prix_unitaire")
        )

        total = self.to_decimal(
            article_data.get("total")
        )

        # ------------------------------------------------------
        # Recherche dans stock
        # ------------------------------------------------------

        stock_article = self.find_stock_article(
            reference=reference,
            designation=designation
        )

        # ------------------------------------------------------
        # Création ligne
        # ------------------------------------------------------

        ligne = FactureLigne(

            facture_id=facture.id,

            stock_id=(
                stock_article.id
                if stock_article
                else None
            ),

            designation=designation,

            reference=reference,

            quantite=quantite,

            prix_unitaire=prix_unitaire,

            total=total
        )

        self.db.add(ligne)

        return ligne

    # ==========================================================
    # CREATION FACTURE
    # ==========================================================

    def create_facture(
        self,
        facture_data,
        texte_ocr=None,
        chemin_document=None
    ):

        # ------------------------------------------------------
        # Fournisseur
        # ------------------------------------------------------

        fournisseur = self.create_fournisseur(
            facture_data.get("fournisseur")
        )

        # ------------------------------------------------------
        # Date
        # ------------------------------------------------------

        date_facture = self.parse_date(
            facture_data.get("date")
        )

        # ------------------------------------------------------
        # Facture
        # ------------------------------------------------------

        facture = Facture(

            fournisseur_id=(
                fournisseur.id
                if fournisseur
                else None
            ),

            numero=self.normalize_text(
                facture_data.get("numero")
            ),

            date_facture=date_facture,

            total_ht=self.to_decimal(
                facture_data.get("total_ht")
            ),

            total_tva=self.to_decimal(
                facture_data.get("total_tva")
            ),

            total_ttc=self.to_decimal(
                facture_data.get("total_ttc")
            ),

            statut="A_VALIDER",

            texte_ocr=texte_ocr,

            chemin_document=chemin_document
        )

        self.db.add(facture)

        self.db.flush()

        # ------------------------------------------------------
        # Lignes
        # ------------------------------------------------------

        articles = facture_data.get(
            "articles",
            []
        )

        for article_data in articles:

            self.create_facture_ligne(
                facture,
                article_data
            )

        # ------------------------------------------------------
        # Validation transaction
        # ------------------------------------------------------

        self.db.commit()

        # ------------------------------------------------------
        # Rafraîchir
        # ------------------------------------------------------

        self.db.refresh(facture)

        return facture

    # ==========================================================
    # IMPORT COMPLET
    # ==========================================================

    def import_facture(
        self,
        facture_data,
        texte_ocr=None,
        chemin_document=None
    ):

        try:

            facture = self.create_facture(

                facture_data=facture_data,

                texte_ocr=texte_ocr,

                chemin_document=chemin_document
            )

            return facture

        except Exception:

            self.db.rollback()

            raise