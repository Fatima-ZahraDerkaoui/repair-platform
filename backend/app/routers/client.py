from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.client import (
    ClientCreate,
    ClientResponse
)

from app.crud.client import (
    create_client,
    get_clients,
    get_client,
    update_client,
    delete_client
)

router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)

@router.post(
    "/",
    response_model=ClientResponse
)
def create(
    client: ClientCreate,
    db: Session = Depends(get_db)
):

    return create_client(db, client)

@router.get(
    "/",
    response_model=list[ClientResponse]
)
def read_all(
    db: Session = Depends(get_db)
):

    return get_clients(db)

@router.get(
    "/{client_id}",
    response_model=ClientResponse
)
def read_one(
    client_id: int,
    db: Session = Depends(get_db)
):

    client = get_client(db, client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable"
        )

    return client

@router.put(
    "/{client_id}",
    response_model=ClientResponse
)
def update(
    client_id: int,
    client: ClientCreate,
    db: Session = Depends(get_db)
):

    updated = update_client(
        db,
        client_id,
        client
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable"
        )

    return updated

@router.delete("/{client_id}")
def delete(
    client_id: int,
    db: Session = Depends(get_db)
):

    deleted = delete_client(
        db,
        client_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable"
        )

    return {
        "message": "Client supprimé avec succès"
    }


