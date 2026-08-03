from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.line_builder import LineBuilder

IMAGE = "test_data/BL Facture.jpeg"

ocr = OCREngine()

elements = ocr.extraire_texte(IMAGE)

builder = LineBuilder()

lignes = builder.build(elements)

print()
print("=" * 80)
print("NOMBRE DE LIGNES :", len(lignes))
print("=" * 80)

for i, ligne in enumerate(lignes, 1):

    print()
    print(f"LIGNE {i}")
    print("-" * 80)

    for c in ligne:

        print(c["text"])