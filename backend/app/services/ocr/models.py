from dataclasses import dataclass


@dataclass
class LigneDocument:

    reference: str

    designation: str

    quantite: int | None

    prix_unitaire: float | None

    total: float | None