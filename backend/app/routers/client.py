from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.client import Client
from sqlalchemy.orm import Session
from app.models.client import Client
from app.database.database import get_db
from app.schemas.client import ClientGetOrCreate
from app.schemas.client import (
    ClientCreate,
    ClientResponse
)

router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
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

@router.get("/search")
def rechercher_client(
    nom: str = Query(...),
    db: Session = Depends(get_db)
):

    client = (
        db.query(Client)
        .filter(
            Client.nom.ilike(f"%{nom}%")
        )
        .first()
    )

    if client is None:
        return None

    return {
        "id": client.id,
        "nom": client.nom,
        "telephone": client.telephone,
        "email": client.email,
        "adresse": client.adresse
    }

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

@router.post(
    "/get-or-create",
    response_model=ClientResponse
)
def get_or_create_client(

    data: ClientGetOrCreate,

    db: Session = Depends(get_db)

):

    client = (

        db.query(Client)

        .filter(

            Client.nom == data.nom,

            Client.telephone == data.telephone

        )

        .first()

    )


    if client:

        return client


    nouveau_client = Client(

        nom=data.nom,

        telephone=data.telephone

    )


    db.add(nouveau_client)

    db.commit()

    db.refresh(nouveau_client)


    return nouveau_client
