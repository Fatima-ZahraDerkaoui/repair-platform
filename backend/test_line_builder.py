from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.invoice_detector import InvoiceDetector
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier
from app.services.ocr.line_builder import LineBuilder


ocr = OCREngine()

elements = ocr.extraire_texte(
    "test_data/BL Facture.jpeg"
)

invoice = InvoiceDetector()

table = invoice.extract_table_elements(elements)

print("=" * 80)
print("TABLE ELEMENTS :", len(table))
print("=" * 80)

for e in table:
    print(e["text"])

detector = ColumnDetector()

colonnes = detector.detect(table)

classifier = ColumnClassifier(colonnes)

classified = classifier.classify(table)

builder = LineBuilder()

lignes = builder.build(classified)

print()
print("=" * 80)
print("LIGNES")
print("=" * 80)

for i, ligne in enumerate(lignes, 1):

    print()

    print(f"LIGNE {i}")

    print("-" * 50)

    for cellule in ligne:

        print(
            f"{cellule['column']:12} : {cellule['text']}"
        )