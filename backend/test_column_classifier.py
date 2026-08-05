from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.invoice_detector import InvoiceDetector
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier


ocr = OCREngine()

elements = ocr.extraire_texte(
    "test_data/BL Facture.jpeg"
)

invoice = InvoiceDetector()

table = invoice.extract_table_elements(elements)

print("=" * 80)
print("TABLE ELEMENTS")
print("=" * 80)

for e in table:
    print(e["text"])


# -------------------------------------------------------
# Détection des colonnes
# -------------------------------------------------------

detector = ColumnDetector()

colonnes = detector.detect(table)

print()
print("=" * 80)
print("COLONNES")
print("=" * 80)

for k, v in colonnes.items():
    print(f"{k:12} : {v:.1f}")


# -------------------------------------------------------
# Classification
# -------------------------------------------------------

classifier = ColumnClassifier(colonnes)

classified = classifier.classify(table)


print()
print("=" * 80)
print("CLASSIFICATION")
print("=" * 80)

for c in classified:

    print(
        f"{c['column']:12}"
        f"| x={c['x']:7.1f} "
        f"| y={c['y']:7.1f} "
        f"| {c['text']}"
    )

print("test 2")
from collections import Counter

counter = Counter()

for c in classified:
    counter[c["column"]] += 1

print()
print("=" * 80)
print("STATISTIQUES")
print("=" * 80)

for k, v in counter.items():
    print(f"{k:12} : {v}")

print("test 3")
print()
print("=" * 80)
print("VERIFICATION")
print("=" * 80)

for c in classified:

    txt = c["text"]

    # prix classé ailleurs
    if classifier.is_price(txt) and c["column"] not in ("pu", "total"):
        print("PRIX MAL CLASSE :", c)

    # quantité classée ailleurs
    elif classifier.is_quantity(txt) and c["column"] != "qte":
        print("QTE MAL CLASSEE :", c)

    # TVA classée ailleurs
    elif classifier.is_tva(txt) and c["column"] != "tva":
        print("TVA MAL CLASSEE :", c)

    # désignation classée ailleurs
    elif (
        classifier.is_designation(txt)
        and c["column"] != "designation"
        and not classifier.is_price(txt)
        and not classifier.is_quantity(txt)
        and not classifier.is_tva(txt)
    ):
        print("DESIGNATION MAL CLASSEE :", c)
        