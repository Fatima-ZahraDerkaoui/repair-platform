from pathlib import Path

from app.services.ocr.document_detector import DocumentDetector
from app.services.ocr.image_preprocessor import ImagePreprocessor
from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.document_classifier import DocumentClassifier
from app.services.ocr.facture_parser import FactureParser


class OCRPipeline:

    def __init__(self):

        self.detector = DocumentDetector()

        self.preprocessor = ImagePreprocessor()

        self.engine = OCREngine()

        self.classifier = DocumentClassifier()

        self.facture = FactureParser()

    def process(self, image_path: str):

        image_path = Path(image_path)

        # 1
        detected = self.detector.detect(image_path)

        # 2
        clean = self.preprocessor.process(detected)

        # 3
        words = self.engine.extract(clean)

        # 4
        document_type = self.classifier.classify(words)

        if document_type != "FACTURE":

            return {

                "success": False,

                "message": "Document non supporté.",

                "type": document_type

            }

        # 5

        result = self.facture.parse(words)

        return {

            "success": True,

            "type": document_type,

            "data": result

        }


pipeline = OCRPipeline()