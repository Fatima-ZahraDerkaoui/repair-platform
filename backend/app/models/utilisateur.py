from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    nom: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[str] = mapped_column(String(30), nullable=False)

    telephone: Mapped[str] = mapped_column(String(20), nullable=True)

    reparations = relationship(
        "Reparation",
        back_populates="receptionniste"
    )

    historiques = relationship(
        "HistoriqueStatut"
    )