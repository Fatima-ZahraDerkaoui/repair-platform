from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from app.database.database import Base

from sqlalchemy.orm import relationship


class HistoriqueStatut(Base):

    __tablename__ = "historique_statut"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    reparation_id = Column(
        Integer,
        ForeignKey("reparation.id"),
        nullable=False
    )

    ancien_statut = Column(
        String(30),
        nullable=True
    )

    nouveau_statut = Column(
        String(30),
        nullable=False
    )

    utilisateur_id = Column(
        Integer,
        ForeignKey("utilisateur.id"),
        nullable=True
    )

    date_modification = Column(
        DateTime,
        server_default=func.now()
    )

    reparation = relationship(
        "Reparation",
        back_populates="historique"
    )

    utilisateur = relationship(
        "Utilisateur",
        back_populates="historiques"
    )