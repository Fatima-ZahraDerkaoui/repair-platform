from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.facture import Facture
from app.models.facture_ligne import FactureLigne

from app.schemas.facture import (
    FactureCreate,
    FactureUpdate
)

from app.schemas.facture_ligne import (
    FactureLigneCreate,
    FactureLigneUpdate
)


# ==========================================================
# FACTURE
# ==========================================================

def create(
    db: Session,
    data: FactureCreate
) -> Facture:

    facture = Facture(
        fournisseur_id=data.fournisseur_id,
        numero=data.numero,
        date_facture=data.date_facture,
        total_ht=data.total_ht,
        total_tva=data.total_tva,
        total_ttc=data.total_ttc,
        statut=data.statut,
        texte_ocr=data.texte_ocr,
        chemin_document=data.chemin_document
    )

    for ligne_data in data.lignes:

        ligne = FactureLigne(
            **ligne_data.model_dump()
        )

        facture.lignes.append(ligne)

    db.add(facture)

    db.commit()

    db.refresh(facture)

    return facture


def get_by_id(
    db: Session,
    facture_id: int
) -> Facture | None:

    result = db.execute(
        select(Facture)
        .options(
            selectinload(Facture.lignes),
            selectinload(Facture.fournisseur)
        )
        .where(
            Facture.id == facture_id
        )
    )

    return result.scalar_one_or_none()


def get_all(
    db: Session
) -> list[Facture]:

    result = db.execute(
        select(Facture)
        .options(
            selectinload(Facture.lignes),
            selectinload(Facture.fournisseur)
        )
        .order_by(
            Facture.id.desc()
        )
    )

    return list(result.scalars().unique().all())


def get_by_numero(
    db: Session,
    numero: str
) -> Facture | None:

    result = db.execute(
        select(Facture)
        .options(
            selectinload(Facture.lignes)
        )
        .where(
            Facture.numero == numero
        )
    )

    return result.scalar_one_or_none()


def update(
    db: Session,
    facture: Facture,
    data: FactureUpdate
) -> Facture:

    values = data.model_dump(
        exclude_unset=True
    )

    for field, value in values.items():

        setattr(
            facture,
            field,
            value
        )

    db.commit()

    db.refresh(facture)

    return facture


def delete(
    db: Session,
    facture: Facture
) -> None:

    db.delete(facture)

    db.commit()


# ==========================================================
# FACTURE LIGNE
# ==========================================================

def add_ligne(
    db: Session,
    facture_id: int,
    data: FactureLigneCreate
) -> FactureLigne:

    ligne = FactureLigne(
        facture_id=facture_id,
        **data.model_dump()
    )

    db.add(ligne)

    db.commit()

    db.refresh(ligne)

    return ligne


def get_ligne(
    db: Session,
    ligne_id: int
) -> FactureLigne | None:

    return db.get(
        FactureLigne,
        ligne_id
    )


def update_ligne(
    db: Session,
    ligne: FactureLigne,
    data: FactureLigneUpdate
) -> FactureLigne:

    values = data.model_dump(
        exclude_unset=True
    )

    for field, value in values.items():

        setattr(
            ligne,
            field,
            value
        )

    db.commit()

    db.refresh(ligne)

    return ligne


def delete_ligne(
    db: Session,
    ligne: FactureLigne
) -> None:

    db.delete(ligne)

    db.commit()