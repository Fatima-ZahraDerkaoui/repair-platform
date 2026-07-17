from datetime import datetime

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

    id: Mapped[int] = mapped_column(primary_key=True)

    nom_piece: Mapped[str] = mapped_column(String(150))

    reference: Mapped[str | None] = mapped_column(String(100))

    categorie: Mapped[str | None] = mapped_column(String(100))

    quantite: Mapped[int] = mapped_column(Integer)

    seuil_min: Mapped[int] = mapped_column(Integer)

    prix_unitaire: Mapped[float] = mapped_column(
        Numeric(10,2)
    )

    fournisseur: Mapped[str | None] = mapped_column(
        String(150)
    )

    date_ajout: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    reparations = relationship(
        "ReparationPiece",
        back_populates="piece"
    )