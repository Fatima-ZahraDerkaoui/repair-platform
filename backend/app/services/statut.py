from sqlalchemy.orm import Session

from app.models.reparation import Reparation
from app.models.historique_statut import HistoriqueStatut


STATUTS_AUTORISES = [

    "En attente",

    "Diagnostic",

    "En réparation",

    "En test",

    "Terminé",

    "Livré"
]


def changer_statut(

    db: Session,

    reparation_id: int,

    nouveau_statut: str,

    utilisateur_id: int | None = None

):

    if nouveau_statut not in STATUTS_AUTORISES:

        raise ValueError(
            "Statut invalide"
        )


    reparation = (

        db.query(Reparation)

        .filter(
            Reparation.id == reparation_id
        )

        .first()
    )


    if not reparation:

        return None


    ancien_statut = reparation.statut


    # Éviter un historique inutile
    if ancien_statut == nouveau_statut:

        return reparation


    reparation.statut = nouveau_statut


    historique = HistoriqueStatut(

        reparation_id=reparation.id,

        ancien_statut=ancien_statut,

        nouveau_statut=nouveau_statut,

        utilisateur_id=utilisateur_id

    )


    db.add(historique)

    db.commit()

    db.refresh(reparation)


    return reparation