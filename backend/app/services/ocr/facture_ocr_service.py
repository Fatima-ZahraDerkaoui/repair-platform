from pathlib import Path

from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier
from app.services.ocr.line_builder import LineBuilder
from app.services.ocr.article_parser import ArticleParser
from app.services.ocr.facture_parser import FactureParser


class FactureOCRService:

    def __init__(self):

        self.ocr_engine = OCREngine()
        self.column_detector = ColumnDetector()
        self.article_parser = ArticleParser()
        self.facture_parser = FactureParser()

    def analyser(self, image_path):

        # =====================================================
        # 1. OCR
        # =====================================================

        elements = self.ocr_engine.extraire_texte(
            str(image_path)
        )

        if not elements:
            raise ValueError(
                "Aucun texte détecté dans la facture."
            )

        # =====================================================
        # 2. DETECTION COLONNES
        # =====================================================

        columns = self.column_detector.detect(
            elements
        )

        # =====================================================
        # 3. CLASSIFICATION
        # =====================================================

        classifier = ColumnClassifier(
            columns
        )

        classified = classifier.classify(
            elements
        )

        # =====================================================
        # 4. LINE BUILDER
        # =====================================================

        builder = LineBuilder()

        grouped_articles = builder.build(
            classified
        )

        # =====================================================
        # 5. ARTICLE PARSER
        # =====================================================

        articles = self.article_parser.parse(
            grouped_articles
        )

        # =====================================================
        # 6. TEXTE COMPLET
        # =====================================================

        texte_complet = (
            self.ocr_engine.texte_complet(
                str(image_path)
            )
        )

        # =====================================================
        # 7. FACTURE PARSER
        # =====================================================

        facture = self.facture_parser.parse(
            texte_complet,
            articles
        )

        return facture