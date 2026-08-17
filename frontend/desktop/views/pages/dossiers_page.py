from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)


class DossiersPage(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "Gestion des dossiers"
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
                "Module de gestion des dossiers de réparation."
            )
        )

        layout.addStretch()