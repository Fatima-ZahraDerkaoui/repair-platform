from sqlalchemy.orm import Session

from app.models.reparation import Reparation

from app.schemas.reparation import (
    ReparationCreate,
    ReparationUpdate
)

from app.services.dossier import (
    generer_numero_dossier
)

from app.services.qr_code import (
    generer_qr_code
)

from app.services.fiche_pdf import (
    generer_fiche_pdf
)

from app.crud.historique_statut import (
    create_historique
)

import os


def create_reparation(

    db: Session,

    reparation: ReparationCreate

):

    nouvelle = Reparation(

        **reparation.model_dump()

    )

    db.add(nouvelle)

    db.commit()

    db.refresh(nouvelle)


    # NUMÉRO DOSSIER

    nouvelle.numero_dossier = (

        generer_numero_dossier(

            nouvelle.id

        )

    )


    # QR CODE

    nouvelle.qr_code = (

        generer_qr_code(

            nouvelle.numero_dossier

        )

    )


    db.commit()

    db.refresh(nouvelle)


    # CLIENT

    client = nouvelle.client


    # PDF

    dossier_fiches = "uploads/fiches"

    os.makedirs(

        dossier_fiches,

        exist_ok=True

    )


    chemin_fiche = os.path.join(

        dossier_fiches,

        f"{nouvelle.numero_dossier}.pdf"

    )


    generer_fiche_pdf(

        reparation=nouvelle,

        client=client,

        chemin_fichier=chemin_fiche

    )


    return nouvelle


def get_reparations(

    db: Session

):

    return (

        db.query(Reparation)

        .all()

    )


def get_reparation(

    db: Session,

    id: int

):

    return (

        db.query(Reparation)

        .filter(

            Reparation.id == id

        )

        .first()

    )


def get_reparation_by_numero(

    db: Session,

    numero_dossier: str

):

    return (

        db.query(Reparation)

        .filter(

            Reparation.numero_dossier

            == numero_dossier

        )

        .first()

    )


def update_reparation(

    db: Session,

    id: int,

    data: ReparationUpdate

):

    reparation = get_reparation(

        db,

        id

    )

    if not reparation:

        return None


    for key, value in data.model_dump(

        exclude_unset=True

    ).items():

        setattr(

            reparation,

            key,

            value

        )


    db.commit()

    db.refresh(reparation)

    return reparation


def delete_reparation(

    db: Session,

    id: int

):

    reparation = get_reparation(

        db,

        id

    )

    if not reparation:

        return None


    db.delete(reparation)

    db.commit()

    return reparation


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