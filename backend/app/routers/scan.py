from fastapi import APIRouter

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.scan.manager import manager
from pathlib import Path
import shutil
from fastapi import UploadFile, File
from app.scan.qr_generator import generate_qrcode


router = APIRouter(
    prefix="/scan",
    tags=["Scanner Mobile"]
)


@router.post("/session")
def create_scan_session():

    session = manager.create_session()

    qr = generate_qrcode(session.session_id)

    return {

        "success": True,

        "session_id": session.session_id,

        "connected": session.connected,

        "closed": session.closed,

        "mobile_url": qr["url"],

        "qr_code": qr["path"]

    }

templates = Jinja2Templates(directory="app/templates")

@router.get("/mobile/{session_id}", response_class=HTMLResponse)
async def mobile_scan(request: Request, session_id: str):

    manager.connect_phone(session_id)

    return templates.TemplateResponse(
        request=request,
        name="mobile_scan.html",
        context={
            "session_id": session_id
        }
    )

UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload/{session_id}")
async def upload_scan(
    session_id: str,
    image: UploadFile = File(...)
):

    extension = Path(image.filename).suffix

    filename = f"{session_id}{extension}"

    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return {
        "success": True,
        "filename": filename,
        "path": str(filepath)
    }

@router.get("/session/{session_id}")
def session_status(session_id: str):

    session = manager.get(session_id)

    if session is None:

        return {

            "exists": False

        }

    return {

        "exists": True,

        "connected": session.connected,

        "closed": session.closed,
        
        "status": session.status,

        "documents": len(session.uploaded_files)

    }

@router.delete("/session/{session_id}")
def close_session(session_id: str):

    manager.close(session_id)

    return {

        "success": True

    } 
