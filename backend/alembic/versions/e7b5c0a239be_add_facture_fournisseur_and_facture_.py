"""add facture fournisseur and facture ligne

Revision ID: e7b5c0a239be
Revises: 2b3543e67baf
Create Date: 2026-08-15 11:54:48.861497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b5c0a239be'
down_revision: Union[str, Sequence[str], None] = '2b3543e67baf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ==========================================================
# UPGRADE
# ==========================================================

def upgrade() -> None:

    # ======================================================
    # FOURNISSEUR
    # ======================================================

    op.create_table(
        "fournisseur",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "nom",
            sa.String(length=150),
            nullable=False
        ),

        sa.Column(
            "adresse",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "ville",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "pays",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "telephone",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "fax",
            sa.String(length=50),
            nullable=True
        ),

        sa.Column(
            "email",
            sa.String(length=150),
            nullable=True
        ),

        sa.Column(
            "site_web",
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            "ice",
            sa.String(length=50),
            nullable=True
        ),

        sa.Column(
            "identifiant_fiscal",
            sa.String(length=50),
            nullable=True
        ),

        sa.Column(
            "rc",
            sa.String(length=50),
            nullable=True
        ),

        sa.Column(
            "patente",
            sa.String(length=50),
            nullable=True
        ),

        sa.Column(
            "cnss",
            sa.String(length=50),
            nullable=True
        ),

        sa.Column(
            "rib",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "date_creation",
            sa.DateTime(),
            nullable=False
        ),

        sa.UniqueConstraint(
            "ice",
            name="uq_fournisseur_ice"
        )
    )

    # ======================================================
    # FACTURE
    # ======================================================

    op.create_table(
        "facture",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "fournisseur_id",
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            "numero",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "date_facture",
            sa.DateTime(),
            nullable=True
        ),

        sa.Column(
            "total_ht",
            sa.Numeric(12, 2),
            nullable=True
        ),

        sa.Column(
            "total_tva",
            sa.Numeric(12, 2),
            nullable=True
        ),

        sa.Column(
            "total_ttc",
            sa.Numeric(12, 2),
            nullable=True
        ),

        sa.Column(
            "statut",
            sa.String(length=30),
            nullable=False,
            server_default="A_VALIDER"
        ),

        sa.Column(
            "texte_ocr",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "chemin_document",
            sa.String(length=500),
            nullable=True
        ),

        sa.Column(
            "date_creation",
            sa.DateTime(),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["fournisseur_id"],
            ["fournisseur.id"],
            name="fk_facture_fournisseur"
        )
    )

    # ======================================================
    # FACTURE LIGNE
    # ======================================================

    op.create_table(
        "facture_ligne",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "facture_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "stock_id",
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            "designation",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "reference",
            sa.String(length=150),
            nullable=True
        ),

        sa.Column(
            "quantite",
            sa.Numeric(10, 2),
            nullable=True
        ),

        sa.Column(
            "prix_unitaire",
            sa.Numeric(12, 2),
            nullable=True
        ),

        sa.Column(
            "total",
            sa.Numeric(12, 2),
            nullable=True
        ),

        sa.ForeignKeyConstraint(
            ["facture_id"],
            ["facture.id"],
            name="fk_facture_ligne_facture",
            ondelete="CASCADE"
        ),

        sa.ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            name="fk_facture_ligne_stock"
        )
    )


# ==========================================================
# DOWNGRADE
# ==========================================================

def downgrade() -> None:

    op.drop_table("facture_ligne")

    op.drop_table("facture")

    op.drop_table("fournisseur")