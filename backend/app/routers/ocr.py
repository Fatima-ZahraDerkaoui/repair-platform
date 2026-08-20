from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.ocr.pipeline import pipeline


router = APIRouter(
    prefix="/ocr",
    tags=["OCR"]
)


# =========================================================
# DOSSIER
# =========================================================

DOSSIER_DOCUMENTS = Path("uploads/documents")

DOSSIER_DOCUMENTS.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# EXECUTEUR OCR
# =========================================================

OCR_EXECUTOR = ThreadPoolExecutor(
    max_workers=1,
    thread_name_prefix="OCR"
)


# =========================================================
# FONCTION OCR
# =========================================================

def executer_ocr(chemin):

    print()
    print("=" * 80)
    print("OCR DIRECT")
    print("=" * 80)

    print(
        f"Fichier : {chemin}"
    )

    print(
        "Lancement pipeline OCR..."
    )

    try:

        resultat = pipeline.process(
            str(chemin)
        )

        print(
            "OCR terminé avec succès."
        )

        print("=" * 80)

        return resultat

    except Exception:

        print()
        print("=" * 80)
        print("ERREUR PIPELINE OCR")
        print("=" * 80)

        traceback.print_exc()

        print("=" * 80)

        raise


# =========================================================
# ANALYSER FACTURE
# =========================================================

@router.post("/analyser")
async def analyser_document(
    fichier: UploadFile = File(...)
):

    # =====================================================
    # 1. VERIFICATION
    # =====================================================

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


    # =====================================================
    # 2. NOM FICHIER
    # =====================================================

    nom_fichier = (
        f"{uuid.uuid4()}"
        f"{extension}"
    )


    chemin = (
        DOSSIER_DOCUMENTS
        /
        nom_fichier
    )


    # =====================================================
    # 3. SAUVEGARDE
    # =====================================================

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

            f.write(
                contenu
            )


    except HTTPException:

        raise


    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur lors de la sauvegarde : "
                f"{str(e)}"
            )
        )


    # =====================================================
    # 4. OCR DANS THREADPOOL
    # =====================================================

    try:

        loop = asyncio.get_running_loop()

        resultat = await loop.run_in_executor(
            OCR_EXECUTOR,
            executer_ocr,
            str(chemin)
        )


        # =================================================
        # 5. REPONSE
        # =================================================

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
        print("ERREUR ANALYSE OCR")
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