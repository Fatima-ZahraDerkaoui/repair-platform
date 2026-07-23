from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QMessageBox
)


class NouvelleReparation(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(

            "Nouvelle réparation"

        )

        self.resize(

            700,

            800

        )

        self.init_ui()


    def init_ui(self):

        layout = QVBoxLayout()


        form = QFormLayout()


        # CLIENT

        self.nom_client = QLineEdit()

        form.addRow(

            "Nom et prénom :",

            self.nom_client

        )


        self.telephone = QLineEdit()

        form.addRow(

            "Téléphone :",

            self.telephone

        )


        # MATERIEL

        self.type_materiel = QComboBox()

        self.type_materiel.addItems(

            [

                "PC",

                "PC Portable",

                "Imprimante",

                "Unité centrale",

                "Autre"

            ]

        )

        form.addRow(

            "Type matériel :",

            self.type_materiel

        )


        # SYSTEME

        self.systeme = QComboBox()

        self.systeme.addItems(

            [

                "Windows 10",

                "Windows 11",

                "Linux",

                "Autre"

            ]

        )

        form.addRow(

            "Système d'exploitation :",

            self.systeme

        )


        # OFFICE

        self.office = QComboBox()

        self.office.addItems(

            [

                "Office 2013",

                "Office 2024",

                "Microsoft 365",

                "Aucun"

            ]

        )

        form.addRow(

            "Office :",

            self.office

        )


        # ORIGINE

        self.origine = QComboBox()

        self.origine.addItems(

            [

                "Matériel",

                "Logiciel",

                "Réseau",

                "Virus",

                "Mise à jour",

                "Inconnue",

                "Autre"

            ]

        )

        form.addRow(

            "Origine du problème :",

            self.origine

        )


        # INTERVENTION

        self.intervention = QLineEdit()

        form.addRow(

            "Intervention :",

            self.intervention

        )


        # PROBLEME

        self.probleme = QTextEdit()

        form.addRow(

            "Problème constaté :",

            self.probleme

        )


        # PIECES

        self.pieces = QTextEdit()

        form.addRow(

            "Pièces défectueuses :",

            self.pieces

        )


        # REMARQUES

        self.remarques = QTextEdit()

        form.addRow(

            "Remarques :",

            self.remarques

        )


        # URGENT

        self.urgent = QCheckBox(

            "Réparation urgente"

        )

        form.addRow(

            self.urgent

        )


        layout.addLayout(form)


        # BOUTON

        bouton = QPushButton(

            "Créer le dossier de réparation"

        )

        bouton.clicked.connect(

            self.creer_reparation

        )

        layout.addWidget(bouton)


        self.setLayout(layout)


    def creer_reparation(self):

        QMessageBox.information(

            self,

            "Test",

            "Le formulaire est prêt."

        )