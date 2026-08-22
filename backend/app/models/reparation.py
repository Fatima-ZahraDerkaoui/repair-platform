from datetime import datetime

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

    # =========================================================
    # IDENTIFICATION
    # =========================================================

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

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

    # =========================================================
    # MATÉRIEL
    # =========================================================

    type_materiel: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    marque: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    modele: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    numero_serie: Mapped[str | None] = mapped_column(
        String(150),
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

    mot_de_passe_pc: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # =========================================================
    # PROBLÈME
    # =========================================================

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

    pieces_defectueuses: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    accessoires: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    remarques: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # =========================================================
    # ÉTAT
    # =========================================================

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

    # =========================================================
    # DOSSIER
    # =========================================================

    numero_dossier: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True
    )

    qr_code: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    texte_ocr: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # =========================================================
    # ESTIMATION
    # =========================================================

    delai_estime: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    cout_estime: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    # =========================================================
    # FIN DE RÉPARATION
    # =========================================================

    cout_reel: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    date_fin: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # =========================================================
    # RELATIONS
    # =========================================================

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
        back_populates="reparation",
        cascade="all, delete-orphan"
    )

    historique = relationship(
        "HistoriqueStatut",
        back_populates="reparation",
        cascade="all, delete-orphan"
    )
    