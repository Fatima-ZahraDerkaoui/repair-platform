from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame
)

from PySide6.QtCore import Qt


class MenuPrincipal(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.init_ui()

    # =========================================================
    # UI
    # =========================================================

    def init_ui(self):

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout.setSpacing(20)

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        titre = QLabel(
            "Tableau de bord"
        )

        titre.setStyleSheet("""
            QLabel {
                font-size: 30px;
                font-weight: bold;
            }
        """)

        layout.addWidget(
            titre
        )

        sous_titre = QLabel(
            "Vue générale de l'activité de Repair Platform"
        )

        sous_titre.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #6b7280;
            }
        """)

        layout.addWidget(
            sous_titre
        )

        # -----------------------------------------------------
        # STATISTIQUES
        # -----------------------------------------------------

        stats_layout = QHBoxLayout()

        stats_layout.setSpacing(15)

        stats_layout.addWidget(
            self.create_stat_card(
                "Réparations",
                "0"
            )
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Factures",
                "0"
            )
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Stock",
                "0"
            )
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Dossiers ouverts",
                "0"
            )
        )

        layout.addLayout(
            stats_layout
        )

        # -----------------------------------------------------
        # ESPACE CENTRAL
        # -----------------------------------------------------

        information = QFrame()

        information.setFrameShape(
            QFrame.StyledPanel
        )

        information_layout = QVBoxLayout(
            information
        )

        titre_info = QLabel(
            "Bienvenue dans Repair Platform"
        )

        titre_info.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
            }
        """)

        information_layout.addWidget(
            titre_info
        )

        description = QLabel(
            "Utilisez le menu de navigation pour accéder "
            "aux réparations, factures, dossiers et stock."
        )

        description.setWordWrap(
            True
        )

        description.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #6b7280;
            }
        """)

        information_layout.addWidget(
            description
        )

        information_layout.addStretch()

        layout.addWidget(
            information
        )

        layout.addStretch()

    # =========================================================
    # STAT CARD
    # =========================================================

    def create_stat_card(
        self,
        title,
        value
    ):

        card = QFrame()

        card.setFrameShape(
            QFrame.StyledPanel
        )

        card.setMinimumHeight(
            120
        )

        layout = QVBoxLayout(
            card
        )

        value_label = QLabel(
            value
        )

        value_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
            }
        """)

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
            }
        """)

        layout.addWidget(
            value_label
        )

        layout.addWidget(
            title_label
        )

        return card