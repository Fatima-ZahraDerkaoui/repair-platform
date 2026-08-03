from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier


ocr = OCREngine()

elements = ocr.extraire_texte(
    "test_data/BL Facture.jpeg"
)

detector = ColumnDetector()

colonnes = detector.detect(elements)

classifier = ColumnClassifier(colonnes)

resultat = classifier.classify(elements)

print()

print("========== CLASSIFICATION ==========\n")

for e in resultat:

    print(
        f"{e['column']:12} | "
        f"x={int(e['x']):4} | "
        f"{e['text']}"
    )