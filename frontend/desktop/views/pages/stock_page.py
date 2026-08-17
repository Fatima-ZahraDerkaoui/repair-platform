from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)

from PySide6.QtCore import Qt


class StockPage(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "Gestion du stock"
        )

        title.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
        """)

        layout.addWidget(
            title
        )

        layout.addWidget(
            QLabel(
                "Module de gestion du stock."
            )
        )

        layout.addStretch()