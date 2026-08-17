from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.facture_ligne import (
    FactureLigneCreate,
    FactureLigneResponse
)


class FactureBase(BaseModel):

    fournisseur_id: int | None = None

    numero: str | None = None

    date_facture: datetime | None = None

    total_ht: Decimal | None = None

    total_tva: Decimal | None = None

    total_ttc: Decimal | None = None

    statut: str = "A_VALIDER"

    texte_ocr: str | None = None

    chemin_document: str | None = None


class FactureCreate(FactureBase):

    lignes: list[FactureLigneCreate] = []


class FactureUpdate(BaseModel):

    fournisseur_id: int | None = None

    numero: str | None = None

    date_facture: datetime | None = None

    total_ht: Decimal | None = None

    total_tva: Decimal | None = None

    total_ttc: Decimal | None = None

    statut: str | None = None

    texte_ocr: str | None = None

    chemin_document: str | None = None


class FactureResponse(FactureBase):

    id: int

    date_creation: datetime

    lignes: list[FactureLigneResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )