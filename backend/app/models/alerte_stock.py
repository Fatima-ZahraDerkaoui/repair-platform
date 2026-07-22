from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database.database import Base


class AlerteStock(Base):

    __tablename__ = "alerte_stock"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    piece_id: Mapped[int] = mapped_column(
        ForeignKey("stock.id"),
        nullable=False
    )

    reparation_id: Mapped[int | None] = mapped_column(
        ForeignKey("reparation.id"),
        nullable=True
    )

    quantite_demandee: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    quantite_disponible: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    statut: Mapped[str] = mapped_column(
        String(30),
        default="NON_LUE"
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    piece = relationship(
        "Stock"
    )