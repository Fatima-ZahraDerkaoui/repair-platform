from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FactureLigneBase(BaseModel):

    stock_id: int | None = None

    designation: str | None = None

    reference: str | None = None

    quantite: Decimal | None = None

    prix_unitaire: Decimal | None = None

    total: Decimal | None = None


class FactureLigneCreate(FactureLigneBase):
    pass


class FactureLigneUpdate(BaseModel):

    stock_id: int | None = None

    designation: str | None = None

    reference: str | None = None

    quantite: Decimal | None = None

    prix_unitaire: Decimal | None = None

    total: Decimal | None = None


class FactureLigneResponse(FactureLigneBase):

    id: int

    facture_id: int

    model_config = ConfigDict(
        from_attributes=True
    )