from pathlib import Path
import os
import cv2
import time

from paddleocr import PaddleOCR

from app.services.ocr.image_preprocessor import ImagePreprocessor


class OCREngine:

    TEMP_DIRECTORY = Path("temp")
    TEMP_IMAGE_NAME = "preprocessed.png"

    def __init__(self):

        self.preprocessor = ImagePreprocessor()

        print("=" * 80)
        print("INITIALISATION OCR ENGINE")
        print("=" * 80)

        print(
            "[CPU] Cores disponibles :",
            os.cpu_count()
        )

        try:

            self.ocr = PaddleOCR(

                # ==================================================
                # LANGUE
                # ==================================================

                lang="fr",

                # ==================================================
                # MODULES INUTILES POUR FACTURE
                # ==================================================

                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,

                # ==================================================
                # DETECTION
                # ==================================================

                text_det_limit_side_len=1400,
                text_det_limit_type="max",

                # ==================================================
                # CPU
                # ==================================================

                device="cpu",

                # IMPORTANT :
                # False = évite le crash oneDNN/PIR
                # rencontré avec PaddlePaddle 3.x
                enable_mkldnn=False,

                # Nombre de threads CPU
                cpu_threads=min(
                    os.cpu_count() or 4,
                    8
                ),
            )

        except Exception as e:

            print(
                "[ERREUR] Impossible d'initialiser PaddleOCR."
            )

            print(
                f"[ERREUR] {e}"
            )

            raise

        print("[OCR] PaddleOCR initialisé.")
        print("[OCR] Mode : CPU")
        print("[OCR] Device : cpu")
        print("[OCR] Orientation document : OFF")
        print("[OCR] Dewarping : OFF")
        print("[OCR] Orientation ligne : OFF")
        print("[OCR] MKLDNN : OFF")
        print("[OCR] CPU threads :", min(os.cpu_count() or 4, 8))
        print("[OCR] Limite détection : 1400")
        print("=" * 80)
        
    # ==========================================================
    # SAUVEGARDE IMAGE TEMPORAIRE
    # ==========================================================

    def save_temp_image(self, image):

        self.TEMP_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        image_path = (
            self.TEMP_DIRECTORY
            / self.TEMP_IMAGE_NAME
        )

        success = cv2.imwrite(
            str(image_path),
            image,
        )

        if not success:

            raise ValueError(
                "Impossible de sauvegarder l'image temporaire : "
                f"{image_path}"
            )

        return str(image_path)

    # ==========================================================
    # PREPARATION IMAGE
    # ==========================================================

    def prepare_image(self, image_path):

        start = time.perf_counter()

        image = self.preprocessor.preprocess(
            image_path
        )

        preprocessing_time = (
            time.perf_counter()
            - start
        )

        print(
            f"[TIME] ImagePreprocessor : "
            f"{preprocessing_time:.2f}s"
        )

        print(
            f"[PREPROCESS] Image finale : "
            f"{image.shape[1]}x{image.shape[0]}"
        )

        # ------------------------------------------------------
        # Sauvegarde
        # ------------------------------------------------------

        start = time.perf_counter()

        prepared_path = self.save_temp_image(
            image
        )

        save_time = (
            time.perf_counter()
            - start
        )

        print(
            f"[TIME] Sauvegarde image : "
            f"{save_time:.2f}s"
        )

        return prepared_path

    # ==========================================================
    # PADDLE OCR
    # ==========================================================

    def run_ocr(self, image_path):

        print(
            "[PADDLE OCR] Analyse de l'image..."
        )

        start = time.perf_counter()

        # ------------------------------------------------------
        # UN SEUL APPEL OCR
        # ------------------------------------------------------

        results = self.ocr.predict(
            image_path
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        print(
            "[PADDLE OCR] Analyse terminée."
        )

        print(
            f"[TIME] PaddleOCR interne : "
            f"{elapsed:.2f}s"
        )

        return results

    # ==========================================================
    # NORMALISATION BOX
    # ==========================================================

    @staticmethod
    def normalize_box(points):

        if points is None:
            return [0, 0, 0, 0]

        xs = [
            point[0]
            for point in points
        ]

        ys = [
            point[1]
            for point in points
        ]

        return [
            int(min(xs)),
            int(min(ys)),
            int(max(xs)),
            int(max(ys)),
        ]

    # ==========================================================
    # PARSING RESULTATS OCR
    # ==========================================================

    def parse_results(self, results):

        elements = []

        for result in results:

            try:
                data = result.json
            except Exception:
                continue

            if not isinstance(data, dict):
                continue

            result_data = data.get(
                "res",
                data,
            )

            if not isinstance(result_data, dict):
                continue

            texts = result_data.get(
                "rec_texts",
                [],
            )

            scores = result_data.get(
                "rec_scores",
                [],
            )

            boxes = result_data.get(
                "rec_polys",
                [],
            )

            for text, score, box in zip(
                texts,
                scores,
                boxes,
            ):

                text = str(
                    text
                ).strip()

                if not text:
                    continue

                normalized_box = (
                    self.normalize_box(
                        box
                    )
                )

                elements.append(
                    {
                        "text": text,
                        "score": float(score),
                        "box": normalized_box,
                    }
                )

        return elements

    # ==========================================================
    # EXTRACTION OCR
    # ==========================================================

    def extraire_texte(
        self,
        image_path: str
    ):

        total_start = time.perf_counter()

        # ------------------------------------------------------
        # PREPARATION
        # ------------------------------------------------------

        print(
            "[OCR] Préparation image..."
        )

        start = time.perf_counter()

        prepared_path = (
            self.prepare_image(
                image_path
            )
        )

        preparation_time = (
            time.perf_counter()
            - start
        )

        print(
            f"[TIME] Préparation image : "
            f"{preparation_time:.2f}s"
        )

        print(
            "[OCR] Image préparée :",
            prepared_path
        )

        # ------------------------------------------------------
        # OCR
        # ------------------------------------------------------

        start = time.perf_counter()

        resultats = self.run_ocr(
            prepared_path
        )

        paddle_time = (
            time.perf_counter()
            - start
        )

        print(
            f"[TIME] PaddleOCR : "
            f"{paddle_time:.2f}s"
        )

        # ------------------------------------------------------
        # PARSING
        # ------------------------------------------------------

        start = time.perf_counter()

        elements = self.parse_results(
            resultats
        )

        parsing_time = (
            time.perf_counter()
            - start
        )

        print(
            f"[TIME] Parsing OCR : "
            f"{parsing_time:.2f}s"
        )

        print(
            f"[OCR] Éléments extraits : "
            f"{len(elements)}"
        )

        # ------------------------------------------------------
        # TOTAL
        # ------------------------------------------------------

        total_time = (
            time.perf_counter()
            - total_start
        )

        print(
            f"[TIME] TOTAL OCR ENGINE : "
            f"{total_time:.2f}s"
        )

        return elements

    # ==========================================================
    # TEXTE COMPLET DEPUIS ELEMENTS
    # ==========================================================

    @staticmethod
    def texte_complet_depuis_elements(
        elements
    ):

        if not elements:
            return ""

        lines = [
            element["text"]
            for element in elements
            if element.get("text")
        ]

        return "\n".join(lines)

    # ==========================================================
    # TEXTE COMPLET DEPUIS IMAGE
    # ==========================================================

    def texte_complet(
        self,
        image_path: str
    ):

        elements = self.extraire_texte(
            image_path
        )

        return (
            self.texte_complet_depuis_elements(
                elements
            )
        )

    # ==========================================================
    # BLOCS OCR
    # ==========================================================

    def extraire_blocs(
        self,
        image_path
    ):

        elements = self.extraire_texte(
            image_path
        )

        blocks = []

        for element in elements:

            box = element["box"]

            blocks.append(
                {
                    "text": element["text"],
                    "score": element["score"],
                    "x1": box[0],
                    "y1": box[1],
                    "x2": box[2],
                    "y2": box[3],
                }
            )

        return blocks