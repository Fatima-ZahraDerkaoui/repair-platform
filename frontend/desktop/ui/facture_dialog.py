from pathlib import Path

from PySide6.QtCore import Qt, QTimer

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox
)

from services.backend_api import BackendAPI
from ui.widgets.qr_widget import QrWidget


class FactureDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.session_id = None

        self.build_ui()

        self.create_scan_session()

        self.timer = QTimer(self)

        self.timer.timeout.connect(self.check_session_status)

        self.timer.start(2000)


    def build_ui(self):

        self.setWindowTitle("Ajouter une facture")

        self.resize(900, 600)


        main_layout = QHBoxLayout(self)


        # =============================
        # Partie gauche
        # =============================

        left = QVBoxLayout()

        title = QLabel("Acquisition de la facture")

        title.setStyleSheet("""
            font-size:20px;
            font-weight:bold;
        """)

        left.addWidget(title)

        left.addSpacing(20)


        self.phoneButton = QPushButton("📱 Scanner avec téléphone")

        self.pcButton = QPushButton("💻 Choisir une image")

        self.phoneButton.setMinimumHeight(45)

        self.pcButton.setMinimumHeight(45)

        left.addWidget(self.phoneButton)

        left.addWidget(self.pcButton)

        left.addStretch()


        # =============================
        # Partie droite
        # =============================

        self.qrWidget = QrWidget()


        main_layout.addLayout(left, 2)

        main_layout.addWidget(self.qrWidget, 3)


    def create_scan_session(self):

        try:

            data = BackendAPI.create_scan_session()

            self.session_id = data["session_id"]

            self.qrWidget.set_session(self.session_id)

            self.qrWidget.set_status("🟡 En attente du téléphone")


            qr_path = Path(data["qr_code"])

            self.qrWidget.set_qrcode(str(qr_path))


        except Exception as e:

            QMessageBox.critical(

                self,

                "Erreur",

                str(e)

            )

    def check_session_status(self):

        if not self.session_id:
            return

        try:

            data = BackendAPI.get_session_status(
                self.session_id
            )

            if not data["exists"]:

                self.qrWidget.set_status("❌ Session inexistante")

                return

            if data["closed"]:

                self.qrWidget.set_status("⚫ Session fermée")

                return

            if data["connected"]:

                self.qrWidget.set_status(
                    "🟢 Téléphone connecté"
                )

            else:

                self.qrWidget.set_status(
                    "🟡 En attente du téléphone"
                )

        except Exception:

            self.qrWidget.set_status(
                "🔴 Backend indisponible"
            )

    def closeEvent(self, event):

        self.timer.stop()

        if self.session_id:

            try:

                BackendAPI.close_session(
                    self.session_id
                )

            except Exception:
                pass

        event.accept()