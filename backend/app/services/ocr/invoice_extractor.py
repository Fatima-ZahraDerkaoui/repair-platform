from app.services.ocr.ocr_engine import OCREngine

from app.services.ocr.invoice_detector import InvoiceDetector
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier
from app.services.ocr.line_builder import LineBuilder

from app.services.ocr.article_parser import ArticleParser

from app.services.ocr.facture_parser import FactureParser

from app.services.ocr.supplier_extractor import SupplierExtractor


class InvoiceExtractor:

    def __init__(self):

        self.ocr = OCREngine()

        self.invoice_detector = InvoiceDetector()

        self.column_detector = ColumnDetector()

        self.line_builder = LineBuilder()

        self.article_parser = ArticleParser()

        self.facture_parser = FactureParser()

        self.supplier_extractor = SupplierExtractor()

    # =======================================================
    # OCR
    # =======================================================

    def run_ocr(self, image_path):

        return self.ocr.extraire_texte(image_path)

    # =======================================================
    # Texte complet
    # =======================================================

    def build_text(self, elements):

        return "\n".join(

            e["text"]

            for e in elements

        )

    # =======================================================
    # Extraction du tableau
    # =======================================================

    def extract_table(self, elements):

        return self.invoice_detector.extract_table_elements(

            elements

        )

    # =======================================================
    # Détection des colonnes
    # =======================================================

    def detect_columns(self, table_elements):

        return self.column_detector.detect(

            table_elements

        )

    # =======================================================
    # Classification
    # =======================================================

    def classify(self, table_elements, colonnes):

        classifier = ColumnClassifier(colonnes)

        return classifier.classify(

            table_elements

        )

    # =======================================================
    # Reconstruction des lignes
    # =======================================================

    def build_lines(self, classified):

        return self.line_builder.build(

            classified

        )

    # =======================================================
    # Extraction des articles
    # =======================================================

    def parse_articles(self, lignes):

        return self.article_parser.parse(

            lignes

        )

    # =======================================================
    # Extraction fournisseur
    # =======================================================

    def parse_supplier(self, texte):

        return self.supplier_extractor.extract(

            texte

        )

    # =======================================================
    # Extraction facture
    # =======================================================

    def parse_invoice(self, texte, articles):

        return self.facture_parser.parse(

            texte,

            articles

        )

    # =======================================================
    # Pipeline complet
    # =======================================================

    def extract(self, image_path):

        # -----------------------------------
        # OCR
        # -----------------------------------

        elements = self.run_ocr(

            image_path

        )

        # -----------------------------------
        # Texte complet
        # -----------------------------------

        texte = self.build_text(

            elements

        )

        # -----------------------------------
        # Tableau
        # -----------------------------------

        table_elements = self.extract_table(

            elements

        )

        # -----------------------------------
        # Colonnes
        # -----------------------------------

        colonnes = self.detect_columns(

            table_elements

        )

        # -----------------------------------
        # Classification
        # -----------------------------------

        classified = self.classify(

            table_elements,

            colonnes

        )

        # -----------------------------------
        # Lignes
        # -----------------------------------

        lignes = self.build_lines(

            classified

        )

        # -----------------------------------
        # Articles
        # -----------------------------------

        articles = self.parse_articles(

            lignes

        )

        # -----------------------------------
        # Informations facture
        # -----------------------------------

        facture = self.parse_invoice(

            texte,

            articles

        )

        # -----------------------------------
        # Fournisseur
        # -----------------------------------

        fournisseur = self.parse_supplier(

            texte

        )

        facture["supplier"] = fournisseur

        # -----------------------------------
        # Informations techniques
        # -----------------------------------

        facture["meta"] = {

            "ocr_elements": len(elements),

            "table_elements": len(table_elements),

            "classified_elements": len(classified),

            "articles_detected": len(articles),

            "columns": colonnes

        }

        return facture
    