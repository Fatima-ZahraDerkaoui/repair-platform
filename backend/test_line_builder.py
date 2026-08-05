from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.invoice_detector import InvoiceDetector
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier
from app.services.ocr.line_builder import LineBuilder


# ==========================================================
# OCR
# ==========================================================

ocr = OCREngine()

elements = ocr.extraire_texte(
    "test_data/BL Facture.jpeg"
)

# ==========================================================
# Détection du tableau
# ==========================================================

invoice = InvoiceDetector()

table = invoice.extract_table_elements(elements)

print()
print("=" * 60)
print("TABLE")
print("=" * 60)

print(f"Nombre d'éléments : {len(table)}")

# ==========================================================
# Colonnes
# ==========================================================

detector = ColumnDetector()

colonnes = detector.detect(table)

print()
print("=" * 60)
print("COLONNES")
print("=" * 60)

for k, v in colonnes.items():
    print(f"{k:12} : {v}")

# ==========================================================
# Classification
# ==========================================================

classifier = ColumnClassifier(colonnes)

classified = classifier.classify(table)

# ==========================================================
# Construction des lignes
# ==========================================================

builder = LineBuilder()

lignes = builder.build(classified)

# ==========================================================
# Résultat
# ==========================================================

print()
print("=" * 80)
print("ARTICLES RECONSTRUITS")
print("=" * 80)

for i, ligne in enumerate(lignes, start=1):

    print()
    print(f"ARTICLE {i}")
    print("-" * 80)

    for cellule in ligne:

        print(
            f"{cellule['column']:12} : {cellule['text']}"
        )