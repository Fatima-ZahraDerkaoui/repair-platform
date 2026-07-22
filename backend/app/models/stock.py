from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    DateTime
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database.database import Base


class Stock(Base):

    __tablename__ = "stock"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    nom_piece: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    categorie: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    quantite: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    seuil_min: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5
    )

    prix_unitaire: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    fournisseur: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    date_ajout: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    reparations = relationship(
        "ReparationPiece",
        back_populates="piece"
    )