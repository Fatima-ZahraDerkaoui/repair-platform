from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.sql import func

from app.database.database import Base


class DocumentOCR(Base):

    __tablename__ = "documents_ocr"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(String(100), nullable=False, unique=True)

    document_type = Column(String(50), nullable=False)

    numero = Column(String(100))

    date_document = Column(String(50))

    fournisseur = Column(String(255))

    total_ht = Column(String(50))

    tva = Column(String(50))

    total_ttc = Column(String(50))

    fichier_image = Column(Text)

    resultat_json = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )