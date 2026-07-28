from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.line_parser import LineParser

ocr = OCREngine()

donnees = ocr.extraire_texte("test_data/BL Facture.jpeg")

parser = LineParser()

lignes = parser.parser(donnees)

for ligne in lignes:

    print("-----------------------")
    print(ligne.reference)
    print(ligne.designation)
    print(ligne.quantite)
    print(ligne.prix_unitaire)
    print(ligne.total)