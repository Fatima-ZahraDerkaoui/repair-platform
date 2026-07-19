from paddleocr import PaddleOCR


class OCREngine:

    def __init__(self):

        self.ocr = PaddleOCR(
            lang="fr",
            enable_mkldnn=False
        )

    def extract_text(self, image_path: str):

        result = self.ocr.predict(image_path)

        texts = []

        for page in result:

            data = page.json

            if isinstance(data, str):
                continue

            if "res" not in data:
                continue

            res = data["res"]

            rec_texts = res.get("rec_texts", [])
            rec_scores = res.get("rec_scores", [])

            for text, score in zip(rec_texts, rec_scores):

                texts.append({
                    "text": text,
                    "confidence": float(score)
                })

        return texts