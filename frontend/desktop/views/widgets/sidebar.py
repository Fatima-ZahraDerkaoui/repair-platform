from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame
)

from PySide6.QtCore import Signal, Qt


class Sidebar(QWidget):

    page_changed = Signal(str)
    quit_requested = Signal()

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setFixedWidth(240)

        self.init_ui()

    # =========================================================
    # UI
    # =========================================================

    def init_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            15,
            20,
            15,
            20
        )

        layout.setSpacing(8)

        # -----------------------------------------------------
        # LOGO
        # -----------------------------------------------------

        logo = QLabel("REPAIR\nPLATFORM")

        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 20px;
            }
        """)

        layout.addWidget(logo)

        separator = QFrame()

        separator.setFrameShape(
            QFrame.HLine
        )

        layout.addWidget(separator)

        # -----------------------------------------------------
        # NAVIGATION
        # -----------------------------------------------------

        self.add_button(
            layout,
            "🏠  Tableau de bord",
            "dashboard"
        )

        self.add_button(
            layout,
            "🔧  Nouvelle réparation",
            "nouvelle_reparation"
        )

        self.add_button(
            layout,
            "📁  Dossiers",
            "dossiers"
        )

        self.add_button(
            layout,
            "🧾  Factures",
            "factures"
        )

        self.add_button(
            layout,
            "📦  Stock",
            "stock"
        )

        self.add_button(
            layout,
            "⚙  Administration",
            "administration"
        )

        layout.addStretch()

        # -----------------------------------------------------
        # QUITTER
        # -----------------------------------------------------

        bouton_quitter = QPushButton(
            "🚪  Quitter"
        )

        bouton_quitter.setMinimumHeight(45)

        bouton_quitter.clicked.connect(
            self.quit_requested.emit
        )

        layout.addWidget(
            bouton_quitter
        )

    # =========================================================
    # BUTTON
    # =========================================================

    def add_button(
        self,
        layout,
        text,
        page
    ):

        button = QPushButton(text)

        button.setMinimumHeight(45)

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.clicked.connect(
            lambda: self.page_changed.emit(page)
        )

        layout.addWidget(button)