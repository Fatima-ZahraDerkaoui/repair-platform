from datetime import datetime

from pydantic import BaseModel


class AlerteStockResponse(BaseModel):

    id: int

    piece_id: int

    reparation_id: int | None

    quantite_demandee: int

    quantite_disponible: int

    message: str

    statut: str

    date_creation: datetime

    class Config:

        from_attributes = True