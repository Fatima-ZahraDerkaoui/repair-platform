from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class OCRRepairResponse(BaseModel):

    date_reception: Optional[date] = None

    nom: Optional[str] = None

    telephone: Optional[str] = None

    type_materiel: Optional[str] = None

    mot_de_passe: Optional[str] = None

    systeme_exploitation: Optional[str] = None

    version_office: Optional[str] = None

    origine_probleme: Optional[str] = None

    intervention: List[str] = []

    probleme: Optional[str] = None

    pieces_defectueuses: Optional[str] = None

    remarques: Optional[str] = None

    urgent: bool = False

    resolu: bool = False