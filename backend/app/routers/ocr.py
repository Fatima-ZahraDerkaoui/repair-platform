from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid

from app.services.ocr_service import traiter_document

router = APIRouter(
    prefix="/ocr",
    tags=["OCR"]
)

DOSSIER_DOCUMENTS = Path("uploads/documents")

DOSSIER_DOCUMENTS.mkdir(
    parents=True,
    exist_ok=True
)


@router.post("/analyser")
async def analyser_document(
    fichier: UploadFile = File(...)
):

    extensions_autorisees = [
        ".jpg",
        ".jpeg",
        ".png",
        ".pdf"
    ]

    extension = Path(
        fichier.filename
    ).suffix.lower()

    if extension not in extensions_autorisees:

        raise HTTPException(
            status_code=400,
            detail="Format non supporté"
        )

    nom_fichier = (
        f"{uuid.uuid4()}"
        f"{extension}"
    )

    chemin = (
        DOSSIER_DOCUMENTS
        /
        nom_fichier
    )

    contenu = await fichier.read()

    with open(chemin, "wb") as f:

        f.write(contenu)

    try:

        resultat = traiter_document(
            str(chemin)
        )

        return {

            "message":
            "Document analysé avec succès",

            "fichier":
            nom_fichier,

            "resultat":
            resultat

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )