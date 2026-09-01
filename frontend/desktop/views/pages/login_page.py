import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal

API_URL = "http://127.0.0.1:8000"


class LoginPage(QWidget):
    login_successful = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Arrière-plan de la fenêtre
        self.setObjectName("loginPage")
        self.setStyleSheet("""
            QWidget#loginPage {
                background-color: #F1F5F9;
            }
            QFrame#loginCard {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
            }
            QLabel {
                background-color: transparent;
            }
            QLabel#brandIcon {
                font-size: 32px;
                background-color: #EEF2FF;
                border-radius: 12px;
                padding: 8px;
            }
            QLabel#title {
                font-size: 20px; 
                font-weight: 800; 
                color: #0F172A;
            }
            QLabel#subtitle {
                font-size: 13px; 
                color: #64748B; 
                font-weight: 500;
            }
            QLabel#fieldLabel {
                font-size: 12px;
                font-weight: 600;
                color: #334155;
            }
            QLineEdit {
                background-color: #F8FAFC; 
                border: 1px solid #CBD5E1;
                border-radius: 8px; 
                padding: 10px 14px; 
                font-size: 13px; 
                color: #0F172A;
            }
            QLineEdit:hover {
                border: 1px solid #94A3B8;
                background-color: #FFFFFF;
            }
            QLineEdit:focus { 
                border: 2px solid #2563EB; 
                background-color: #FFFFFF;
            }
            QPushButton#btnLogin {
                background-color: #2563EB; 
                color: #FFFFFF;
                font-weight: 700; 
                font-size: 14px; 
                border: none;
                border-radius: 8px; 
                padding: 12px; 
            }
            QPushButton#btnLogin:hover { 
                background-color: #1D4ED8; 
            }
            QPushButton#btnLogin:pressed { 
                background-color: #1E40AF; 
            }
            QLabel#footerText {
                font-size: 11px;
                color: #94A3B8;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Carte de connexion
        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(400)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(10)

        # En-tête : Icône
        header_box = QHBoxLayout()
        header_box.setAlignment(Qt.AlignCenter)
        brand_icon = QLabel("🛠️")
        brand_icon.setObjectName("brandIcon")
        header_box.addWidget(brand_icon)

        title = QLabel("Repair Platform")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Identifiez-vous pour accéder à l'atelier")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        # Champs de saisie
        lbl_email = QLabel("Adresse Email")
        lbl_email.setObjectName("fieldLabel")
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("nom@exemple.com")

        lbl_password = QLabel("Mot de passe")
        lbl_password.setObjectName("fieldLabel")
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("••••••••")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.returnPressed.connect(self.attempt_login)

        # Bouton
        btn_login = QPushButton("Se Connecter")
        btn_login.setObjectName("btnLogin")
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.clicked.connect(self.attempt_login)

        # Pied de carte
        footer = QLabel("v2.0 — Système de Gestion Interne")
        footer.setObjectName("footerText")
        footer.setAlignment(Qt.AlignCenter)

        # Assemblage
        card_layout.addLayout(header_box)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addWidget(lbl_email)
        card_layout.addWidget(self.input_email)
        card_layout.addWidget(lbl_password)
        card_layout.addWidget(self.input_password)
        card_layout.addSpacing(8)
        card_layout.addWidget(btn_login)
        card_layout.addSpacing(4)
        card_layout.addWidget(footer)

        main_layout.addWidget(card)

    def attempt_login(self):
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Attention", "Veuillez saisir votre email et votre mot de passe.")
            return

        try:
            res = requests.post(
                f"{API_URL}/utilisateurs/login",
                json={"email": email, "password": password},
                timeout=10
            )
            if res.ok:
                user_data = res.json().get("user", {})
                self.login_successful.emit(user_data)
            else:
                detail = res.json().get("detail", "Échec de connexion.")
                QMessageBox.warning(self, "Erreur d'accès", detail)
        except requests.RequestException as err:
            QMessageBox.critical(self, "Erreur Réseau", f"Impossible de joindre le serveur :\n{err}")
            