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
        self.setFixedWidth(250)
        self.buttons = {}
        self.active_page = "dashboard"
        self.init_ui()

    def init_ui(self):
        # Arrière-plan BLANC PUR avec bordure droite épurée
        self.setStyleSheet("""
            Sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #E2E8F0;
            }
            QLabel#logoTitle {
                color: #0F172A;
                font-size: 17px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }
            QLabel#logoSubtitle {
                color: #2563EB;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.5px;
                margin-top: 2px;
            }
            QFrame#separator {
                background-color: #E2E8F0;
                max-height: 1px;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                color: #475569;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding-left: 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F8FAFC;
                color: #0F172A;
            }
            QPushButton[active="true"] {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: 700;
            }
            QPushButton#btnQuit {
                background-color: #FEF2F2;
                color: #DC2626;
                border: 1px solid #FECACA;
                border-radius: 6px;
                font-weight: 600;
                text-align: center;
                padding-left: 0px;
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
        # NAVIGATION (SANS EMOJIS)
        # -----------------------------------------------------
        items = [
            ("Tableau de bord", "dashboard"),
            ("Nouvelle réparation", "nouvelle_reparation"),
            ("Dossiers", "dossiers"),
            ("Factures", "factures"),
            ("Stock & Pièces", "stock"),
            ("Administration", "administration"),
        ]

        for text, page in items:
            self.add_nav_button(layout, text, page)

        layout.addStretch()

        # -----------------------------------------------------
        # BOUTON QUITTER / DÉCONNEXION
        # -----------------------------------------------------
        btn_quitter = QPushButton("Déconnexion")
        btn_quitter.setObjectName("btnQuit")
        btn_quitter.setMinimumHeight(40)
        btn_quitter.setCursor(Qt.PointingHandCursor)
        btn_quitter.clicked.connect(self.quit_requested.emit)
        layout.addWidget(btn_quitter)

        # Sélectionner le dashboard par défaut
        self.set_active_page("dashboard")

    def add_nav_button(self, layout, text, page_name):
        btn = QPushButton(text)
        btn.setMinimumHeight(42)
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
            