from pydantic import BaseModel
from typing import Optional


class ProduitOCR(BaseModel):

    reference: Optional[str] = None

    designation: Optional[str] = None

    quantite: Optional[float] = None

    prix_unitaire: Optional[float] = None

    total: Optional[float] = None


class FournisseurOCR(BaseModel):

    nom: Optional[str] = None

    telephone: Optional[str] = None

    email: Optional[str] = None

    adresse: Optional[str] = None


class ClientOCR(BaseModel):

    nom: Optional[str] = None

    telephone: Optional[str] = None

    adresse: Optional[str] = None


class TotauxOCR(BaseModel):

    total_ht: Optional[float] = None

    total_tva: Optional[float] = None

    total_ttc: Optional[float] = None


class DocumentOCRResponse(BaseModel):

    type_document: Optional[str] = None

    numero_document: Optional[str] = None

    date_document: Optional[str] = None

    fournisseur: Optional[FournisseurOCR] = None

    client: Optional[ClientOCR] = None

    produits: list[ProduitOCR] = []

    totaux: Optional[TotauxOCR] = None