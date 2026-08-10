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

        temp = Path("temp")

        temp.mkdir(
            exist_ok=True
        )

        path = (
            temp /
            "preprocessed.png"
        )

        cv2.imwrite(
            str(path),
            image
        )

        return str(path)

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
    # OCR
    # ==========================================================

    def extraire_texte(
        self,
        image_path: str
    ):

        image = self.preprocessor.preprocess(
            image_path
        )

        image_path = self.save_temp_image(
            image
        )

        resultats = self.ocr.predict(
            image_path
        )

        elements = []

        for resultat in resultats:

            data = resultat.json

            if not isinstance(
                data,
                dict
            ):
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

                elements.append({

                    "text": texte,

                    "score": float(
                        score
                    ),

                    "box": self.normalize_box(
                        box
                    )
                })

        return elements

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
            e["text"]
            for e in elements
            if e.get("text")
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

        image = self.preprocessor.preprocess(
            image_path
        )

        image_path = self.save_temp_image(
            image
        )

        resultats = self.ocr.predict(
            image_path
        )

        blocs = []

        for resultat in resultats:

            data = resultat.json

            if not isinstance(
                data,
                dict
            ):
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

            polys = res.get(
                "rec_polys",
                []
            )

            for texte, score, poly in zip(
                textes,
                scores,
                polys
            ):

                texte = str(
                    texte
                ).strip()

                if not texte:
                    continue

                box = self.normalize_box(
                    poly
                )

                blocs.append({

                    "text": texte,

                    "score": float(
                        score
                    ),

                    "x1": box[0],
                    "y1": box[1],
                    "x2": box[2],
                    "y2": box[3]
                })

        return blocs
    