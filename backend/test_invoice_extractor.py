from pprint import pprint

from app.services.ocr.invoice_extractor import InvoiceExtractor


# ==========================================================
# Choisir l'image à tester
# ==========================================================

IMAGE = "test_data/BL Facture.jpeg"

# IMAGE = "test_data/avoir.jpeg"
# IMAGE = "test_data/bon de livraison.jpeg"


# ==========================================================
# Extraction
# ==========================================================

extractor = InvoiceExtractor()

result = extractor.extract(IMAGE)


# ==========================================================
# Facture
# ==========================================================

print()
print("=" * 70)
print("FACTURE")
print("=" * 70)

print("Numéro      :", result.get("numero"))
print("Date        :", result.get("date"))
print("Client      :", result.get("client"))

print()

print("Total HT    :", result.get("total_ht"))
print("Total TVA   :", result.get("total_tva"))
print("Total TTC   :", result.get("total_ttc"))


# ==========================================================
# Fournisseur
# ==========================================================

supplier = result.get("supplier", {})

print()
print("=" * 70)
print("FOURNISSEUR")
print("=" * 70)

for key, value in supplier.items():

    print(f"{key:12}: {value}")


# ==========================================================
# Articles
# ==========================================================

articles = result.get("articles", [])

print()
print("=" * 70)
print(f"ARTICLES ({len(articles)})")
print("=" * 70)

for i, article in enumerate(articles, start=1):

    print()

    print(f"ARTICLE {i}")

    print("-" * 50)

    print("Reference     :", article["reference"])

    print("Designation   :", article["designation"])

    print("Quantite      :", article["quantite"])

    print("Prix unitaire :", article["prix_unitaire"])

    print("TVA           :", article["tva"])

    print("Total         :", article["total"])


# ==========================================================
# Métadonnées
# ==========================================================

meta = result.get("meta", {})

print()
print("=" * 70)
print("META")
print("=" * 70)

for key, value in meta.items():

    print(f"{key:20}: {value}")


# ==========================================================
# JSON complet
# ==========================================================

print()
print("=" * 70)
print("JSON COMPLET")
print("=" * 70)

pprint(result, sort_dicts=False)