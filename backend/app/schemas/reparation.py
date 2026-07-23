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

class ReparationCreate(ReparationBase):
    pass

class ReparationUpdate(ReparationBase):
    
    diagnostic: str | None = None

    intervention: str | None = None

    pieces_defectueuses: str | None = None

    remarques: str | None = None

    cout_reel: Decimal | None = None

    date_fin: datetime | None = None

class ReparationResponse(ReparationBase):

    id: int

    statut: str

    numero_dossier: str | None = None

    qr_code: Optional[str]

    texte_ocr: Optional[str]

    delai_estime: Optional[int]

    cout_estime: Optional[float]

    cout_reel: Optional[float]

    date_reception: datetime

    date_fin: Optional[datetime]

    class Config:
        from_attributes = True

class StatutUpdate(BaseModel):

    nouveau_statut: str

    utilisateur_id: int | None = None

from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class ClientInfo(BaseModel):

    nom: str

    telephone: str


class ReparationResponse(BaseModel):

    id: int

    client_id: int

    client: ClientInfo

    receptionniste_id: int

    type_materiel: str

    systeme_exploitation: str

    version_office: str

    origine_probleme: str

    intervention: str | None

    probleme: str

    pieces_defectueuses: str | None

    remarques: str | None

    mot_de_passe_pc: str | None

    urgent: bool

    resolu: bool

    statut: str

    numero_dossier: str | None

    qr_code: str | None

    texte_ocr: str | None

    delai_estime: int | None

    cout_estime: float | None

    cout_reel: float | None

    date_reception: datetime

    date_fin: datetime | None

    class Config:

        from_attributes = True