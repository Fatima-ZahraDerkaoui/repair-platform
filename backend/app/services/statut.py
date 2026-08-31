from sqlalchemy.orm import Session

from app.crud.reparation import (
    get_reparation
)

from app.crud.historique_statut import (
    create_historique
)


# =========================================================
# STATUTS OFFICIELS
# =========================================================

STATUTS_AUTORISES = [

    "En attente",

    "En diagnostic",

    "En réparation",

    "Terminé"

]


# =========================================================
# CHANGER STATUT
# =========================================================
from datetime import datetime
from sqlalchemy.orm import Session
from app.crud.reparation import get_reparation
from app.crud.historique_statut import create_historique

STATUTS_AUTORISES = [
    "En attente",
    "En diagnostic",
    "En réparation",
    "Terminé"
]

def changer_statut(
    db: Session,
    reparation_id: int,
    nouveau_statut: str,
    utilisateur_id: int | None = None
):
    nouveau_statut = (nouveau_statut or "").strip()

    if nouveau_statut not in STATUTS_AUTORISES:
        raise ValueError(
            "Statut invalide. Valeurs autorisées : " + ", ".join(STATUTS_AUTORISES)
        )

    reparation = get_reparation(db, reparation_id)
    if not reparation:
        return None

    ancien_statut = reparation.statut or "En attente"

    if ancien_statut == nouveau_statut:
        raise ValueError("Le nouveau statut est identique à l'ancien")

    reparation.statut = nouveau_statut

    # -----------------------------------------------------
    # GESTION AUTOMATIQUE DATE SORTIE & DÉLAI RÉEL
    # -----------------------------------------------------
    if nouveau_statut == "Terminé":
        maintenant = datetime.now()
        reparation.date_sortie = maintenant
        reparation.resolu = True

        date_entree = getattr(reparation, "date_reception", None) or getattr(reparation, "date_entree", None)
        if date_entree:
            delai_calcul = (maintenant - date_entree).days
            reparation.delai_estime = max(delai_calcul, 1)
    else:
        reparation.resolu = False

    create_historique(
        db=db,
        reparation_id=reparation.id,
        ancien_statut=ancien_statut,
        nouveau_statut=nouveau_statut,
        utilisateur_id=utilisateur_id
    )

    db.commit()
    db.refresh(reparation)

    return reparation
