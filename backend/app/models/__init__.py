from app.models.client import Client
from app.models.utilisateur import Utilisateur
from app.models.stock import Stock
from app.models.reparation import Reparation
from app.models.reparation_piece import ReparationPiece
from app.models.historique_statut import HistoriqueStatut
from app.models.alerte_stock import AlerteStock
from app.models.fournisseur import Fournisseur
from app.models.facture import Facture
from app.models.facture_ligne import FactureLigne

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