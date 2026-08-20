from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from fastapi.responses import HTMLResponse

from pathlib import Path

import uuid
import traceback
import asyncio

from concurrent.futures import ThreadPoolExecutor

from app.services.ocr.pipeline import pipeline


router = APIRouter(
    prefix="/facture-scan",
    tags=["Facture Scan"]
)


# =========================================================
# DOSSIERS
# =========================================================

# Racine du projet :
# repair-platform/
#
# backend/
# frontend/
#
# On remonte depuis :
# backend/app/routers/facture_scan.py
# vers :
# repair-platform/

PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]


DOSSIER_SCAN = (
    PROJECT_ROOT
    / "backend"
    / "uploads"
    / "facture_scan"
)


DOSSIER_SCAN.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# FRONTEND MOBILE
# =========================================================

MOBILE_HTML = (
    PROJECT_ROOT
    / "frontend"
    / "mobile"
    / "facture_scan.html"
)


# =========================================================
# SESSIONS
# =========================================================

sessions = {}

# =========================================================
# EXECUTEUR OCR MOBILE
# =========================================================

OCR_EXECUTOR = ThreadPoolExecutor(
    max_workers=1,
    thread_name_prefix="OCR-MOBILE"
)

# =========================================================
# CREER SESSION
# =========================================================

@router.post("/session")
async def create_session():

    session_id = str(
        uuid.uuid4()
    )

    sessions[session_id] = {
        "status": "WAITING",
        "image_path": None,
        "result": None
    }

    print()
    print("=" * 80)
    print("NOUVELLE SESSION SCAN")
    print("=" * 80)

    print(
        "SESSION ID :",
        session_id
    )

    print(
        "STATUS     : WAITING"
    )

    print("=" * 80)

    return {
        "session_id": session_id,
        "status": "WAITING"
    }


# =========================================================
# STATUT SESSION
# =========================================================

@router.get(
    "/session/{session_id}"
)
async def get_session_status(
    session_id: str
):

    session = sessions.get(
        session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session introuvable."
        )

    return {
        "session_id": session_id,
        "status": session["status"]
    }


# =========================================================
# PAGE MOBILE
# =========================================================

@router.get(
    "/mobile/{session_id}",
    response_class=HTMLResponse
)
async def mobile_page(
    session_id: str
):

    # -----------------------------------------------------
    # SESSION
    # -----------------------------------------------------

    session = sessions.get(
        session_id
    )

    if session is None:

        return HTMLResponse(
            content="""
<!DOCTYPE html>

<html lang="fr">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Session invalide</title>

</head>

<body
style="
    font-family: Arial;
    text-align: center;
    padding: 50px;
"
>

<h2>❌ Session invalide</h2>

<p>
Cette session de scan n'existe plus.
</p>

</body>

</html>
""",
            status_code=404
        )

    # -----------------------------------------------------
    # VERIFIER FICHIER HTML
    # -----------------------------------------------------

    print()
    print(
        "[MOBILE] HTML :",
        MOBILE_HTML
    )

    print(
        "[MOBILE] EXISTS :",
        MOBILE_HTML.exists()
    )

    if not MOBILE_HTML.exists():

        raise HTTPException(
            status_code=500,
            detail=(
                "Fichier mobile introuvable : "
                f"{MOBILE_HTML}"
            )
        )

    # -----------------------------------------------------
    # LIRE HTML
    # -----------------------------------------------------

    try:

        html = MOBILE_HTML.read_text(
            encoding="utf-8"
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Impossible de lire le fichier mobile : "
                f"{str(e)}"
            )
        )

    # -----------------------------------------------------
    # INJECTER SESSION ID
    # -----------------------------------------------------

    html = html.replace(
        "{{ session_id }}",
        session_id
    )

    return HTMLResponse(
        content=html
    )


# =========================================================
# UPLOAD FACTURE
# =========================================================

@router.post(
    "/upload/{session_id}"
)
async def upload_facture(
    session_id: str,
    image: UploadFile = File(...)
):

    # =====================================================
    # 1. SESSION
    # =====================================================

    session = sessions.get(
        session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session introuvable."
        )

    if session["status"] != "WAITING":

        raise HTTPException(
            status_code=400,
            detail=(
                "Cette session ne peut plus "
                "recevoir de facture."
            )
        )

    # =====================================================
    # 2. FICHIER
    # =====================================================

    if not image.filename:

        raise HTTPException(
            status_code=400,
            detail="Nom de fichier manquant."
        )

    extension = (
        Path(image.filename)
        .suffix
        .lower()
    )

    extensions_autorisees = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp"
    }

    if extension not in extensions_autorisees:

        raise HTTPException(
            status_code=400,
            detail="Format d'image non supporté."
        )

    # =====================================================
    # 3. LIRE IMAGE
    # =====================================================

    try:

        contenu = await image.read()

        if not contenu:

            raise HTTPException(
                status_code=400,
                detail="Image vide."
            )

    except HTTPException:

        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur lors de la lecture "
                f"de l'image : {str(e)}"
            )
        )

    # =====================================================
    # 4. SAUVEGARDER
    # =====================================================

    nom_fichier = (
        f"{session_id}"
        f"{extension}"
    )

    chemin = (
        DOSSIER_SCAN
        / nom_fichier
    )

    try:

        with open(
            chemin,
            "wb"
        ) as f:

            f.write(
                contenu
            )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur lors de la sauvegarde "
                f"de l'image : {str(e)}"
            )
        )

    # =====================================================
    # 5. SESSION PROCESSING
    # =====================================================

    session["status"] = "PROCESSING"

    session["image_path"] = str(
        chemin
    )

    session["result"] = None

    print()
    print("=" * 80)
    print("FACTURE RECUE DEPUIS TELEPHONE")
    print("=" * 80)

    print(
        "SESSION :",
        session_id
    )

    print(
        "FICHIER :",
        chemin
    )

    print(
        "STATUS : PROCESSING"
    )

    print("=" * 80)

    # =====================================================
    # 6. OCR THREAD
    # =====================================================

    OCR_EXECUTOR.submit(
        executer_pipeline_ocr,
        session_id,
        str(chemin)
    )

    # =====================================================
    # 7. REPONSE IMMEDIATE
    # =====================================================

    return {
        "message": (
            "Facture reçue. "
            "Analyse OCR démarrée."
        ),

        "session_id": session_id,

        "status": "PROCESSING"
    }


# =========================================================
# RESULTAT FACTURE
# =========================================================

@router.get(
    "/result/{session_id}"
)
async def get_facture_result(
    session_id: str
):

    session = sessions.get(
        session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session introuvable."
        )

    # -----------------------------------------------------
    # ERREUR
    # -----------------------------------------------------

    if session["status"] == "ERROR":

        error = session.get(
            "result",
            {}
        )

        if isinstance(error, dict):

            detail = error.get(
                "error",
                "Erreur OCR inconnue."
            )

        else:

            detail = "Erreur OCR inconnue."

        return {
            "status": "ERROR",
            "error": detail
        }

    # -----------------------------------------------------
    # OCR EN COURS
    # -----------------------------------------------------

    if session["status"] != "READY":

        raise HTTPException(
            status_code=409,
            detail=(
                "Le résultat OCR n'est pas "
                "encore disponible."
            )
        )

    # -----------------------------------------------------
    # RESULTAT
    # -----------------------------------------------------

    return session["result"]


# =========================================================
# FERMER SESSION
# =========================================================

@router.delete(
    "/session/{session_id}"
)
async def close_session(
    session_id: str
):

    session = sessions.pop(
        session_id,
        None
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session introuvable."
        )

    # -----------------------------------------------------
    # SUPPRIMER IMAGE
    # -----------------------------------------------------

    image_path = session.get(
        "image_path"
    )

    if image_path:

        try:

            path = Path(
                image_path
            )

            if path.exists():

                path.unlink()

        except Exception:

            traceback.print_exc()

    return {
        "message": "Session fermée.",
        "session_id": session_id
    }


# =========================================================
# OCR EN ARRIERE-PLAN
# =========================================================

# =========================================================
# OCR EN ARRIERE-PLAN
# =========================================================

def executer_pipeline_ocr(
    session_id,
    chemin
):

    session = sessions.get(
        session_id
    )

    if session is None:
        return

    try:

        print()
        print("=" * 80)
        print("DEMARRAGE OCR MOBILE")
        print("=" * 80)

        print(
            "SESSION :",
            session_id
        )

        print(
            "FICHIER :",
            chemin
        )

        print("=" * 80)


        # =================================================
        # OCR
        # =================================================

        resultat = pipeline.process(
            str(chemin)
        )


        # =================================================
        # RESULTAT
        # =================================================

        session = sessions.get(
            session_id
        )

        if session is None:
            return


        session["result"] = resultat

        session["status"] = "READY"


        print()
        print("=" * 80)
        print("OCR MOBILE TERMINE")
        print("=" * 80)

        print(
            "SESSION :",
            session_id
        )

        print(
            "STATUS : READY"
        )

        print("=" * 80)


    except Exception as e:

        session = sessions.get(
            session_id
        )

        if session is None:
            return


        session["status"] = "ERROR"

        session["result"] = {
            "error": str(e)
        }


        print()
        print("=" * 80)
        print("ERREUR OCR MOBILE")
        print("=" * 80)

        print(
            "SESSION :",
            session_id
        )

        print(
            "ERREUR :",
            str(e)
        )

        traceback.print_exc()

        print("=" * 80)
