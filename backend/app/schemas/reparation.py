from decimal import Decimal
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReparationBase(BaseModel):

    client_id: int

    receptionniste_id: int

    type_materiel: str

    systeme_exploitation: Optional[str] = None

    version_office: Optional[str] = None

    origine_probleme: Optional[str] = None

    intervention: Optional[str] = None

    probleme: Optional[str] = None

    pieces_defectueuses: Optional[str] = None

    remarques: Optional[str] = None

    mot_de_passe_pc: Optional[str] = None

    urgent: bool = False

    resolu: bool = False


class ReparationCreate(ReparationBase):
    pass


class ReparationUpdate(BaseModel):

    diagnostic: Optional[str] = None

    intervention: Optional[str] = None

    pieces_defectueuses: Optional[str] = None

    remarques: Optional[str] = None

    cout_reel: Optional[Decimal] = None

    date_fin: Optional[datetime] = None


class StatutUpdate(BaseModel):

    nouveau_statut: str

    utilisateur_id: Optional[int] = None


class ClientInfo(BaseModel):

    id: int

    nom: str

    telephone: str

    email: Optional[str] = None

    adresse: Optional[str] = None

    class Config:

        from_attributes = True


class ReparationResponse(BaseModel):

    id: int

    client_id: int

    receptionniste_id: int

    date_reception: datetime

    type_materiel: str

    systeme_exploitation: Optional[str] = None

    version_office: Optional[str] = None

    origine_probleme: Optional[str] = None

    probleme: Optional[str] = None

    diagnostic: Optional[str] = None

    intervention: Optional[str] = None

    pieces_defectueuses: Optional[str] = None

    remarques: Optional[str] = None

    mot_de_passe_pc: Optional[str] = None

    urgent: bool

    resolu: bool

    statut: str

    numero_dossier: Optional[str] = None

    qr_code: Optional[str] = None

    texte_ocr: Optional[str] = None

    delai_estime: Optional[int] = None

    cout_estime: Optional[Decimal] = None

    cout_reel: Optional[Decimal] = None

    date_fin: Optional[datetime] = None

    fiche_pdf: Optional[str] = None

    client: Optional[ClientInfo] = None


    class Config:

        from_attributes = True