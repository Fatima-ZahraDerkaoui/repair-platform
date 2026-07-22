from fastapi import (

    APIRouter,

    Depends,

    HTTPException,

    status

)

from sqlalchemy.orm import Session


from app.database.database import get_db


from app.schemas.stock import (

    StockCreate,

    StockUpdate,

    StockResponse

)


from app.crud.stock import (

    create_stock,

    get_stocks,

    get_stock,

    update_stock,

    delete_stock

)


router = APIRouter(

    prefix="/stock",

    tags=["Stock"]

)


@router.post(

    "/",

    response_model=StockResponse,

    status_code=status.HTTP_201_CREATED

)

def create(

    data: StockCreate,

    db: Session = Depends(get_db)

):

    return create_stock(

        db,

        data

    )

@router.get(

    "/",

    response_model=list[StockResponse]

)

def read_all(

    db: Session = Depends(get_db)

):

    return get_stocks(db)


@router.get(

    "/{stock_id}",

    response_model=StockResponse

)

def read_one(

    stock_id: int,

    db: Session = Depends(get_db)

):

    piece = get_stock(

        db,

        stock_id

    )


    if not piece:

        raise HTTPException(

            status_code=404,

            detail="Pièce introuvable"

        )


    return piece

@router.put(

    "/{stock_id}",

    response_model=StockResponse

)

def update(

    stock_id: int,

    data: StockUpdate,

    db: Session = Depends(get_db)

):

    piece = update_stock(

        db,

        stock_id,

        data

    )


    if not piece:

        raise HTTPException(

            status_code=404,

            detail="Pièce introuvable"

        )


    return piece

@router.delete(

    "/{stock_id}"

)

def delete(

    stock_id: int,

    db: Session = Depends(get_db)

):

    piece = delete_stock(

        db,

        stock_id

    )


    if not piece:

        raise HTTPException(

            status_code=404,

            detail="Pièce introuvable"

        )


    return {

        "message":
        "Pièce supprimée avec succès"

    }