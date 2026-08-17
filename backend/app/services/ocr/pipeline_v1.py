from app.services.ocr.image_preprocessor import ImagePreprocessor
from app.services.ocr.ocr_engine import OCREngine

from app.services.ocr.invoice_detector import InvoiceDetector
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier
from app.services.ocr.line_builder import LineBuilder
from app.services.ocr.facture_parser import FactureParser


class OCRPipeline:

    def __init__(self):

        self.preprocessor = ImagePreprocessor()

        self.engine = OCREngine()

        self.invoice_detector = InvoiceDetector()

        self.column_detector = ColumnDetector()

        self.line_builder = LineBuilder()

        self.facture_parser = FactureParser()

    # =========================================================

    def process(self, image_path):

        # -----------------------------------------------------
        # Prétraitement
        # -----------------------------------------------------

        image = self.preprocessor.preprocess(image_path)

        # -----------------------------------------------------
        # OCR
        # -----------------------------------------------------

        elements = self.engine.extraire_texte(image)
        print("=" * 80)
        print("DEBUG PIPELINE")
        print("image =", image)
        print("type(image) =", type(image))
        print("=" * 80)

        print(
            "DEBUG PIPELINE IMAGE :",
            image
        )

        print(
            "DEBUG PIPELINE TYPE :",
            type(image)
        )

        elements = self.engine.extraire_texte(
            image
        )

        texte = "\n".join(

            e["text"]

            for e in elements

        )

        # -----------------------------------------------------
        # Détection du tableau
        # -----------------------------------------------------

        table_elements = self.invoice_detector.extract_table_elements(

            elements

        )

        # -----------------------------------------------------
        # Détection des colonnes
        # -----------------------------------------------------

        colonnes = self.column_detector.detect(

            table_elements

        )

        # -----------------------------------------------------
        # Classification des mots dans les colonnes
        # -----------------------------------------------------

        classifier = ColumnClassifier(

            colonnes

        )

        classified = classifier.classify(

            table_elements

        )

        # -----------------------------------------------------
        # Construction des lignes
        # -----------------------------------------------------

        lignes = self.line_builder.build(

            classified

        )

        # -----------------------------------------------------
        # Parsing
        # -----------------------------------------------------

        data = self.facture_parser.parse(

            texte,

            lignes

        )

        # -----------------------------------------------------

        return {

            "texte": texte,

            "elements": elements,

            "table_elements": table_elements,

            "colonnes": colonnes,

            "classified": classified,

            "lignes": lignes,

            "data": data

        }


pipeline = OCRPipeline()