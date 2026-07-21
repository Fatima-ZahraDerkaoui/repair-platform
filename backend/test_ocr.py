from app.ocr.engine import OCREngine
from backend.app.ocr.parser import RepairParser


image_path = "test_data/fiche_reparation.png"


# 1. OCR
ocr_engine = OCREngine()

ocr_results = ocr_engine.extract_text(
    image_path
)


# 2. Récupérer uniquement les textes
texts = [

    item["text"]

    for item in ocr_results

]


# 3. Parser
parser = RepairParser()

data = parser.parse(texts)


# 4. Affichage
print("\n===== DONNEES STRUCTUREES =====\n")


for key, value in data.items():

    print(f"{key}: {value}")