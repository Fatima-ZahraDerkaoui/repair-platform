from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier
from app.services.ocr.line_builder import LineBuilder
from app.services.ocr.article_parser import ArticleParser
from app.services.ocr.facture_parser import FactureParser
from app.services.ocr.invoice_detector import InvoiceDetector
from app.services.ocr.supplier_extractor import SupplierExtractor
from app.services.ocr.invoice_validator import InvoiceValidator


class InvoiceExtractor:

    def __init__(self):

        # ==================================================
        # SERVICES OCR
        # ==================================================

        self.ocr = OCREngine()

        self.invoice_detector = InvoiceDetector()

        self.column_detector = ColumnDetector()

        self.column_classifier = None

        self.line_builder = LineBuilder()

        self.article_parser = ArticleParser()

        self.facture_parser = FactureParser()

        self.supplier_extractor = SupplierExtractor()

        self.validator = InvoiceValidator()

    # ==================================================
    # EXTRACTION COMPLETE
    # ==================================================

    def extract(self, elements):

        """
        Pipeline complet d'extraction d'une facture.

        Entrée :
            elements = éléments OCR déjà détectés.

        Sortie :
            dictionnaire facture complet.
        """

        # ==================================================
        # 0. SECURITE
        # ==================================================

        if not elements:

            facture = {
                "numero": None,
                "date": None,
                "client": None,
                "fournisseur": None,
                "articles": [],
                "total_ht": None,
                "total_tva": None,
                "total_ttc": None,
            }

            facture["supplier"] = None

            facture["validation"] = {
                "score": 0,
                "required": ["aucun élément OCR"],
                "amounts": [],
                "references": [],
                "tva": [],
                "designation": [],
                "quantity": [],
                "price": [],
                "articles": [],
                "invoice_totals": [],
                "line_totals": [],
            }

            return facture

        # ==================================================
        # 1. DETECTION DES COLONNES
        # ==================================================

        columns = self.column_detector.detect(
            elements
        )

        if columns is None:

            columns = {}

        # ==================================================
        # 2. CLASSIFICATION DES ELEMENTS
        # ==================================================

        self.column_classifier = ColumnClassifier(
            columns
        )

        classified = self.column_classifier.classify(
            elements
        )

        # ==================================================
        # 3. CONSTRUCTION DES LIGNES
        # ==================================================

        grouped_articles = self.line_builder.build(
            classified
        )

        # ==================================================
        # DEBUG TEMPORAIRE
        # ==================================================

        print()
        print("=" * 80)
        print("DEBUG GROUPED ARTICLES")
        print("=" * 80)

        for i, group in enumerate(
            grouped_articles,
            start=1
        ):

            print()
            print(f"GROUP {i}")

            print(
                "reference :",
                group.get("reference")
            )

            print(
                "reference_y :",
                group.get("reference_y")
            )

            for element in group.get(
                "elements",
                []
            ):

                print(
                    f"  {element.get('text')!r} "
                    f"| column={element.get('column')} "
                    f"| x={element.get('x')} "
                    f"| y={element.get('y')}"
                )

        # ==================================================
        # 4. ARTICLE PARSER
        # ==================================================

        articles = self.article_parser.parse(
            grouped_articles
        )

        if articles is None:

            articles = []

        # ==================================================
        # 5. TEXTE COMPLET OCR
        # ==================================================

        sorted_elements = sorted(
            elements,
            key=lambda e: (
                e.get(
                    "box",
                    [0, 0, 0, 0]
                )[1],

                e.get(
                    "box",
                    [0, 0, 0, 0]
                )[0]
            )
        )

        texte_complet = "\n".join(
            str(
                e.get(
                    "text",
                    ""
                )
            ).strip()

            for e in sorted_elements

            if str(
                e.get(
                    "text",
                    ""
                )
            ).strip()
        )

        # ==================================================
        # 6. FACTURE PARSER
        # ==================================================

        facture = self.facture_parser.parse(
            texte_complet,
            articles
        )

        if facture is None:

            facture = {}

        # ==================================================
        # 7. GARANTIR LA STRUCTURE
        # ==================================================

        facture.setdefault(
            "numero",
            None
        )

        facture.setdefault(
            "date",
            None
        )

        facture.setdefault(
            "client",
            None
        )

        facture.setdefault(
            "fournisseur",
            None
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

        # ==================================================
        # 8. SECURISER LES ARTICLES
        # ==================================================

        if not facture.get("articles"):

            facture["articles"] = articles

        # ==================================================
        # 9. COMPATIBILITE VALIDATOR
        # ==================================================

        # FactureParser utilise "fournisseur".
        #
        # InvoiceValidator utilise "supplier".
        #
        # On conserve les deux pour le moment afin
        # de ne casser aucun composant existant.

        if "supplier" not in facture:

            facture["supplier"] = facture.get(
                "fournisseur"
            )

        # ==================================================
        # 10. VALIDATION
        # ==================================================

        validation = self.validator.validate(
            facture
        )

        # ==================================================
        # 11. RESULTAT FINAL
        # ==================================================

        facture["validation"] = validation

        return facture
    