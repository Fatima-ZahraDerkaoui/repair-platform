from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.facture_parser import FactureParser

ocr = OCREngine()

elements = ocr.extraire_texte("test_data/BL Facture.jpeg")
#elements = ocr.extraire_texte("test_data/avoir.jpeg")
#elements = ocr.extraire_texte("test_data/bon de livraison.jpeg")

texte = "\n".join(e["text"] for e in elements)

parser = FactureParser()

print("=" * 60)
print("NUMERO")
print("=" * 60)

print(parser.extract_invoice_number(texte))

print()
print("=" * 60)
print("DATE")
print("=" * 60)

print(parser.extract_date(texte))

print()
print("=" * 60)
print("TOTALS")
print("=" * 60)

totaux = parser.extract_totals(texte)

for k, v in totaux.items():
    print(f"{k:12} : {v}")

print()
print("=" * 60)
print("FOURNISSEUR")
print("=" * 60)

print(parser.extract_supplier(texte))

print()
print("=" * 60)
print("CLIENT")
print("=" * 60)

print(parser.extract_client(texte))

print()
print("=" * 60)
print("INFORMATIONS FISCALES")
print("=" * 60)

infos = parser.extract_tax_information(texte)

for k, v in infos.items():
    print(f"{k:10} : {v}")