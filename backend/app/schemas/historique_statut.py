from datetime import datetime

from pydantic import BaseModel


class HistoriqueStatutResponse(BaseModel):

    id: int

    reparation_id: int

    ancien_statut: str | None

    nouveau_statut: str

    utilisateur_id: int | None

    date_modification: datetime

    class Config:

        from_attributes = True
