from pprint import pprint

from app.services.ocr.invoice_extractor import InvoiceExtractor
from app.services.ocr.invoice_validator import InvoiceValidator

extractor = InvoiceExtractor()

facture = extractor.extract(
    "test_data/BL Facture.jpeg"
)

validator = InvoiceValidator()

rapport = validator.validate(facture)

print("=" * 70)
print("SCORE")
print("=" * 70)
print(rapport["score"])

print()

print("=" * 70)
print("CHAMPS OBLIGATOIRES")
print("=" * 70)
pprint(rapport["required"])

print()

print("=" * 70)
print("CONTROLE DES TOTAUX")
print("=" * 70)
pprint(rapport["amounts"])

print()

print("=" * 70)
print("CONTROLE TVA")
print("=" * 70)
pprint(rapport["tva"])

print()

print("=" * 70)
print("CONTROLE REFERENCES")
print("=" * 70)
pprint(rapport["references"])

print()

print("=" * 70)
print("CONTROLE DESIGNATION")
print("=" * 70)
pprint(rapport["designation"])

print()

print("=" * 70)
print("CONTROLE QUANTITES")
print("=" * 70)
pprint(rapport["quantity"])

print()

print("=" * 70)
print("CONTROLE PRIX")
print("=" * 70)
pprint(rapport["price"])

print()

print("=" * 70)
print("CONTROLE ARTICLES")
print("=" * 70)

for article in rapport["articles"]:
    pprint(article)

print()

print("=" * 70)
print("CONTROLE TOTAUX FACTURE")
print("=" * 70)

pprint(rapport["invoice_totals"])

print()

print("=" * 70)
print("CONTROLE TOTAUX LIGNES")
print("=" * 70)

pprint(rapport["line_totals"])
