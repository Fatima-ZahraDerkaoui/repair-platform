from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Fournisseur(Base):
    __tablename__ = "fournisseur"

    id: Mapped[int] = mapped_column(primary_key=True)

    nom: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    adresse: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    ville: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    pays: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    telephone: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    fax: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    site_web: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    ice: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True
    )

    identifiant_fiscal: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    rc: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    patente: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    cnss: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    rib: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    factures = relationship(
        "Facture",
        back_populates="fournisseur"
    )