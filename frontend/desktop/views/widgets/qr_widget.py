from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout

from PySide6.QtGui import QPixmap

from desktop.services.backend_api import BackendAPI


class QRWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.api = BackendAPI()

        self.session = None

        self.image = QLabel()

        self.url = QLabel()

        self.button = QPushButton(
            "Scanner une facture"
        )

        self.button.clicked.connect(
            self.start_session
        )

        layout = QVBoxLayout(self)

        layout.addWidget(self.image)

        layout.addWidget(self.url)

        layout.addWidget(self.button)

    # -----------------------------------------

    def start_session(self):

        self.session = self.api.create_facture_session()

        self.image.setPixmap(
            QPixmap(
                self.session["qr_code"]
            )
        )

        self.url.setText(
            self.session["mobile_url"]
        )