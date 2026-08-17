from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import traceback

from app.services.ocr.pipeline import pipeline


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

    # =========================================================
    # 1. VERIFICATION FICHIER
    # =========================================================

    if not fichier.filename:

        raise HTTPException(
            status_code=400,
            detail="Nom de fichier manquant."
        )


    extensions_autorisees = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
        ".pdf"
    }


    extension = Path(
        fichier.filename
    ).suffix.lower()


    if extension not in extensions_autorisees:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Format non supporté : {extension}. "
                f"Formats autorisés : "
                f"{', '.join(sorted(extensions_autorisees))}"
            )
        )


    # =========================================================
    # 2. CREATION NOM FICHIER
    # =========================================================

    nom_fichier = (
        f"{uuid.uuid4()}"
        f"{extension}"
    )


    chemin = (
        DOSSIER_DOCUMENTS
        /
        nom_fichier
    )


    # =========================================================
    # 3. LECTURE FICHIER
    # =========================================================

    try:

        contenu = await fichier.read()

        if not contenu:

            raise HTTPException(
                status_code=400,
                detail="Le fichier envoyé est vide."
            )


        with open(
            chemin,
            "wb"
        ) as f:

            f.write(contenu)


    except HTTPException:

        raise


    except Exception as e:

        print()
        print("=" * 80)
        print("ERREUR SAUVEGARDE DOCUMENT")
        print("=" * 80)
        traceback.print_exc()
        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la sauvegarde : {str(e)}"
        )


    # =========================================================
    # 4. OCR
    # =========================================================

    try:

        print()
        print("=" * 80)
        print("OCR DIRECT")
        print("=" * 80)

        print(
            f"Fichier original : {fichier.filename}"
        )

        print(
            f"Fichier sauvegardé : {chemin}"
        )

        print(
            f"Extension : {extension}"
        )

        print(
            "Lancement pipeline OCR..."
        )


        resultat = pipeline.process(
            str(chemin)
        )


        print(
            "OCR terminé avec succès."
        )

        print("=" * 80)


        # =====================================================
        # 5. REPONSE
        # =====================================================

        return {

            "message":
            "Document analysé avec succès",

            "fichier":
            nom_fichier,

            "resultat":
            resultat

        }


    except Exception as e:

        print()
        print("=" * 80)
        print("ERREUR PIPELINE OCR")
        print("=" * 80)

        print(
            f"Fichier : {chemin}"
        )

        print(
            f"Erreur : {str(e)}"
        )

        traceback.print_exc()

        print("=" * 80)


        raise HTTPException(

            status_code=500,

            detail=(
                "Erreur pendant l'analyse OCR : "
                f"{str(e)}"
            )

        )