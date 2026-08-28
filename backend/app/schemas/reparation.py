from decimal import Decimal
from typing import Optional
from datetime import datetime

from pydantic import BaseModel


# =========================================================
# BASE
# =========================================================

class ReparationBase(BaseModel):

    client_id: int

    receptionniste_id: int

    type_materiel: str

    marque: Optional[str] = None

    modele: Optional[str] = None

    numero_serie: Optional[str] = None

    systeme_exploitation: Optional[str] = None

    version_office: Optional[str] = None

    mot_de_passe_pc: Optional[str] = None

    origine_probleme: Optional[str] = None

    intervention: Optional[str] = None

    probleme: Optional[str] = None

    diagnostic: Optional[str] = None

    pieces_defectueuses: Optional[str] = None

    accessoires: Optional[str] = None

    remarques: Optional[str] = None

    urgent: bool = False

    resolu: bool = False


# =========================================================
# CRÉATION
# =========================================================

class ReparationCreate(ReparationBase):

    pass


# =========================================================
# MODIFICATION
# =========================================================

class ReparationUpdate(BaseModel):

    # -----------------------------------------------------
    # CLIENT
    # -----------------------------------------------------

    client_nom: Optional[str] = None

    client_telephone: Optional[str] = None

    client_email: Optional[str] = None

    # -----------------------------------------------------
    # MATÉRIEL
    # -----------------------------------------------------

    type_materiel: Optional[str] = None

    marque: Optional[str] = None

    modele: Optional[str] = None

    numero_serie: Optional[str] = None

    systeme_exploitation: Optional[str] = None

    version_office: Optional[str] = None

    mot_de_passe_pc: Optional[str] = None

    origine_probleme: Optional[str] = None

    # -----------------------------------------------------
    # RÉPARATION
    # -----------------------------------------------------

    probleme: Optional[str] = None

    diagnostic: Optional[str] = None

    intervention: Optional[str] = None

    pieces_defectueuses: Optional[str] = None

    accessoires: Optional[str] = None

    remarques: Optional[str] = None

    # -----------------------------------------------------
    # STATUT
    # -----------------------------------------------------

    statut: Optional[str] = None

    resolu: Optional[bool] = None

    urgent: Optional[bool] = None

    # -----------------------------------------------------
    # FINANCES
    # -----------------------------------------------------
    cout_estime: Optional[float] = None

    cout_reel: Optional[float] = None

    date_fin: Optional[datetime] = None


# =========================================================
# MODIFICATION DU STATUT
# =========================================================

class StatutUpdate(BaseModel):

    nouveau_statut: str

    utilisateur_id: Optional[int] = None


# =========================================================
# CLIENT
# =========================================================

class ClientInfo(BaseModel):

    id: int

    nom: str

    telephone: str

    email: Optional[str] = None

    adresse: Optional[str] = None

    class Config:
        from_attributes = True


# =========================================================
# RÉPONSE
# =========================================================

class ReparationResponse(BaseModel):

    id: int

    client_id: int

    receptionniste_id: int

    date_reception: datetime

    type_materiel: str

    marque: Optional[str] = None

    modele: Optional[str] = None

    numero_serie: Optional[str] = None

    systeme_exploitation: Optional[str] = None

    version_office: Optional[str] = None

    mot_de_passe_pc: Optional[str] = None

    origine_probleme: Optional[str] = None

    probleme: Optional[str] = None

    diagnostic: Optional[str] = None

    intervention: Optional[str] = None

    pieces_defectueuses: Optional[str] = None

    accessoires: Optional[str] = None

    remarques: Optional[str] = None

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
        