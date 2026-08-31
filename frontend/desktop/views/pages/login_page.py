import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal

API_URL = "http://127.0.0.1:8000"


class LoginPage(QWidget):
    login_successful = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #0F172A;")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedWidth(380)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 16px;
                padding: 24px;
            }
            QLabel#title {
                font-size: 22px; font-weight: 800; color: #0F172A;
            }
            QLabel#subtitle {
                font-size: 13px; color: #64748B; margin-bottom: 12px;
            }
            QLineEdit {
                background-color: #F8FAFC; border: 1px solid #CBD5E1;
                border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #0F172A;
            }
            QLineEdit:focus { border: 1px solid #4F46E5; }
            QPushButton {
                background-color: #4F46E5; color: #FFFFFF;
                font-weight: 700; font-size: 14px; border: none;
                border-radius: 8px; padding: 12px; margin-top: 8px;
            }
            QPushButton:hover { background-color: #4338CA; }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        title = QLabel("REPAIR PLATFORM")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Accès réservé au personnel")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Adresse Email")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Mot de passe")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.returnPressed.connect(self.attempt_login)

        btn_login = QPushButton("Se Connecter")
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.clicked.connect(self.attempt_login)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.input_email)
        card_layout.addWidget(self.input_password)
        card_layout.addWidget(btn_login)

        main_layout.addWidget(card)

    def attempt_login(self):
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Attention", "Veuillez saisir votre email et mot de passe.")
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
            