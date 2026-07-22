from .client import Client
from .utilisateur import Utilisateur
from .reparation import Reparation
from .stock import Stock
from .reparation_piece import ReparationPiece
from app.models.historique_statut import HistoriqueStatut
'''
TABLES EXISTANTES
│
├── utilisateur
├── client
├── article
├── stock
├── fournisseur
├── achat
├── facture
├── bon_livraison
└── reparation
        │
        │
        ▼
TABLES AJOUTÉES POUR LE PFA
│
├── historique_statut
├── reparation_article
├── notification
├── prediction_delai
└── prediction_cout
'''