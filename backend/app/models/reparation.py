from datetime import datetime
from sqlalchemy import Enum
from app.core.status import StatutReparation

from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
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


class Reparation(Base):

    __tablename__ = "reparation"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("client.id")
    )

    receptionniste_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.id")
    )

    date_reception: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    type_materiel: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    systeme_exploitation: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    version_office: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    origine_probleme: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    probleme: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    diagnostic: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    intervention: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    pieces_defectueuses: Mapped[str | None] = mapped_column(Text, nullable=True)

    remarques: Mapped[str | None] = mapped_column(Text, nullable=True)

    mot_de_passe_pc: Mapped[str | None] = mapped_column(String(255), nullable=True)

    urgent: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    resolu: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    statut: Mapped[str] = mapped_column(
        String(30),
        default="En attente"
    )

    numero_dossier: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True
    )

    qr_code: Mapped[str | None] = mapped_column(String(255))

    texte_ocr: Mapped[str | None] = mapped_column(Text)

    delai_estime: Mapped[int | None] = mapped_column(Integer)

    cout_estime: Mapped[float | None] = mapped_column(Numeric(10,2))

    cout_reel: Mapped[float | None] = mapped_column(Numeric(10,2))

    date_fin: Mapped[datetime | None] = mapped_column(DateTime)

    client = relationship(
        "Client",
        back_populates="reparations"
    )

    receptionniste = relationship(
        "Utilisateur",
        back_populates="reparations"
    )

    pieces = relationship(
        "ReparationPiece",
        back_populates="reparation"
    )

    historique = relationship(
        "HistoriqueStatut",
        back_populates="reparation",
        cascade="all, delete-orphan"
    )
'''
    notifications = relationship(
        "Notification",
        back_populates="reparation"
    )

    statut: Mapped[StatutReparation] = mapped_column(
        Enum(StatutReparation),
        default=StatutReparation.EN_ATTENTE
    )
'''
