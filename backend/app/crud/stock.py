from sqlalchemy.orm import Session

from app.models.stock import Stock

from app.schemas.stock import (
    StockCreate,
    StockUpdate
)


# CREATE
def create_stock(

    db: Session,

    data: StockCreate

):

    nouvelle_piece = Stock(

        **data.model_dump()

    )

    db.add(nouvelle_piece)

    db.commit()

    db.refresh(nouvelle_piece)

    return nouvelle_piece


# READ ALL
def get_stocks(

    db: Session

):

    return (

        db.query(Stock)

        .order_by(
            Stock.nom_piece
        )

        .all()

    )


# READ ONE
def get_stock(

    db: Session,

    stock_id: int

):

    return (

        db.query(Stock)

        .filter(

            Stock.id == stock_id

        )

        .first()

    )


# UPDATE
def update_stock(

    db: Session,

    stock_id: int,

    data: StockUpdate

):

    piece = get_stock(

        db,

        stock_id

    )


    if not piece:

        return None


    donnees = data.model_dump(

        exclude_unset=True

    )


    for key, value in donnees.items():

        setattr(

            piece,

            key,

            value

        )


    db.commit()

    db.refresh(piece)


    return piece


# DELETE
def delete_stock(

    db: Session,

    stock_id: int

):

    piece = get_stock(

        db,

        stock_id

    )


    if not piece:

        return None


    db.delete(piece)

    db.commit()


    return piece