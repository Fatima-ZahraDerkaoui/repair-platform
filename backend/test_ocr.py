from app.ocr.engine import OCREngine


image_path = "test_data/fiche2.png"


ocr_engine = OCREngine()


texts = ocr_engine.extract_text(
    image_path
)


print("\n===== TEXTE OCR =====\n")


for text in texts:

    print(text)