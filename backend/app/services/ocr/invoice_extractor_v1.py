from pathlib import Path
import re


from app.services.ocr.invoice_validator import InvoiceValidator
from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier
from app.services.ocr.line_builder import LineBuilder
from app.services.ocr.article_parser import ArticleParser
from app.services.ocr.facture_parser import FactureParser
from app.services.ocr.invoice_detector import InvoiceDetector
from app.services.ocr.supplier_extractor import SupplierExtractor


class InvoiceExtractor:

    def __init__(self):

        # ==========================================================
        # SERVICES EXISTANTS
        # ==========================================================

        self.ocr = OCREngine()

        self.invoice_detector = InvoiceDetector()

        self.column_detector = ColumnDetector()

        self.line_builder = LineBuilder()

        self.article_parser = ArticleParser()

        self.facture_parser = FactureParser()

        self.supplier_extractor = SupplierExtractor()

        self.validator = InvoiceValidator()

    # ==============================================================
    # NORMALISATION
    # ==============================================================

    @staticmethod
    def normalize_text(text):

        if text is None:
            return ""

        return re.sub(
            r"\s+",
            " ",
            str(text).strip()
        )

    # ==============================================================
    # POSITION X
    # ==============================================================

    @staticmethod
    def get_x(element):

        if element.get("x") is not None:
            return float(element["x"])

        box = element.get("box")

        if box and len(box) >= 4:
            return (
                float(box[0]) +
                float(box[2])
            ) / 2

        return 0.0

    # ==============================================================
    # POSITION Y
    # ==============================================================

    @staticmethod
    def get_y(element):

        if element.get("y") is not None:
            return float(element["y"])

        box = element.get("box")

        if box and len(box) >= 4:
            return (
                float(box[1]) +
                float(box[3])
            ) / 2

        return 0.0

    # ==============================================================
    # PREPARER ELEMENTS
    # ==============================================================

    def prepare_elements(self, elements):

        if not elements:
            return []

        prepared = []

        for element in elements:

            if not isinstance(element, dict):
                continue

            text = self.normalize_text(
                element.get("text", "")
            )

            if not text:
                continue

            item = element.copy()

            item["text"] = text

            item["x"] = self.get_x(item)
            item["y"] = self.get_y(item)

            prepared.append(item)

        return prepared

    # ==============================================================
    # DETECTER NUMERO FACTURE
    # ==============================================================

    def extract_invoice_number(self, elements):

        patterns = [

            r"(?:FACTURE\s*)?(?:N[°ºo]?\s*)?[:\-]?\s*"
            r"([A-Z]{0,5}[\s\-]?\d{2,4}[A-Z]?[\/\-]\d+)",

            r"(?:FACTURE\s*)?(?:N[°ºo]?\s*)?[:\-]?\s*"
            r"([A-Z0-9]+[\-\/][A-Z0-9\-\/]+)",
        ]

        # ----------------------------------------------------------
        # Priorité aux textes contenant FACTURE
        # ----------------------------------------------------------

        ordered = sorted(
            elements,
            key=lambda e: (
                0
                if "FACTURE" in
                self.normalize_text(
                    e.get("text", "")
                ).upper()
                else 1,
                self.get_y(e)
            )
        )

        for element in ordered:

            text = self.normalize_text(
                element.get("text", "")
            )

            upper = text.upper()

            for pattern in patterns:

                match = re.search(
                    pattern,
                    upper,
                    flags=re.IGNORECASE
                )

                if match:

                    value = match.group(1).strip()

                    value = re.sub(
                        r"\s+",
                        " ",
                        value
                    )

                    return value

        return None

    # ==============================================================
    # DETECTER DATE
    # ==============================================================

    def extract_invoice_date(self, elements):

        date_patterns = [

            r"\b\d{2}/\d{2}/\d{4}\b",

            r"\b\d{2}-\d{2}-\d{4}\b",

            r"\b\d{4}/\d{2}/\d{2}\b",

            r"\b\d{4}-\d{2}-\d{2}\b",
        ]

        ordered = sorted(
            elements,
            key=lambda e: self.get_y(e)
        )

        for element in ordered:

            text = self.normalize_text(
                element.get("text", "")
            )

            for pattern in date_patterns:

                match = re.search(
                    pattern,
                    text
                )

                if match:
                    return match.group(0)

        return None

    # ==============================================================
    # TEXTE COMPLET
    # ==============================================================

    def build_full_text(self, elements):

        ordered = sorted(
            elements,
            key=lambda e: (
                self.get_y(e),
                self.get_x(e)
            )
        )

        return "\n".join(
            self.normalize_text(
                e.get("text", "")
            )
            for e in ordered
            if self.normalize_text(
                e.get("text", "")
            )
        )

    # ==============================================================
    # CLASSIFICATION
    # ==============================================================

    def classify_elements(self, elements):

        # ----------------------------------------------------------
        # Si les éléments possèdent déjà une colonne,
        # on ne recommence pas la classification.
        # ----------------------------------------------------------

        already_classified = any(
            element.get("column")
            for element in elements
        )

        if already_classified:
            return elements

        # ----------------------------------------------------------
        # Détection colonnes
        # ----------------------------------------------------------

        try:

            columns = self.column_detector.detect(
                elements
            )

        except Exception:

            columns = {}

        # ----------------------------------------------------------
        # Classification
        # ----------------------------------------------------------

        if columns:

            try:

                classifier = ColumnClassifier(
                    columns
                )

                classified = classifier.classify(
                    elements
                )

                if classified:
                    return classified

            except Exception:

                pass

        # ----------------------------------------------------------
        # FALLBACK
        #
        # Utilisé principalement par le test simulé.
        # ----------------------------------------------------------

        return self.fallback_classification(
            elements
        )

    # ==============================================================
    # CLASSIFICATION FALLBACK
    # ==============================================================

    def fallback_classification(self, elements):

        result = []

        # ----------------------------------------------------------
        # Recherche des headers
        # ----------------------------------------------------------

        headers = {}

        for element in elements:

            text = self.normalize_text(
                element.get("text", "")
            ).upper()

            if text in (
                "DESIGNATION",
                "DÉSIGNATION"
            ):
                headers["designation"] = self.get_x(
                    element
                )

            elif text in (
                "REFERENCE",
                "RÉFÉRENCE",
                "REF"
            ):
                headers["reference"] = self.get_x(
                    element
                )

            elif text in (
                "QTE",
                "QTÉ",
                "QUANTITE",
                "QUANTITÉ"
            ):
                headers["qte"] = self.get_x(
                    element
                )

            elif text in (
                "PU",
                "P.U",
                "P.U."
            ):
                headers["pu"] = self.get_x(
                    element
                )

            elif text in (
                "TOTAL",
                "TOTAL TTC",
                "MONTANT"
            ):
                headers["total"] = self.get_x(
                    element
                )

        # ----------------------------------------------------------
        # Si aucun header, retourner tel quel
        # ----------------------------------------------------------

        if not headers:

            return elements

        # ----------------------------------------------------------
        # Trier colonnes
        # ----------------------------------------------------------

        ordered_columns = sorted(
            headers.items(),
            key=lambda item: item[1]
        )

        # ----------------------------------------------------------
        # Classification par proximité X
        # ----------------------------------------------------------

        for element in elements:

            text = self.normalize_text(
                element.get("text", "")
            )

            upper = text.upper()

            # Headers
            if upper in (
                "DESIGNATION",
                "DÉSIGNATION",
                "REFERENCE",
                "RÉFÉRENCE",
                "REF",
                "QTE",
                "QTÉ",
                "QUANTITE",
                "QUANTITÉ",
                "PU",
                "P.U",
                "P.U.",
                "TOTAL",
                "TOTAL TTC",
                "MONTANT"
            ):
                continue

            x = self.get_x(element)

            # ------------------------------------------------------
            # Choisir colonne la plus proche
            # ------------------------------------------------------

            best_column = None
            best_distance = float("inf")

            for column, column_x in ordered_columns:

                distance = abs(
                    x - column_x
                )

                if distance < best_distance:

                    best_distance = distance
                    best_column = column

            item = element.copy()

            item["column"] = (
                best_column
                if best_column
                else "designation"
            )

            result.append(item)

        return result

    # ==============================================================
    # EXTRACTION DES ARTICLES
    # ==============================================================
    def extract_articles(self, classified):

        if not classified:
            return []

        grouped = self.line_builder.build(
            classified
        )

        if not grouped:
            return []

        # ==========================================================
        # DEBUG ARTICLE PARSER
        # ==========================================================

        print("\n")
        print("=" * 80)
        print("DEBUG AVANT ARTICLE PARSER")
        print("=" * 80)

        for i, article in enumerate(grouped, start=1):

            print(f"\nARTICLE {i}")
            print("REFERENCE :", article.get("reference"))

            for element in article.get("elements", []):

                print(
                    f"  column={element.get('column'):15} "
                    f"x={element.get('x'):7.1f} "
                    f"y={element.get('y'):7.1f} "
                    f"text={element.get('text')}"
                )

        print("=" * 80)

        # ==========================================================
        # ARTICLE PARSER
        # ==========================================================

        try:

            articles = self.article_parser.parse(
                grouped
            )

        except Exception as e:

            print("\n❌ ERREUR ARTICLE PARSER")
            print(type(e).__name__)
            print(e)

            articles = []

        # ==========================================================
        # DEBUG APRES ARTICLE PARSER
        # ==========================================================

        print("\n")
        print("=" * 80)
        print("DEBUG APRES ARTICLE PARSER")
        print("=" * 80)

        for i, article in enumerate(articles or [], start=1):

            print(f"\nARTICLE {i}")
            print("REFERENCE   :", article.get("reference"))
            print("DESIGNATION :", repr(article.get("designation")))
            print("QUANTITE    :", article.get("quantite"))
            print("PU          :", article.get("prix_unitaire"))
            print("TVA         :", article.get("tva"))
            print("TOTAL       :", article.get("total"))

        print("=" * 80)

        return articles or []

    # ==============================================================
    # NETTOYER NOM FOURNISSEUR
    # ==============================================================

    @staticmethod
    def clean_supplier_name(name):

        if not name:
            return None

        name = str(name).strip()

        # Supprimer les préfixes OCR classiques
        name = re.sub(
            r"^\s*(FOURNISSEUR|FOURNISSEUR\s*:)\s*",
            "",
            name,
            flags=re.IGNORECASE
        )

        name = re.sub(
            r"^\s*NOM\s*(DU)?\s*FOURNISSEUR\s*:?\s*",
            "",
            name,
            flags=re.IGNORECASE
        )

        return name.strip() or None
    
    # ==============================================================
    # EXTRACTION FOURNISSEUR
    # ==============================================================

    def extract_supplier(
        self,
        elements,
        full_text
    ):

        # ----------------------------------------------------------
        # SupplierExtractor
        # ----------------------------------------------------------

        try:

            supplier = self.supplier_extractor.extract(
                full_text
            )

            if supplier:

                return supplier

        except Exception as e:

            print(
                "\n========== DEBUG SUPPLIER ERROR =========="
            )

            print(
                type(e).__name__
            )

            print(
                e
            )

            print(
                "==========================================\n"
            )

        # ----------------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------------

        supplier = {
            "name": None,
            "address": None,
            "city": None,
            "country": "Maroc",
            "phone": [],
            "fax": None,
            "email": None,
            "website": None,
            "ice": None,
            "if": None,
            "rc": None,
            "patente": None,
            "cnss": None,
            "rib": None,
        }

        return supplier
    
    # ==============================================================
    # NORMALISER ARTICLES
    # ==============================================================

    def normalize_articles(self, articles):

        normalized = []

        for article in articles:

            if not isinstance(
                article,
                dict
            ):
                continue

            item = {
                "reference":
                    article.get(
                        "reference"
                    ),

                "designation":
                    article.get(
                        "designation"
                    ),

                "quantite":
                    article.get(
                        "quantite"
                    ),

                "prix_unitaire":
                    article.get(
                        "prix_unitaire"
                    ),

                "tva":
                    article.get(
                        "tva"
                    ),

                "total":
                    article.get(
                        "total"
                    ),
            }

            normalized.append(
                item
            )

        return normalized

    # ==============================================================
    # PARSER FACTURE
    # ==============================================================

    def parse_invoice(
        self,
        full_text,
        articles
    ):

        try:

            result = self.facture_parser.parse(
                full_text,
                articles
            )

            if result:
                return result

        except Exception:

            pass

        # ----------------------------------------------------------
        # Fallback
        # ----------------------------------------------------------

        return {
            "numero": None,
            "date": None,
            "client": None,
            "fournisseur": None,
            "articles": articles,
            "total_ht": None,
            "total_tva": None,
            "total_ttc": None,
        }

    # ==============================================================
    # VALIDATION
    # ==============================================================

    def validate_result(self, result):

        if not result:
            return {}

        try:

            validation = self.validator.validate(
                result
            )

            if validation is not None:
                return validation

        except Exception:

            pass

        return {}

    # ==============================================================
    # EXTRACTION PRINCIPALE
    # ==============================================================

    def extract(self, source):

        # ==========================================================
        # SOURCE = IMAGE
        # ==========================================================

        if isinstance(
            source,
            (str, Path)
        ):

            image_path = str(
                source
            )

            elements = (
                self.ocr.extraire_texte(
                    image_path
                )
            )

        # ==========================================================
        # SOURCE = ELEMENTS OCR
        # ==========================================================

        elif isinstance(
            source,
            list
        ):

            elements = source

        else:

            raise TypeError(
                "InvoiceExtractor.extract() "
                "attend une liste d'elements OCR "
                "ou un chemin d'image."
            )

        # ==========================================================
        # PREPARATION
        # ==========================================================

        elements = self.prepare_elements(
            elements
        )

        if not elements:

            raise ValueError(
                "Aucun élément OCR disponible."
            )

        # ==========================================================
        # CLASSIFICATION
        # ==========================================================

        classified = self.classify_elements(
            elements
        )

        # ==========================================================
        # ARTICLES
        # ==========================================================

        articles = self.extract_articles(
            classified
        )

        articles = self.normalize_articles(
            articles
        )

        # ==========================================================
        # TEXTE COMPLET
        # ==========================================================

        full_text = self.build_full_text(
            elements
        )

        # ==========================================================
        # PARSER FACTURE
        # ==========================================================

        facture = self.parse_invoice(
            full_text,
            articles
        )

        # ==========================================================
        # INFOS FACTURE FALLBACK
        # ==========================================================

        numero = self.extract_invoice_number(
            elements
        )

        date = self.extract_invoice_date(
            elements
        )

        if not facture.get("numero"):
            facture["numero"] = numero

        if not facture.get("date"):
            facture["date"] = date

        # ==========================================================
        # FOURNISSEUR
        # ==========================================================

        supplier = self.extract_supplier(
            elements,
            full_text
        )

        if not facture.get(
            "fournisseur"
        ):
            facture["fournisseur"] = supplier

        # ==========================================================
        # STRUCTURE OBLIGATOIRE
        # ==========================================================

        facture.setdefault(
            "numero",
            numero
        )

        facture.setdefault(
            "date",
            date
        )

        facture.setdefault(
            "client",
            None
        )

        facture.setdefault(
            "fournisseur",
            supplier
        )

        facture.setdefault(
            "articles",
            articles
        )

        facture.setdefault(
            "total_ht",
            None
        )

        facture.setdefault(
            "total_tva",
            None
        )

        facture.setdefault(
            "total_ttc",
            None
        )

        # ==========================================================
        # VALIDATION
        # ==========================================================

        validation = self.validate_result(
            facture
        )

        if validation:
            facture["validation"] = (
                validation
            )

        # ==========================================================
        # RESULTAT
        # ==========================================================

        return facture
    