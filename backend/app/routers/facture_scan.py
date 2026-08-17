from fastapi.responses import HTMLResponse
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks
)
from pathlib import Path
import uuid
import traceback

from app.services.ocr.pipeline import pipeline


router = APIRouter(
    prefix="/facture-scan",
    tags=["Facture Scan"]
)


# =========================================================
# DOSSIERS
# =========================================================

DOSSIER_SCAN = Path("uploads/facture_scan")

DOSSIER_SCAN.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# SESSIONS
# =========================================================

sessions = {}


# =========================================================
# CREER SESSION
# =========================================================

@router.post("/session")
async def create_session():

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "status": "WAITING",
        "image_path": None,
        "result": None
    }

    print()
    print("=" * 80)
    print("NOUVELLE SESSION SCAN")
    print("=" * 80)
    print("SESSION ID :", session_id)
    print("=" * 80)

    return {
        "session_id": session_id,
        "status": "WAITING"
    }


# =========================================================
# STATUT SESSION
# =========================================================

@router.get("/session/{session_id}")
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

    session = sessions.get(
        session_id
    )

    if session is None:

        return HTMLResponse(
            content="""
            <html>
                <body style="
                    font-family:Arial;
                    text-align:center;
                    padding:50px;
                ">
                    <h2>❌ Session invalide</h2>
                    <p>Cette session de scan n'existe plus.</p>
                </body>
            </html>
            """,
            status_code=404
        )

    return HTMLResponse(
        content=f"""
<!DOCTYPE html>

<html lang="fr">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Scanner une facture
</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;

    padding: 20px;

    font-family:
        Arial,
        sans-serif;

    background:
        #f4f6f8;

    color:
        #1f2937;
}}

.container {{

    max-width:
        500px;

    margin:
        auto;

    background:
        white;

    padding:
        25px;

    border-radius:
        16px;

    box-shadow:
        0 4px 20px
        rgba(0,0,0,0.08);
}}

h1 {{

    text-align:
        center;

    font-size:
        24px;

    margin-bottom:
        10px;
}}

.description {{

    text-align:
        center;

    color:
        #6b7280;

    line-height:
        1.5;

    margin-bottom:
        25px;
}}

.file-label {{

    display:
        block;

    width:
        100%;

    padding:
        16px;

    margin-top:
        15px;

    border-radius:
        10px;

    text-align:
        center;

    background:
        #2563eb;

    color:
        white;

    font-weight:
        bold;

    cursor:
        pointer;
}}

input[type="file"] {{

    display:
        none;
}}

#preview {{

    width:
        100%;

    max-height:
        500px;

    object-fit:
        contain;

    margin-top:
        20px;

    border-radius:
        10px;

    display:
        none;
}}

button {{

    width:
        100%;

    padding:
        16px;

    margin-top:
        20px;

    border:
        none;

    border-radius:
        10px;

    background:
        #16a34a;

    color:
        white;

    font-size:
        16px;

    font-weight:
        bold;

    cursor:
        pointer;
}}

button:disabled {{

    background:
        #9ca3af;

    cursor:
        not-allowed;
}}

#message {{

    margin-top:
        20px;

    text-align:
        center;

    font-weight:
        bold;

    line-height:
        1.5;
}}

.success {{

    color:
        #15803d;
}}

.error {{

    color:
        #dc2626;
}}

</style>

</head>


<body>

<div class="container">

<h1>
📱 Scanner une facture
</h1>

<div class="description">

Prenez une photo de votre facture
ou sélectionnez une image depuis
la galerie de votre téléphone.

</div>


<label
    class="file-label"
    for="fileInput"
>

📷 Choisir / prendre une photo

</label>


<input
    id="fileInput"
    type="file"
    accept="image/*"
    capture="environment"
>


<img
    id="preview"
    alt="Aperçu de la facture"
>


<button
    id="uploadButton"
    disabled
>

Envoyer la facture

</button>


<div id="message"></div>

</div>


<script>

const fileInput =
    document.getElementById(
        "fileInput"
    );

const preview =
    document.getElementById(
        "preview"
    );

const uploadButton =
    document.getElementById(
        "uploadButton"
    );

const message =
    document.getElementById(
        "message"
    );


let selectedFile = null;


fileInput.addEventListener(
    "change",
    function() {{

        selectedFile =
            this.files[0];

        if (!selectedFile) {{

            uploadButton.disabled =
                true;

            return;
        }}


        const reader =
            new FileReader();


        reader.onload =
            function(event) {{

                preview.src =
                    event.target.result;

                preview.style.display =
                    "block";

            }};


        reader.readAsDataURL(
            selectedFile
        );


        uploadButton.disabled =
            false;

        message.textContent =
            "Image sélectionnée.";

        message.className = "";

    }}
);


uploadButton.addEventListener(
    "click",
    async function() {{

        if (!selectedFile) {{
            return;
        }}


        uploadButton.disabled =
            true;

        message.textContent =
            "Envoi de la facture...";

        message.className = "";


        const formData =
            new FormData();


        formData.append(
            "image",
            selectedFile
        );


        try {{

            const response =
                await fetch(
                    "/facture-scan/upload/{session_id}",
                    {{
                        method:
                            "POST",

                        body:
                            formData
                    }}
                );


            const data =
                await response.json();


            if (!response.ok) {{

                throw new Error(
                    data.detail ||
                    "Erreur pendant l'envoi."
                );

            }}


            message.textContent =
                "✅ Facture envoyée. "
                + "L'analyse OCR est en cours...";

            message.className =
                "success";


            uploadButton.disabled =
                true;


        }} catch(error) {{

            console.error(
                error
            );


            message.textContent =
                "❌ " + error.message;

            message.className =
                "error";


            uploadButton.disabled =
                false;

        }}

    }}

);

</script>

</body>

</html>
"""
    )


# =========================================================
# UPLOAD FACTURE
# =========================================================

@router.post("/upload/{session_id}")
async def upload_facture(
    session_id: str,
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...)
):

    # =========================================================
    # 1. VERIFIER SESSION
    # =========================================================

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


    # =========================================================
    # 2. VERIFIER FICHIER
    # =========================================================

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


    # =========================================================
    # 3. LIRE IMAGE
    # =========================================================

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


    # =========================================================
    # 4. SAUVEGARDER IMAGE
    # =========================================================

    nom_fichier = (
        f"{session_id}"
        f"{extension}"
    )


    chemin = (
        DOSSIER_SCAN
        /
        nom_fichier
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


    # =========================================================
    # 5. METTRE SESSION EN PROCESSING
    # =========================================================

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


    # =========================================================
    # 6. LANCER OCR EN ARRIERE-PLAN
    # =========================================================

    background_tasks.add_task(
        traiter_facture_scan,
        session_id,
        str(chemin)
    )


    # =========================================================
    # 7. REPONSE IMMEDIATE
    # =========================================================

    return {

        "message":
            "Facture reçue. "
            "Analyse OCR démarrée.",

        "session_id":
            session_id,

        "status":
            "PROCESSING"

    }

# =========================================================
# RESULTAT FACTURE
# =========================================================

@router.get("/result/{session_id}")
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


    if session["status"] == "ERROR":

        error = session.get(
            "result",
            {}
        )

        raise HTTPException(
            status_code=500,
            detail=error.get(
                "error",
                "Erreur OCR inconnue."
            )
        )


    if session["status"] != "READY":

        raise HTTPException(
            status_code=409,
            detail=(
                "Le résultat OCR n'est pas "
                "encore disponible."
            )
        )


    return session["result"]


# =========================================================
# FERMER SESSION
# =========================================================

@router.delete("/session/{session_id}")
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
        "message":
            "Session fermée.",
        "session_id":
            session_id
    }

# =========================================================
# OCR EN ARRIERE-PLAN
# =========================================================

def traiter_facture_scan(
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


        # =====================================================
        # OCR
        # =====================================================

        resultat = pipeline.process(
            str(chemin)
        )


        # =====================================================
        # RESULTAT
        # =====================================================

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
