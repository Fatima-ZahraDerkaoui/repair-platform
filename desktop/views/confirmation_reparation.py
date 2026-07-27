from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox
)

from PySide6.QtCore import Qt

import requests

import os

import tempfile


class ConfirmationReparation(QWidget):

    def __init__(

        self,

        data,

        parent=None

    ):

        super().__init__(parent)


        self.data = data


        self.setWindowTitle(

            "Dossier créé"

        )


        self.resize(

            500,

            600

        )


        self.init_ui()


    def init_ui(self):

        layout = QVBoxLayout()


        titre = QLabel(

            "DOSSIER CRÉÉ AVEC SUCCÈS"

        )


        titre.setAlignment(

            Qt.AlignCenter

        )


        titre.setStyleSheet(

            """

            font-size: 22px;

            font-weight: bold;

            padding: 20px;

            """

        )


        layout.addWidget(titre)


        numero = QLabel(

            f"Dossier : "

            f"{self.data.get('numero_dossier')}"

        )


        numero.setAlignment(

            Qt.AlignCenter

        )


        numero.setStyleSheet(

            """

            font-size: 20px;

            font-weight: bold;

            """

        )


        layout.addWidget(numero)


        informations = QLabel(

            f"""

            <b>Client :</b>

            {self.data.get('client_nom')}

            <br><br>


            <b>Téléphone :</b>

            {self.data.get('client_telephone')}

            <br><br>


            <b>Matériel :</b>

            {self.data.get('type_materiel')}

            <br><br>


            <b>Statut :</b>

            {self.data.get('statut')}

            """

        )


        informations.setStyleSheet(

            """

            font-size: 16px;

            padding: 20px;

            """

        )


        layout.addWidget(informations)


        layout.addStretch()


        bouton_imprimer = QPushButton(

            "🖨 Imprimer la fiche"

        )


        bouton_imprimer.setMinimumHeight(

            50

        )


        bouton_imprimer.clicked.connect(

            self.imprimer_fiche

        )


        layout.addWidget(

            bouton_imprimer

        )


        bouton_fermer = QPushButton(

            "Fermer"

        )


        bouton_fermer.clicked.connect(

            self.close

        )


        layout.addWidget(

            bouton_fermer

        )


        self.setLayout(layout)


    def imprimer_fiche(self):

        reparation_id = (

            self.data.get("id")

        )


        url = (

            "http://127.0.0.1:8000"

            f"/reparations/"

            f"{reparation_id}"

            "/fiche"

        )


        try:

            response = requests.get(

                url,

                timeout=30

            )


            if response.status_code != 200:

                QMessageBox.critical(

                    self,

                    "Erreur",

                    "Impossible de récupérer la fiche PDF."

                )

                return


            dossier_temp = (

                tempfile.gettempdir()

            )


            chemin_pdf = os.path.join(

                dossier_temp,

                (

                    f"{self.data.get('numero_dossier')}"

                    ".pdf"

                )

            )


            with open(

                chemin_pdf,

                "wb"

            ) as fichier:

                fichier.write(

                    response.content

                )


            os.startfile(

                chemin_pdf

            )


        except Exception as erreur:

            QMessageBox.critical(

                self,

                "Erreur",

                str(erreur)

            )