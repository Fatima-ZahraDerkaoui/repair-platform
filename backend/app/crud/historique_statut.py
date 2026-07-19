from sqlalchemy.orm import Session

from app.models.historique_statut import (
    HistoriqueStatut
)

def create_historique(

    db: Session,

    reparation_id: int,

    ancien_statut: str | None,

    nouveau_statut: str,

    utilisateur_id: int | None = None

):

    historique = HistoriqueStatut(

        reparation_id=reparation_id,

        ancien_statut=ancien_statut,

        nouveau_statut=nouveau_statut,

        utilisateur_id=utilisateur_id

    )

    db.add(historique)

    return historique

def update_statut(

    db: Session,

    reparation_id: int,

    nouveau_statut: str,

    utilisateur_id: int | None = None

):

    reparation = get_reparation(

        db,

        reparation_id

    )

    if not reparation:

        return None

    ancien_statut = reparation.statut

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