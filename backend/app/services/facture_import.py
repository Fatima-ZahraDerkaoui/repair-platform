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

        except (
            InvalidOperation,
            ValueError,
            TypeError
        ):

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

                return datetime.strptime(
                    value,
                    fmt
                )

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
    # NORMALISATION COMPARAISON
    # ==========================================================

    @staticmethod
    def normalize_compare(value):

        if value is None:
            return None

        value = str(value).strip().upper()

        if not value:
            return None

        return value

    # ==========================================================
    # EXTRACTION TELEPHONE
    # ==========================================================

    @staticmethod
    def normalize_phone(value):

        if value is None:
            return None

        if isinstance(value, list):

            phones = []

            for phone in value:

                phone = str(phone).strip()

                if phone and phone not in phones:
                    phones.append(phone)

            return ", ".join(phones) if phones else None

        return str(value).strip() or None

    # ==========================================================
    # RECHERCHE FOURNISSEUR
    # ==========================================================

    def find_fournisseur(
        self,
        fournisseur_data
    ):

        if not fournisseur_data:
            return None

        if not isinstance(
            fournisseur_data,
            dict
        ):
            return None

        nom = self.normalize_text(
            fournisseur_data.get("name")
            or fournisseur_data.get("nom")
        )

        ice = self.normalize_text(
            fournisseur_data.get("ice")
        )

        email = self.normalize_text(
            fournisseur_data.get("email")
        )

        rc = self.normalize_text(
            fournisseur_data.get("rc")
        )

        identifiant_fiscal = self.normalize_text(
            fournisseur_data.get("if")
            or fournisseur_data.get(
                "identifiant_fiscal"
            )
        )

        # ------------------------------------------------------
        # 1. ICE
        # ------------------------------------------------------

        if ice:

            fournisseur = (
                self.db.query(Fournisseur)
                .filter(
                    Fournisseur.ice == ice
                )
                .first()
            )

            if fournisseur:

                print(
                    "[FOURNISSEUR] Trouvé par ICE :",
                    fournisseur.id
                )

                return fournisseur

        # ------------------------------------------------------
        # 2. EMAIL
        # ------------------------------------------------------

        if email:

            fournisseur = (
                self.db.query(Fournisseur)
                .filter(
                    Fournisseur.email.ilike(email)
                )
                .first()
            )

            if fournisseur:

                print(
                    "[FOURNISSEUR] Trouvé par email :",
                    fournisseur.id
                )

                return fournisseur

        # ------------------------------------------------------
        # 3. RC
        # ------------------------------------------------------

        if rc:

            fournisseur = (
                self.db.query(Fournisseur)
                .filter(
                    Fournisseur.rc == rc
                )
                .first()
            )

            if fournisseur:

                print(
                    "[FOURNISSEUR] Trouvé par RC :",
                    fournisseur.id
                )

                return fournisseur

        # ------------------------------------------------------
        # 4. IDENTIFIANT FISCAL
        # ------------------------------------------------------

        if identifiant_fiscal:

            fournisseur = (
                self.db.query(Fournisseur)
                .filter(
                    Fournisseur.identifiant_fiscal
                    == identifiant_fiscal
                )
                .first()
            )

            if fournisseur:

                print(
                    "[FOURNISSEUR] Trouvé par IF :",
                    fournisseur.id
                )

                return fournisseur

        # ------------------------------------------------------
        # 5. NOM
        # ------------------------------------------------------

        if nom:

            fournisseur = (
                self.db.query(Fournisseur)
                .filter(
                    Fournisseur.nom.ilike(nom)
                )
                .first()
            )

            if fournisseur:

                print(
                    "[FOURNISSEUR] Trouvé par nom :",
                    fournisseur.id
                )

                return fournisseur

        print(
            "[FOURNISSEUR] Fournisseur non trouvé."
        )

        return None

    # ==========================================================
    # CREER FOURNISSEUR
    # ==========================================================

    def create_fournisseur(
        self,
        fournisseur_data
    ):

        if not fournisseur_data:
            print(
                "[FOURNISSEUR] Aucune information fournisseur."
            )

            return None

        if not isinstance(
            fournisseur_data,
            dict
        ):

            print(
                "[FOURNISSEUR] Format fournisseur invalide."
            )

            return None

        # ------------------------------------------------------
        # Vérifier d'abord s'il existe
        # ------------------------------------------------------

        fournisseur_existant = (
            self.find_fournisseur(
                fournisseur_data
            )
        )

        if fournisseur_existant:

            print(
                "[FOURNISSEUR] Fournisseur existant "
                "réutilisé :",
                fournisseur_existant.id
            )

            return fournisseur_existant

        # ------------------------------------------------------
        # Données OCR
        # ------------------------------------------------------

        nom = self.normalize_text(
            fournisseur_data.get("name")
            or fournisseur_data.get("nom")
        )

        adresse = self.normalize_text(
            fournisseur_data.get("address")
            or fournisseur_data.get("adresse")
        )

        ville = self.normalize_text(
            fournisseur_data.get("city")
            or fournisseur_data.get("ville")
        )

        pays = self.normalize_text(
            fournisseur_data.get("country")
            or fournisseur_data.get("pays")
        )

        telephone = self.normalize_phone(
            fournisseur_data.get("phone")
            or fournisseur_data.get("telephone")
        )

        fax = self.normalize_text(
            fournisseur_data.get("fax")
        )

        email = self.normalize_text(
            fournisseur_data.get("email")
        )

        site_web = self.normalize_text(
            fournisseur_data.get("website")
            or fournisseur_data.get("site_web")
        )

        ice = self.normalize_text(
            fournisseur_data.get("ice")
        )

        identifiant_fiscal = self.normalize_text(
            fournisseur_data.get("if")
            or fournisseur_data.get(
                "identifiant_fiscal"
            )
        )

        rc = self.normalize_text(
            fournisseur_data.get("rc")
        )

        patente = self.normalize_text(
            fournisseur_data.get("patente")
        )

        cnss = self.normalize_text(
            fournisseur_data.get("cnss")
        )

        rib = self.normalize_text(
            fournisseur_data.get("rib")
        )

        # ------------------------------------------------------
        # Nom obligatoire
        # ------------------------------------------------------

        if not nom:

            print(
                "[FOURNISSEUR] Impossible de créer : "
                "nom fournisseur absent."
            )

            return None

        # ------------------------------------------------------
        # Création
        # ------------------------------------------------------

        fournisseur = Fournisseur(

            nom=nom,

            adresse=adresse,

            ville=ville,

            pays=pays,

            telephone=telephone,

            fax=fax,

            email=email,

            site_web=site_web,

            ice=ice,

            identifiant_fiscal=identifiant_fiscal,

            rc=rc,

            patente=patente,

            cnss=cnss,

            rib=rib
        )

        self.db.add(
            fournisseur
        )

        self.db.flush()

        print(
            "[FOURNISSEUR] Nouveau fournisseur créé."
        )

        print(
            "[FOURNISSEUR] ID :",
            fournisseur.id
        )

        print(
            "[FOURNISSEUR] NOM :",
            fournisseur.nom
        )

        return fournisseur

    # ==========================================================
    # RECHERCHE ARTICLE STOCK
    # ==========================================================

    def find_stock_article(
        self,
        reference=None,
        designation=None
    ):

        reference = self.normalize_text(
            reference
        )

        designation = self.normalize_text(
            designation
        )

        # ------------------------------------------------------
        # 1. Référence
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
        # 2. Désignation
        # ------------------------------------------------------

        if designation:

            article = (
                self.db.query(Stock)
                .filter(
                    Stock.nom_piece.ilike(
                        designation
                    )
                )
                .first()
            )

            if article:
                return article

        return None

    # ==========================================================
    # CREER / AUGMENTER STOCK
    # ==========================================================

    def update_stock(
        self,
        article_data,
        fournisseur=None
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

        if quantite is None:
            quantite = Decimal("0")

        # ------------------------------------------------------
        # Recherche
        # ------------------------------------------------------

        stock_article = self.find_stock_article(
            reference=reference,
            designation=designation
        )

        # ======================================================
        # ARTICLE EXISTANT
        # ======================================================

        if stock_article:

            ancienne_quantite = (
                self.to_decimal(
                    stock_article.quantite
                )
                or Decimal("0")
            )

            nouvelle_quantite = (
                ancienne_quantite
                + quantite
            )

            stock_article.quantite = (
                nouvelle_quantite
            )

            # Mettre à jour le prix si disponible
            if prix_unitaire is not None:

                stock_article.prix_unitaire = (
                    prix_unitaire
                )

            # Fournisseur si vide
            if (
                fournisseur
                and not stock_article.fournisseur
            ):

                stock_article.fournisseur = (
                    fournisseur.nom
                )

            print(
                "[STOCK] Article existant :",
                reference
            )

            print(
                "[STOCK] Ancienne quantité :",
                ancienne_quantite
            )

            print(
                "[STOCK] Quantité ajoutée :",
                quantite
            )

            print(
                "[STOCK] Nouvelle quantité :",
                nouvelle_quantite
            )

            return stock_article

        # ======================================================
        # NOUVEL ARTICLE
        # ======================================================

        stock_article = Stock(

            nom_piece=(
                designation
                or reference
                or "Article sans désignation"
            ),

            reference=reference,

            categorie=None,

            quantite=quantite,

            seuil_min=5,

            prix_unitaire=prix_unitaire,

            fournisseur=(
                fournisseur.nom
                if fournisseur
                else None
            )
        )

        self.db.add(
            stock_article
        )

        self.db.flush()

        print(
            "[STOCK] Nouvel article :",
            designation
        )

        print(
            "[STOCK] Quantité initiale :",
            quantite
        )

        print(
            "[STOCK] Stock ID :",
            stock_article.id
        )

        return stock_article

    # ==========================================================
    # CREATION LIGNE FACTURE
    # ==========================================================

    def create_facture_ligne(
        self,
        facture,
        article_data,
        fournisseur=None
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
        # STOCK
        # ------------------------------------------------------

        stock_article = self.update_stock(
            article_data,
            fournisseur=fournisseur
        )

        # ------------------------------------------------------
        # LIGNE FACTURE
        # ------------------------------------------------------

        ligne = FactureLigne(

            facture_id=facture.id,

            stock_id=stock_article.id,

            designation=designation,

            reference=reference,

            quantite=quantite,

            prix_unitaire=prix_unitaire,

            total=total
        )

        self.db.add(
            ligne
        )

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

        if not isinstance(
            facture_data,
            dict
        ):

            raise ValueError(
                "Les données de facture sont invalides."
            )

        # ======================================================
        # FOURNISSEUR
        # ======================================================

        fournisseur = self.create_fournisseur(
            facture_data.get(
                "fournisseur"
            )
        )

        # ======================================================
        # DATE
        # ======================================================

        date_facture = self.parse_date(
            facture_data.get("date")
        )

        # ======================================================
        # FACTURE
        # ======================================================

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

        self.db.add(
            facture
        )

        self.db.flush()

        print()
        print("=" * 80)
        print("ENREGISTREMENT FACTURE")
        print("=" * 80)

        print(
            "[FACTURE] ID temporaire :",
            facture.id
        )

        print(
            "[FACTURE] Fournisseur ID :",
            facture.fournisseur_id
        )

        # ======================================================
        # LIGNES
        # ======================================================

        articles = facture_data.get(
            "articles",
            []
        )

        for index, article_data in enumerate(
            articles,
            start=1
        ):

            print()
            print(
                f"[LIGNE {index}]"
            )

            print(
                "  Référence :",
                article_data.get(
                    "reference"
                )
            )

            print(
                "  Désignation :",
                article_data.get(
                    "designation"
                )
            )

            print(
                "  Quantité :",
                article_data.get(
                    "quantite"
                )
            )

            self.create_facture_ligne(
                facture=facture,

                article_data=article_data,

                fournisseur=fournisseur
            )

        # ======================================================
        # COMMIT
        # ======================================================

        self.db.commit()

        self.db.refresh(
            facture
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
            "NUMERO :",
            facture.numero
        )

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

            return self.create_facture(

                facture_data=facture_data,

                texte_ocr=texte_ocr,

                chemin_document=chemin_document
            )

        except Exception:

            self.db.rollback()

            raise
        