from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.column_detector import ColumnDetector

ocr = OCREngine()

elements = ocr.extraire_texte(
    "test_data/BL Facture.jpeg"
)

detector = ColumnDetector()

colonnes = detector.detect(elements)

print()

print("====== COLONNES ======")

for k, v in colonnes.items():

    print(k, ":", int(v))