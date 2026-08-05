from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.invoice_detector import InvoiceDetector


ocr = OCREngine()

elements = ocr.extraire_texte(
    "test_data/BL Facture.jpeg"
)

detector = InvoiceDetector()

zone = detector.detect(elements)

print()
print("=" * 70)
print(zone)
print("=" * 70)

print()

print("Header Y :", zone["header_y"])
print("Footer Y :", zone["footer_y"])

print()

table = detector.extract_table_elements(elements)

print("=" * 70)
print("ELEMENTS DU TABLEAU :", len(table))
print("=" * 70)

for e in table:
    print(e["text"])