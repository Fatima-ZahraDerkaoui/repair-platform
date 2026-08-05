from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.supplier_extractor import SupplierExtractor

ocr = OCREngine()

elements = ocr.extraire_texte("test_data/BL Facture.jpeg")

texte = "\n".join(e["text"] for e in elements)

extractor = SupplierExtractor()

supplier = extractor.extract(texte)

print("=" * 60)
print("FOURNISSEUR")
print("=" * 60)

for k, v in supplier.items():
    print(f"{k:12} : {v}")

supplier = SupplierExtractor()

print("=" * 60)
print("PHONE")
print("=" * 60)

phones = supplier.extract_phone(texte)

for p in phones:
    print(p)