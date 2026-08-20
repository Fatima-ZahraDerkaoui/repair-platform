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

    # =========================================================
    # ANALYSE FACTURE
    # =========================================================

    def analyser(self, image_path):

        print()
        print("=" * 80)
        print("FACTURE OCR SERVICE")
        print("=" * 80)

        # =====================================================
        # 1. OCR — UNE SEULE FOIS
        # =====================================================

        print("[OCR] Extraction du texte...")

        elements = self.ocr_engine.extraire_texte(
            str(image_path)
        )

        if not elements:

            raise ValueError(
                "Aucun texte détecté dans la facture."
            )

        print(
            f"[OCR] {len(elements)} éléments détectés."
        )

        # =====================================================
        # 2. TEXTE COMPLET
        # =====================================================
        #
        # IMPORTANT :
        # NE PAS rappeler extraire_texte().
        #
        # On réutilise les éléments OCR déjà obtenus.
        # =====================================================

        texte_complet = "\n".join(
            element.get("text", "")
            for element in elements
            if element.get("text")
        )

        print(
            "[OCR] Texte complet construit à partir "
            "des résultats existants."
        )

        # =====================================================
        # 3. DETECTION COLONNES
        # =====================================================

        print("[COLUMN] Détection des colonnes...")

        columns = self.column_detector.detect(
            elements
        )

        # =====================================================
        # 4. CLASSIFICATION
        # =====================================================

        print("[COLUMN] Classification...")

        classifier = ColumnClassifier(
            columns
        )

        classified = classifier.classify(
            elements
        )

        # =====================================================
        # 5. LINE BUILDER
        # =====================================================

        print("[LINE] Construction des lignes...")

        builder = LineBuilder()

        grouped_articles = builder.build(
            classified
        )

        print(
            f"[LINE] {len(grouped_articles)} "
            f"groupe(s) détecté(s)."
        )

        # =====================================================
        # 6. ARTICLE PARSER
        # =====================================================

        print("[ARTICLE] Analyse des articles...")

        articles = self.article_parser.parse(
            grouped_articles
        )

        print(
            f"[ARTICLE] {len(articles)} "
            f"article(s) final(aux)."
        )

        # =====================================================
        # 7. FACTURE PARSER
        # =====================================================

        print("[FACTURE] Extraction des informations facture...")

        facture = self.facture_parser.parse(
            texte_complet,
            articles
        )

        # =====================================================
        # FIN
        # =====================================================

        print("[FACTURE] Analyse terminée.")

        print("=" * 80)

        return facture