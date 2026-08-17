from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    Numeric,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database.database import Base


class Facture(Base):

    __tablename__ = "facture"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    fournisseur_id: Mapped[int | None] = mapped_column(
        ForeignKey("fournisseur.id"),
        nullable=True
    )

    numero: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    date_facture: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    total_ht: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    total_tva: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    total_ttc: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    statut: Mapped[str] = mapped_column(
        String(30),
        default="A_VALIDER",
        nullable=False
    )

    texte_ocr: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    chemin_document: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    fournisseur = relationship(
        "Fournisseur",
        back_populates="factures"
    )

    lignes = relationship(
        "FactureLigne",
        back_populates="facture",
        cascade="all, delete-orphan"
    )