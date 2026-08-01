from app.services.ocr.pipeline import pipeline

result = pipeline.process("test_data/BL Facture.jpeg")

print("\n================ OCR =================\n")

print(result["texte"])

print("\n================ LIGNES =================\n")

for ligne in result["lignes"]:

    print("--------------------------------")

    for cellule in ligne:

        print(cellule["text"], end=" | ")

    print()

print("\n================ DONNEES =================")

print(result["data"])