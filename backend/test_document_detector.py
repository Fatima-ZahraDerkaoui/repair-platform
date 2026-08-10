from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.column_detector import ColumnDetector


IMAGE = "test_data/facture2.jpeg"


ocr = OCREngine()

elements = ocr.extraire_texte(IMAGE)

print("=" * 70)
print("TEST COLUMN DETECTOR - MAFOCOPI")
print("=" * 70)

print(f"\nNombre OCR : {len(elements)}")

detector = ColumnDetector()

columns = detector.detect(elements)

print("\n" + "=" * 70)
print("COLONNES DETECTEES")
print("=" * 70)

for column, x in columns.items():
    print(f"{column:15} : {x}")

print("\n" + "=" * 70)
print("ELEMENTS OCR")
print("=" * 70)

table_elements = [
    e for e in elements
    if detector.is_table_candidate(e)
]

for i, e in enumerate(table_elements, 1):

    x = detector.center_x(e)
    y = detector.center_y(e)

    print(
        f"{i:03d} | "
        f"{e['text']:<60} | "
        f"x={x:7.1f} | "
        f"y={y:7.1f}"
    )