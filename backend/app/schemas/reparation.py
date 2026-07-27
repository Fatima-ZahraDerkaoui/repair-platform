from decimal import Decimal

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReparationBase(BaseModel):

    client_id: int

    receptionniste_id: int

    type_materiel: str

    systeme_exploitation: str

    version_office: str

    origine_probleme: str

    intervention: Optional[str] = None

    probleme: str

    pieces_defectueuses: Optional[str] = None

    remarques: Optional[str] = None

    mot_de_passe_pc: Optional[str] = None

    urgent: bool = False

    resolu: bool = False

class ReparationCreate(BaseModel):

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

class ReparationUpdate(ReparationBase):
    
    diagnostic: str | None = None

    intervention: str | None = None

    pieces_defectueuses: str | None = None

    remarques: str | None = None

    cout_reel: Decimal | None = None

    date_fin: datetime | None = None

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


    class Config:

        from_attributes = True

class StatutUpdate(BaseModel):

    nouveau_statut: str

    utilisateur_id: int | None = None

class ClientInfo(BaseModel):

    nom: str

    telephone: str

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
    
    fiche_pdf: str | None = None

    class Config:

        from_attributes = True
