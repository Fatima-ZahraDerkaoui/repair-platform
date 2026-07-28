from app.services.ocr.ocr_engine import OCREngine

ocr = OCREngine()

resultats = ocr.extraire_texte(
    "test_data/BL Facture.jpeg"
)

print()

print("===== OCR =====")

print()

for r in resultats:

    print(r)