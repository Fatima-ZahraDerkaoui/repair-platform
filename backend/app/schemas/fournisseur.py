from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FournisseurBase(BaseModel):
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


class FournisseurCreate(FournisseurBase):
    pass


class FournisseurUpdate(BaseModel):
    nom: str | None = None

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


class FournisseurResponse(FournisseurBase):
    id: int
    date_creation: datetime

    model_config = ConfigDict(
        from_attributes=True
    )