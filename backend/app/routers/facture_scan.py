from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.services.ocr.pipeline import pipeline
from app.facture_scan.manager import manager
from app.scan.qr_generator import generate_qrcode

router = APIRouter(
    prefix="/facture-scan",
    tags=["Facture Scan"]
)

UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/session")
def create_session():

    session = manager.create_session()

    qr = generate_qrcode(session.session_id)

    return {

        "success": True,

        "session_id": session.session_id,

        "mobile_url": qr["url"],

        "qr_code": qr["path"],

        "status": session.status

    }


@router.get("/session/{session_id}")
def session_status(session_id: str):

    session = manager.get(session_id)

    if session is None:
        raise HTTPException(404)

    return {

        "session_id": session.session_id,

        "status": session.status,

        "mobile_connected": session.mobile_connected,

        "ocr_running": session.ocr_running,

        "documents_processed": session.documents_processed,

        "images": session.images

    }


@router.post("/upload/{session_id}")
async def upload_image(
    session_id: str,
    image: UploadFile = File(...)
):

    session = manager.get(session_id)

    if session is None:
        raise HTTPException(404)

    extension = Path(image.filename).suffix

    filename = f"{session_id}_{len(session.images)+1}{extension}"

    filepath = session.folder / filename

    with open(filepath, "wb") as buffer:

        shutil.copyfileobj(image.file, buffer)

    manager.add_image(session_id, str(filepath))

    manager.start_ocr(session_id)

    ocr_result = pipeline.process(str(filepath))

    manager.save_result(
        session_id,
        ocr_result
    )

    manager.save_result(
        session_id,
        ocr_result
    )

    manager.finish_ocr(session_id)

    return {

        "success": True,

        "ocr": ocr_result

    }

@router.get("/result/{session_id}")
def get_result(session_id: str):

    session = manager.get(session_id)

    if session is None:
        raise HTTPException(404, "Session introuvable")

    return {

        "success": True,

        "status": session.status,

        "documents_processed": session.documents_processed,

        "result": session.result

    }

@router.delete("/session/{session_id}")
def close_session(session_id: str):

    manager.close(session_id)

    return {

        "success": True

    }


@router.get("/qrcode/{session_id}")
def get_qrcode(session_id: str):

    path = Path("uploads/qrcodes") / f"{session_id}.png"

    if not path.exists():

        raise HTTPException(404)

    return FileResponse(path)
