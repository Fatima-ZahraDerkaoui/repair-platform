from dataclasses import dataclass, asdict
from typing import List


@dataclass
class InvoiceItem:
    designation: str
    tva: str
    prix_unitaire: float
    quantite: int
    total: float


@dataclass
class Invoice:
    fournisseur: str
    client: str
    numero_facture: str
    date: str
    total_ht: float
    total_tva: float
    total_ttc: float
    articles: List[InvoiceItem]