from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.document_classifier import DocumentClassifier
from app.services.ocr.table_builder import TableBuilder
from app.services.ocr.facture_parser import FactureParser


class OCRPipeline:

    def __init__(self):

        self.engine = OCREngine()

        self.classifier = DocumentClassifier()

        self.table_builder = TableBuilder()

        self.facture_parser = FactureParser()

    # ==========================================================
    # OCR complet
    # ==========================================================

    def process(self, image_path):

        # ------------------------------------------------------
        # OCR
        # ------------------------------------------------------

        elements = self.engine.extraire_texte(
            image_path
        )

        texte = "\n".join(

            e["text"]

            for e in elements

        )

        # ------------------------------------------------------
        # Type document
        # ------------------------------------------------------

        document = self.classifier.detecter(
            texte
        )

        # ------------------------------------------------------
        # Construction des lignes
        # ------------------------------------------------------

        lignes = self.table_builder.build(
            elements
        )

        # ------------------------------------------------------
        # Parsing
        # ------------------------------------------------------

        data = {}

        if document == "FACTURE":

            data = self.facture_parser.parse(

                texte,

                lignes

            )

        # ------------------------------------------------------
        # Résultat
        # ------------------------------------------------------

        return {

            "document": document,

            "texte": texte,

            "elements": elements,

            "lignes": lignes,

            "data": data

        }


pipeline = OCRPipeline()