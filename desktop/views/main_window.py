from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)

from views.nouvelle_reparation import NouvelleReparation


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Repair Platform - Réception"
        )

        self.resize(
            1000,
            700
        )

        self.init_ui()


    def init_ui(self):

        widget = QWidget()

        layout = QVBoxLayout()

        titre = QLabel(
            "REPAIR PLATFORM"
        )

        titre.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            """
        )

        layout.addWidget(titre)


        sous_titre = QLabel(
            "Gestion intelligente des réparations informatiques"
        )

        layout.addWidget(sous_titre)


        bouton = QPushButton(

            "Nouvelle réparation"

        )

        bouton.clicked.connect(

            self.ouvrir_nouvelle_reparation

        )

        layout.addWidget(bouton)


        widget.setLayout(layout)

        self.setCentralWidget(widget)


    def ouvrir_nouvelle_reparation(self):

        self.page_reparation = (

            NouvelleReparation()

        )

        self.page_reparation.show()