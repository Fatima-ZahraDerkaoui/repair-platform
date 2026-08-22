from datetime import datetime
from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.facture import (
    FactureCreate,
    FactureResponse
)

from app.schemas.facture_ligne import (
    FactureLigneCreate
)

from app.crud import facture as facture_crud


router = APIRouter(
    prefix="/factures",
    tags=["Factures"]
)


# =========================================================
# CREER FACTURE
# =========================================================

@router.post(
    "",
    response_model=FactureResponse,
    status_code=201
)
def creer_facture(
    data: FactureCreate,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # VERIFIER NUMERO
    # -----------------------------------------------------

    if data.numero:

        facture_existante = (
            facture_crud.get_by_numero(
                db,
                data.numero
            )
        )

        if facture_existante:

            raise HTTPException(
                status_code=409,
                detail=(
                    f"La facture {data.numero} "
                    "existe déjà."
                )
            )

    # -----------------------------------------------------
    # CREATION
    # -----------------------------------------------------

    facture = facture_crud.create(
        db,
        data
    )

    return facture
