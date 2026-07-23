from sqlalchemy.orm import Session

from app.crud.reparation import (
    get_reparation
)

from app.crud.historique_statut import (
    create_historique
)


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

    if nouveau_statut not in STATUTS_AUTORISES:

        raise ValueError(

            "Statut invalide"

        )


    reparation = get_reparation(

        db,

        reparation_id

    )


    if not reparation:

        return None


    ancien_statut = reparation.statut


    if ancien_statut == nouveau_statut:

        raise ValueError(

            "Le nouveau statut est identique à l'ancien"

        )


    reparation.statut = nouveau_statut


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