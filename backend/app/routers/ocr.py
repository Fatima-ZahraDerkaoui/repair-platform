from fastapi import APIRouter, UploadFile, File
import tempfile
import os

from app.ocr.engine import OCREngine
from app.ocr.parser import RepairParser


router = APIRouter(
    prefix="/ocr",
    tags=["OCR"]
)


ocr_engine = OCREngine()


@router.post("/repair")
async def process_repair_form(
    file: UploadFile = File(...)
):

    # 1. Lire l'image envoyée
    content = await file.read()

    print("Nom fichier :", file.filename)
    print("Taille image :", len(content), "bytes")

    # 2. Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png"
    ) as temp_file:

        temp_file.write(content)

        image_path = temp_file.name

    try:

        # 3. OCR
        texts = ocr_engine.extract_text(
            image_path
        )

        print("\n===== TEXTES OCR DANS API =====")

        for text in texts:

            print(text)

        # 4. Parser
        parser = RepairParser()

        data = parser.parse(texts)

        print("\n===== DONNEES STRUCTUREES =====")

        print(data)

        return {
            "success": True,
            "data": data
        }

    finally:

        # Supprimer le fichier temporaire
        if os.path.exists(image_path):

            os.remove(image_path)