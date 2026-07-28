from app.services.ocr.document_classifier import DocumentClassifier
from app.services.ocr.facture_parser import FactureParser


class DocumentManager:

    @staticmethod
    def analyser(texte):

        type_doc = DocumentClassifier.detecter(texte)

        if type_doc == "FACTURE":
            return FactureParser.parse(texte)

        return {}