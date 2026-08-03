from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.line_builder import LineBuilder
from app.services.ocr.article_parser import ArticleParser

ocr = OCREngine()

elements = ocr.extraire_texte(
    "test_data/BL Facture.jpeg"
)

builder = LineBuilder()

lignes = builder.build(elements)

print("=" * 80)
print("ARTICLES")
print("=" * 80)

for i, ligne in enumerate(lignes, 1):

    article = ArticleParser.parse_line(ligne)

    print(f"\nARTICLE {i}")
    print("-" * 60)

    if article is None:
        print("Impossible de parser")
    else:
        for k, v in article.items():
            print(f"{k:15}: {v}")