from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate

def create_client(db: Session, client: ClientCreate):

    nouveau_client = Client(
        nom=client.nom,
        telephone=client.telephone,
        email=client.email,
        adresse=client.adresse
    )

    db.add(nouveau_client)

    db.commit()

    db.refresh(nouveau_client)

    return nouveau_client

def get_clients(db: Session):

    return db.query(Client).all()

def get_client(db: Session, client_id: int):

    return (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )

def update_client(
    db: Session,
    client_id: int,
    client_data: ClientCreate
):

    client = get_client(db, client_id)

    if client is None:
        return None

    client.nom = client_data.nom
    client.telephone = client_data.telephone
    client.email = client_data.email
    client.adresse = client_data.adresse

    db.commit()

    db.refresh(client)

    return client

def delete_client(
    db: Session,
    client_id: int
):

    client = get_client(db, client_id)

    if client is None:
        return None

    db.delete(client)

    db.commit()

    return client

