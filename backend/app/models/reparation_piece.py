from sqlalchemy import (
    ForeignKey,
    Integer,
    Numeric
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database.database import Base


class ReparationPiece(Base):

    __tablename__ = "reparation_piece"

    id: Mapped[int] = mapped_column(primary_key=True)

    reparation_id: Mapped[int] = mapped_column(
        ForeignKey("reparation.id")
    )

    piece_id: Mapped[int] = mapped_column(
        ForeignKey("stock.id")
    )

    quantite: Mapped[int] = mapped_column(Integer)

    prix_utilise: Mapped[float] = mapped_column(
        Numeric(10,2)
    )

    reparation = relationship(
        "Reparation",
        back_populates="pieces"
    )

    piece = relationship(
        "Stock",
        back_populates="reparations"
    )