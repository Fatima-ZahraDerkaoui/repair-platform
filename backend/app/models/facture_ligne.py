from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Integer,
    Numeric,
    Text,
    String
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database.database import Base


class FactureLigne(Base):

    __tablename__ = "facture_ligne"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    facture_id: Mapped[int] = mapped_column(
        ForeignKey("facture.id", ondelete="CASCADE"),
        nullable=False
    )

    stock_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock.id"),
        nullable=True
    )

    designation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    reference: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    quantite: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    prix_unitaire: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    total: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    facture = relationship(
        "Facture",
        back_populates="lignes"
    )

    stock = relationship(
        "Stock"
    )