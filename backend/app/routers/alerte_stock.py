from fastapi import (

    APIRouter,

    Depends,

    HTTPException

)

from sqlalchemy.orm import Session


from app.database.database import get_db


from app.schemas.alerte_stock import (

    AlerteStockResponse

)


from app.crud.alerte_stock import (

    get_alertes_stock,

    get_alertes_non_lues,

    marquer_alerte_lue

)


router = APIRouter(

    prefix="/alertes-stock",

    tags=["Alertes Stock"]

)

@router.get(

    "/",

    response_model=list[AlerteStockResponse]

)

def lire_alertes(

    db: Session = Depends(get_db)

):

    return get_alertes_stock(db)

@router.get(

    "/non-lues",

    response_model=list[AlerteStockResponse]

)

def lire_alertes_non_lues(

    db: Session = Depends(get_db)

):

    return get_alertes_non_lues(db)

@router.patch(

    "/{alerte_id}/lire",

    response_model=AlerteStockResponse

)

def marquer_lue(

    alerte_id: int,

    db: Session = Depends(get_db)

):

    alerte = marquer_alerte_lue(

        db,

        alerte_id

    )

    if not alerte:

        raise HTTPException(

            status_code=404,

            detail="Alerte introuvable"

        )

    return alerte