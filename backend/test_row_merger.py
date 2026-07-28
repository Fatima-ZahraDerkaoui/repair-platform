from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.table_builder import TableBuilder
from app.services.ocr.row_merger import RowMerger


ocr = OCREngine()

elements = ocr.extraire_texte("test_data/BL Facture.jpeg")

builder = TableBuilder()

lignes = builder.build(elements)

merger = RowMerger()

produits = merger.merge(lignes)

for i, produit in enumerate(produits, start=1):

    print("=" * 60)

    print("PRODUIT", i)

    print("=" * 60)

    for cellule in produit:

        print(cellule["text"])