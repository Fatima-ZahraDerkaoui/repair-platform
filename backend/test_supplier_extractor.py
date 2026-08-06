from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.supplier_extractor import SupplierExtractor


ocr = OCREngine()

elements = ocr.extraire_texte(
    "test_data/BL Facture.jpeg"
)

texte = "\n".join(e["text"] for e in elements)

extractor = SupplierExtractor()

supplier = extractor.extract(texte)

print()
print("=" * 70)
print("FOURNISSEUR")
print("=" * 70)

for key, value in supplier.items():

    print(f"{key:12}: {value}")

print()

print("=" * 70)
print("TESTS INDIVIDUELS")
print("=" * 70)

print()

print("Nom")
print("-" * 30)
print(extractor.extract_name(texte))

print()

print("Adresse")
print("-" * 30)
print(extractor.extract_address(texte))

print()

print("Ville")
print("-" * 30)
print(extractor.extract_city(texte))

print()

print("Pays")
print("-" * 30)
print(extractor.extract_country(texte))

print()

print("Téléphone")
print("-" * 30)
print(extractor.extract_phone(texte))

print()

print("Fax")
print("-" * 30)
print(extractor.extract_fax(texte))

print()

print("Email")
print("-" * 30)
print(extractor.extract_email(texte))

print()

print("Website")
print("-" * 30)
print(extractor.extract_website(texte))

print()

print("ICE")
print("-" * 30)
print(extractor.extract_ice(texte))

print()

print("IF")
print("-" * 30)
print(extractor.extract_if(texte))

print()

print("RC")
print("-" * 30)
print(extractor.extract_rc(texte))

print()

print("Patente")
print("-" * 30)
print(extractor.extract_patente(texte))

print()

print("CNSS")
print("-" * 30)
print(extractor.extract_cnss(texte))

print()

print("RIB")
print("-" * 30)
print(extractor.extract_rib(texte))