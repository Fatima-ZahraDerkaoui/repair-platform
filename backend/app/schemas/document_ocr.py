from pydantic import BaseModel


class DocumentOCRCreate(BaseModel):

    session_id: str

    document_type: str

    numero: str | None = None

    date_document: str | None = None

    fournisseur: str | None = None

    total_ht: str | None = None

    tva: str | None = None

    total_ttc: str | None = None

    fichier_image: str | None = None

    resultat_json: str