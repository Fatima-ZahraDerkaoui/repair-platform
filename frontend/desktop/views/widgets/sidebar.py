from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class Sidebar(QWidget):
    page_changed = Signal(str)
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.buttons = {}
        self.active_page = "dashboard"
        self.init_ui()

    def init_ui(self):
        # Style global du menu latéral (Fond sombre profond pour faire ressortir le blanc)
        self.setStyleSheet("""
            Sidebar {
                background-color: #0B0F19;
                border-right: 1px solid #1E293B;
            }
            QLabel#logoTitle {
                color: #1E293B;
                font-size: 19px;
                font-weight: 900;
                letter-spacing: 1px;
            }
            QLabel#logoSubtitle {
                color: #38BDF8;
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 1.5px;
                margin-top: 2px;
            }
            QFrame#separator {
                background-color: #1E293B;
                max-height: 1px;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding-left: 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #FFFFFF;
            }
            QPushButton[active="true"] {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: 700;
            }
            QPushButton#btnQuit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton#btnQuit:hover {
                background-color: #DC2626;
                color: #FFFFFF;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(6)

        # -----------------------------------------------------
        # LOGO & EN-TÊTE : REPAIR PLATFORM - DAY MACHINES
        # -----------------------------------------------------
        logo_container = QVBoxLayout()
        logo_container.setSpacing(0)

        logo_title = QLabel("REPAIR PLATFORM")
        logo_title.setObjectName("logoTitle")

        logo_subtitle = QLabel("DAY MACHINES")
        logo_subtitle.setObjectName("logoSubtitle")

        logo_container.addWidget(logo_title)
        logo_container.addWidget(logo_subtitle)
        layout.addLayout(logo_container)

        layout.addSpacing(16)

        separator = QFrame()
        separator.setObjectName("separator")
        layout.addWidget(separator)

        layout.addSpacing(12)

        # -----------------------------------------------------
        # NAVIGATION
        # -----------------------------------------------------
        items = [
            ("🏠   Tableau de bord", "dashboard"),
            ("🔧   Nouvelle réparation", "nouvelle_reparation"),
            ("📁   Dossiers", "dossiers"),
            ("🧾   Factures", "factures"),
            ("📦   Stock & Pièces", "stock"),
            ("⚙   Administration", "administration"),
        ]

        for text, page in items:
            self.add_nav_button(layout, text, page)

        layout.addStretch()

        # -----------------------------------------------------
        # BOUTON QUITTER / DÉCONNEXION
        # -----------------------------------------------------
        btn_quitter = QPushButton("🚪   Déconnexion / Quitter")
        btn_quitter.setObjectName("btnQuit")
        btn_quitter.setMinimumHeight(42)
        btn_quitter.setCursor(Qt.PointingHandCursor)
        btn_quitter.clicked.connect(self.quit_requested.emit)
        layout.addWidget(btn_quitter)

        # Sélectionner le dashboard par défaut
        self.set_active_page("dashboard")

    def add_nav_button(self, layout, text, page_name):
        btn = QPushButton(text)
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("active", False)
        btn.clicked.connect(lambda: self.on_button_clicked(page_name))
        
        layout.addWidget(btn)
        self.buttons[page_name] = btn

    def on_button_clicked(self, page_name):
        self.set_active_page(page_name)
        self.page_changed.emit(page_name)

    def set_active_page(self, page_name):
        self.active_page = page_name
        for p_name, btn in self.buttons.items():
            is_active = (p_name == page_name)
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
