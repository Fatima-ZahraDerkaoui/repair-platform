from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)

from PySide6.QtCore import Qt


class LoadingWidget(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        self.label = QLabel("Analyse OCR en cours...")

        self.label.setAlignment(Qt.AlignCenter)

        self.label.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            color:#2563eb;
        """)

        layout.addStretch()

        layout.addWidget(self.label)

        layout.addStretch()

        self.hide()

    def start(self):

        self.show()

    def stop(self):

        self.hide()