import json

from sqlalchemy.orm import Session

from app.models.document import DocumentOCR


def create_document(db: Session, data):

    document = DocumentOCR(

        session_id=data.session_id,

        document_type=data.document_type,

        numero=data.numero,

        date_document=data.date_document,

        fournisseur=data.fournisseur,

        total_ht=data.total_ht,

        tva=data.tva,

        total_ttc=data.total_ttc,

        fichier_image=data.fichier_image,

        resultat_json=data.resultat_json

    )

    db.add(document)

    db.commit()

    db.refresh(document)

    return document