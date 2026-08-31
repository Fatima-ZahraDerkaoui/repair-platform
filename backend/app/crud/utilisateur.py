import hashlib
import os
from sqlalchemy.orm import Session
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurUpdate


def hash_password(password: str) -> str:
    """Hache le mot de passe de manière sécurisée (SHA-256 avec Salt)."""
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie le mot de passe saisi."""
    if not hashed_password:
        return False
    
    # Si le mot de passe en BDD n'est pas encore haché (ex: "123456")
    if "$" not in hashed_password:
        return plain_password == hashed_password

    try:
        salt, stored_hash = hashed_password.split("$", 1)
        computed_hash = hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
        return computed_hash == stored_hash
    except ValueError:
        return plain_password == hashed_password


def create_utilisateur(db: Session, utilisateur: UtilisateurCreate):
    data = utilisateur.model_dump()
    if data.get("password"):
        data["password"] = hash_password(data["password"])

    nouveau = Utilisateur(**data)
    db.add(nouveau)
    db.commit()
    db.refresh(nouveau)
    return nouveau


def authenticate_utilisateur(db: Session, email: str, password: str):
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user


def get_utilisateurs(db: Session):
    return db.query(Utilisateur).all()


def get_utilisateur(db: Session, utilisateur_id: int):
    return db.query(Utilisateur).filter(Utilisateur.id == utilisateur_id).first()


def update_utilisateur(db: Session, utilisateur_id: int, data: UtilisateurUpdate):
    utilisateur = get_utilisateur(db, utilisateur_id)
    if not utilisateur:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        update_data["password"] = hash_password(update_data["password"])

    for key, value in update_data.items():
        if value is not None:
            setattr(utilisateur, key, value)

    db.commit()
    db.refresh(utilisateur)
    return utilisateur


def delete_utilisateur(db: Session, utilisateur_id: int):
    utilisateur = get_utilisateur(db, utilisateur_id)
    if not utilisateur:
        return None

    db.delete(utilisateur)
    db.commit()
    return utilisateur
