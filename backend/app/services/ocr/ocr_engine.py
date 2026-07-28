import cv2
import tempfile
from paddleocr import PaddleOCR
from app.services.ocr.image_preprocessor import ImagePreprocessor

class OCREngine:

    def __init__(self):

        self.preprocessor = ImagePreprocessor()

        self.ocr = PaddleOCR(
            lang="fr",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            enable_mkldnn=False
        )

    def extraire_texte(self, chemin_image):

        image = self.preprocessor.preprocess(
            chemin_image,
            debug=True
        )

        resultats = self.ocr.predict(
            image
        )

        donnees = []

        for resultat in resultats:

            data = resultat.json

            if isinstance(data, dict):

                res = data.get("res", data)

                textes = res.get("rec_texts", [])

                boxes = res.get("rec_boxes", [])

                for texte, box in zip(textes, boxes):

                    x1 = int(box[0])
                    y1 = int(box[1])
                    x2 = int(box[2])
                    y2 = int(box[3])

                    donnees.append(
                        {
                            "text": texte,
                            "box": [x1, y1, x2, y2]
                        }
                    )

        return donnees