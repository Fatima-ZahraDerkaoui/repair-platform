from pathlib import Path

import cv2
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

    # ==========================================================
    # SAVE IMAGE
    # ==========================================================

    def save_temp_image(self, image):

        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        path = temp_dir / "preprocessed.png"

        success = cv2.imwrite(
            str(path),
            image
        )

        if not success:
            raise ValueError(
                f"Impossible de sauvegarder l'image temporaire : {path}"
            )

        return str(path)

    # ==========================================================
    # PREPARE IMAGE
    # ==========================================================

    def prepare_image(self, image_path):

        image = self.preprocessor.preprocess(
            image_path
        )

        return self.save_temp_image(
            image
        )

    # ==========================================================
    # OCR RAW
    # ==========================================================

    def run_ocr(self, image_path):

        resultats = self.ocr.predict(
            image_path
        )

        return resultats

    # ==========================================================
    # NORMALIZE BOX
    # ==========================================================

    def normalize_box(self, points):

        xs = [
            p[0]
            for p in points
        ]

        ys = [
            p[1]
            for p in points
        ]

        return [
            int(min(xs)),
            int(min(ys)),
            int(max(xs)),
            int(max(ys))
        ]

    # ==========================================================
    # PARSE OCR RESULT
    # ==========================================================

    def parse_resultats(self, resultats):

        elements = []

        for resultat in resultats:

            data = resultat.json

            if not isinstance(data, dict):
                continue

            res = data.get(
                "res",
                data
            )

            textes = res.get(
                "rec_texts",
                []
            )

            scores = res.get(
                "rec_scores",
                []
            )

            boxes = res.get(
                "rec_polys",
                []
            )

            for texte, score, box in zip(
                textes,
                scores,
                boxes
            ):

                texte = str(
                    texte
                ).strip()

                if not texte:
                    continue

                normalized_box = self.normalize_box(
                    box
                )

                elements.append({

                    "text": texte,

                    "score": float(
                        score
                    ),

                    "box": normalized_box
                })

        return elements

    # ==========================================================
    # EXTRAIRE ELEMENTS
    # ==========================================================

    def extraire_texte(
        self,
        image_path: str
    ):

        prepared_path = self.prepare_image(
            image_path
        )

        resultats = self.run_ocr(
            prepared_path
        )

        return self.parse_resultats(
            resultats
        )

    # ==========================================================
    # TEXTE COMPLET
    # ==========================================================

    def texte_complet(
        self,
        image_path: str
    ):

        elements = self.extraire_texte(
            image_path
        )

        lignes = [
            element["text"]
            for element in elements
            if element.get("text")
        ]

        return "\n".join(
            lignes
        )

    # ==========================================================
    # BLOCS
    # ==========================================================

    def extraire_blocs(
        self,
        image_path
    ):

        elements = self.extraire_texte(
            image_path
        )

        blocs = []

        for element in elements:

            box = element["box"]

            blocs.append({

                "text": element["text"],

                "score": element["score"],

                "x1": box[0],
                "y1": box[1],
                "x2": box[2],
                "y2": box[3]
            })

        return blocs