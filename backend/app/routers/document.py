from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.document_ocr import DocumentOCRCreate

from app.crud.document import create_document

router = APIRouter(

    prefix="/documents",

    tags=["Documents OCR"]

)


@router.post("/")

def save_document(

    document: DocumentOCRCreate,

    db: Session = Depends(get_db)

):

    obj = create_document(

        db,

        document

    )

    return {

        "success": True,

        "id": obj.id

    }