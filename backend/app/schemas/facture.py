from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.facture_ligne import (
    FactureLigneCreate,
    FactureLigneResponse
)


# ==========================================================
# FOURNISSEUR DANS LA REPONSE
# ==========================================================

class FournisseurFactureResponse(BaseModel):

    id: int

    nom: str

    adresse: str | None = None
    ville: str | None = None
    pays: str | None = None
    telephone: str | None = None
    fax: str | None = None
    email: str | None = None
    site_web: str | None = None
    ice: str | None = None
    identifiant_fiscal: str | None = None
    rc: str | None = None
    patente: str | None = None
    cnss: str | None = None
    rib: str | None = None

    date_creation: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# BASE
# ==========================================================

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


# ==========================================================
# CREATION
# ==========================================================

class FactureCreate(BaseModel):

    fournisseur_id: int | None = None

    # IMPORTANT :
    # On accepte directement le dictionnaire provenant
    # du résultat OCR.
    #
    # Exemple :
    #
    # "fournisseur": {
    #     "name": "CASINFO",
    #     "address": "...",
    #     "ice": "..."
    # }
    #
    fournisseur: dict[str, Any] | None = None

    numero: str | None = None

    date_facture: datetime | None = None

    total_ht: Decimal | None = None

    total_tva: Decimal | None = None

    total_ttc: Decimal | None = None

    statut: str = "A_VALIDER"

    texte_ocr: str | None = None

    chemin_document: str | None = None

    lignes: list[FactureLigneCreate] = Field(
        default_factory=list
    )


# ==========================================================
# UPDATE
# ==========================================================

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


# ==========================================================
# REPONSE
# ==========================================================

class FactureResponse(FactureBase):

    id: int

    date_creation: datetime

    fournisseur: FournisseurFactureResponse | None = None

    lignes: list[FactureLigneResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )