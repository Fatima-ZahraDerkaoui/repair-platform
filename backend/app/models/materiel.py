from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Materiel(Base):
    __tablename__ = "materiel"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("client.id"),
        nullable=False
    )

    type_materiel: Mapped[str] = mapped_column(
        String(50)
    )

    marque: Mapped[str] = mapped_column(
        String(100)
    )

    modele: Mapped[str] = mapped_column(
        String(100)
    )

    numero_serie: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True
    )

    systeme_exploitation: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    version_office: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    client = relationship(
        "Client",
        back_populates="materiels"
    )

    reparations = relationship(
        "Reparation",
        back_populates="materiel"
    )