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

def changer_statut(

    db: Session,

    reparation_id: int,

    nouveau_statut: str,

    utilisateur_id: int | None = None

):

    # -----------------------------------------------------
    # Vérification
    # -----------------------------------------------------

    nouveau_statut = (
        nouveau_statut
        or ""
    ).strip()

    if nouveau_statut not in STATUTS_AUTORISES:

        raise ValueError(
            "Statut invalide. "
            "Valeurs autorisées : "
            + ", ".join(
                STATUTS_AUTORISES
            )
        )

    # -----------------------------------------------------
    # Récupérer réparation
    # -----------------------------------------------------

    reparation = get_reparation(
        db,
        reparation_id
    )

    if not reparation:

        return None

    ancien_statut = (
        reparation.statut
        or "En attente"
    )

    # -----------------------------------------------------
    # Même statut
    # -----------------------------------------------------

    if ancien_statut == nouveau_statut:

        raise ValueError(
            "Le nouveau statut est identique à l'ancien"
        )

    # -----------------------------------------------------
    # Modifier
    # -----------------------------------------------------

    reparation.statut = (
        nouveau_statut
    )

    # -----------------------------------------------------
    # Synchroniser resolu
    # -----------------------------------------------------

    reparation.resolu = (
        nouveau_statut == "Terminé"
    )

    # -----------------------------------------------------
    # Historique
    # -----------------------------------------------------

    create_historique(

        db=db,

        reparation_id=reparation.id,

        ancien_statut=ancien_statut,

        nouveau_statut=nouveau_statut,

        utilisateur_id=utilisateur_id

    )

    # -----------------------------------------------------
    # Commit
    # -----------------------------------------------------

    db.commit()

    db.refresh(
        reparation
    )

    return reparation
