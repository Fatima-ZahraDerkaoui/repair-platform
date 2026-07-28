from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.table_builder import TableBuilder


ocr = OCREngine()

elements = ocr.extraire_texte("test_data/BL Facture.jpeg")

builder = TableBuilder()

tableau = builder.build(elements)


for numero, ligne in enumerate(tableau, start=1):

    print("=" * 60)

    print(f"LIGNE {numero}")

    print("=" * 60)

    for cellule in ligne:

        print(cellule["text"])