from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QMessageBox,
    QLabel,
    QGroupBox,
    QGridLayout
)
from PySide6.QtCore import QTimer
import requests
import os
import subprocess

class NouvelleReparation(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "Nouvelle réparation"
        )

        self.resize(
            850,
            850
        )

        # Client trouvé dans la base
        self.client_existe = False

        self.client_id = None

        self.timer_client = QTimer()
        self.timer_client.setSingleShot(True)
        self.timer_client.timeout.connect(
            self.rechercher_client
        )

        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout()


        # ==================================================
        # INFORMATIONS CLIENT
        # ==================================================

        client_group = QGroupBox(
            "Informations client"
        )

        client_form = QFormLayout()


        # NOM CLIENT - OBLIGATOIRE

        self.nom_client = QLineEdit()

        self.nom_client.textChanged.connect(
            lambda: self.timer_client.start(500)
        )

        self.nom_client.setPlaceholderText(

            "Nom et prénom du client"

        )

        client_form.addRow(

            "Nom et prénom * :",

            self.nom_client

        )


        # TELEPHONE - OBLIGATOIRE

        self.telephone = QLineEdit()

        self.telephone.setPlaceholderText(

            "Exemple : 0661234567"

        )

        client_form.addRow(

            "Téléphone * :",

            self.telephone

        )


        # MESSAGE CLIENT

        self.client_info = QLabel()

        self.client_info.setStyleSheet(

            "color: #2563eb;"

        )

        client_form.addRow(

            "",

            self.client_info

        )


        client_group.setLayout(

            client_form

        )

        layout.addWidget(

            client_group

        )


        # ==================================================
        # INFORMATIONS MATERIEL
        # ==================================================

        materiel_group = QGroupBox(

            "Informations matériel"

        )

        materiel_form = QFormLayout()


        # TYPE MATERIEL - OBLIGATOIRE

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

        self.type_materiel.currentTextChanged.connect(

            self.gerer_type_materiel

        )

        materiel_form.addRow(

            "Type matériel * :",

            self.type_materiel

        )


        # SYSTEME

        self.systeme_label = QLabel(

            "Système d'exploitation :"

        )

        self.systeme = QComboBox()

        self.systeme.addItems(

            [

                "",

                "Windows 10",

                "Windows 11",

                "Linux",

                "Autre"

            ]

        )

        materiel_form.addRow(

            self.systeme_label,

            self.systeme

        )


        # OFFICE

        self.office_label = QLabel(

            "Office :"

        )

        self.office = QComboBox()

        self.office.addItems(

            [

                "",

                "Office 2013",

                "Office 2024",

                "Microsoft 365",

                "Aucun"

            ]

        )

        materiel_form.addRow(

            self.office_label,

            self.office

        )


        # MOT DE PASSE

        self.mot_de_passe = QLineEdit()

        self.mot_de_passe.setPlaceholderText(

            "Facultatif"

        )

        self.mot_de_passe.setEchoMode(

            QLineEdit.Password

        )

        materiel_form.addRow(

            "Mot de passe PC :",

            self.mot_de_passe

        )


        # MARQUE

        self.marque_label = QLabel(

            "Marque :"

        )

        self.marque = QLineEdit()

        materiel_form.addRow(

            self.marque_label,

            self.marque

        )


        # MODELE

        self.modele_label = QLabel(

            "Modèle :"

        )

        self.modele = QLineEdit()

        materiel_form.addRow(

            self.modele_label,

            self.modele

        )


        # NUMERO DE SERIE

        self.numero_serie_label = QLabel(

            "Numéro de série :"

        )

        self.numero_serie = QLineEdit()

        materiel_form.addRow(

            self.numero_serie_label,

            self.numero_serie

        )


        materiel_group.setLayout(

            materiel_form

        )

        layout.addWidget(

            materiel_group

        )


        # ==================================================
        # PROBLEME
        # ==================================================

        probleme_group = QGroupBox(

            "Informations sur le problème"

        )

        probleme_form = QFormLayout()


        # ORIGINE

        self.origine = QComboBox()

        self.origine.addItems(

            [

                "",

                "Matériel",

                "Logiciel",

                "Réseau",

                "Virus",

                "Mise à jour",

                "Inconnue",

                "Autre"

            ]

        )

        probleme_form.addRow(

            "Origine du problème :",

            self.origine

        )


        # INTERVENTION

        self.intervention = QComboBox()

        self.intervention.addItems(

            [

                "",

                "Réinstallation",

                "Désinstallation",

                "Dépannage",

                "Sauvegarde",

                "Récupération de données",

                "Nettoyage",

                "Formatage C",

                "Formatage D",

                "Configuration réseau",

                "Mise à jour",

                "Suppression de virus",

                "Autre"

            ]

        )

        probleme_form.addRow(

            "Intervention :",

            self.intervention

        )


        # PROBLEME CONSTATE

        self.probleme = QTextEdit()

        self.probleme.setPlaceholderText(

            "Décrire le problème constaté..."

        )

        self.probleme.setMaximumHeight(

            90

        )

        probleme_form.addRow(

            "Problème constaté :",

            self.probleme

        )


        # PIECES DEFECTUEUSES

        self.pieces = QTextEdit()

        self.pieces.setPlaceholderText(

            "Exemple : Disque dur, RAM..."

        )

        self.pieces.setMaximumHeight(

            70

        )

        probleme_form.addRow(

            "Pièces défectueuses :",

            self.pieces

        )


        # REMARQUES

        self.remarques = QTextEdit()

        self.remarques.setPlaceholderText(

            "Remarques supplémentaires..."

        )

        self.remarques.setMaximumHeight(

            70

        )

        probleme_form.addRow(

            "Remarques :",

            self.remarques

        )


        # URGENT

        self.urgent = QCheckBox(

            "Réparation urgente"

        )

        probleme_form.addRow(

            "",

            self.urgent

        )


        probleme_group.setLayout(

            probleme_form

        )

        layout.addWidget(

            probleme_group

        )


        # ==================================================
        # BOUTON
        # ==================================================

        bouton = QPushButton(

            "Créer le dossier de réparation"

        )

        bouton.setMinimumHeight(

            45

        )

        bouton.clicked.connect(

            self.creer_reparation

        )

        layout.addWidget(

            bouton

        )


        self.setLayout(

            layout

        )


        # Etat initial

        self.gerer_type_materiel(

            self.type_materiel.currentText()

        )

    # ======================================================
    # RECHERCHE CLIENT
    # ======================================================
    def rechercher_client(self):

        nom = self.nom_client.text().strip()

        if len(nom) < 3:

            return

        try:

            response = requests.get(

                "http://127.0.0.1:8000/clients/search",

                params={

                    "nom": nom

                },

                timeout=5

            )


            if response.status_code != 200:

                return


            client = response.json()


            if client:

                self.client_existe = True

                self.client_id = client["id"]


                self.telephone.setText(

                    client["telephone"]

                )


                self.client_info.setText(

                    "✓ Client existant"

                )


            else:

                self.client_existe = False

                self.client_id = None


                self.client_info.setText(

                    "Nouveau client"

                )


        except requests.exceptions.RequestException:

            self.client_info.setText(

                "Serveur inaccessible"

            )

    # ======================================================
    # AFFICHAGE DYNAMIQUE DU MATERIEL
    # ======================================================

    def gerer_type_materiel(

        self,

        type_materiel

    ):


        est_pc = type_materiel in [

            "PC",

            "PC Portable",

            "Unité centrale"

        ]


        est_imprimante = (

            type_materiel

            ==

            "Imprimante"

        )


        # Champs PC

        self.systeme_label.setVisible(

            est_pc

        )

        self.systeme.setVisible(

            est_pc

        )


        self.office_label.setVisible(

            est_pc

        )

        self.office.setVisible(

            est_pc

        )


        self.mot_de_passe.setVisible(

            est_pc

        )


        # Champs imprimante

        self.marque_label.setVisible(

            est_imprimante

        )

        self.marque.setVisible(

            est_imprimante

        )


        self.modele_label.setVisible(

            est_imprimante

        )

        self.modele.setVisible(

            est_imprimante

        )


        self.numero_serie_label.setVisible(

            est_imprimante

        )

        self.numero_serie.setVisible(

            est_imprimante

        )

    # ======================================================
    # CREATION DU DOSSIER
    # ======================================================

    def creer_reparation(self):

        nom = self.nom_client.text().strip()

        telephone = self.telephone.text().strip()

        type_materiel = self.type_materiel.currentText()


        # =========================================
        # VALIDATION DES CHAMPS OBLIGATOIRES
        # =========================================

        if not nom:

            QMessageBox.warning(

                self,

                "Erreur",

                "Le nom du client est obligatoire."

            )

            self.nom_client.setFocus()

            return


        if not telephone:

            QMessageBox.warning(

                self,

                "Erreur",

                "Le téléphone est obligatoire."

            )

            self.telephone.setFocus()

            return


        if not type_materiel:

            QMessageBox.warning(

                self,

                "Erreur",

                "Le type de matériel est obligatoire."

            )

            return


        try:

            # =========================================
            # 1. CREER OU RECUPERER LE CLIENT
            # =========================================

            client_response = requests.post(

                "http://127.0.0.1:8000/clients/get-or-create",

                json={

                    "nom": nom,

                    "telephone": telephone

                },

                timeout=10

            )


            if client_response.status_code != 200:

                QMessageBox.critical(

                    self,

                    "Erreur",

                    "Impossible de créer ou récupérer le client."

                )

                return


            client = client_response.json()


            client_id = client["id"]


            # =========================================
            # 2. PREPARER LES DONNEES
            # =========================================

            est_pc = type_materiel in [

                "PC",

                "PC Portable",

                "Unité centrale"

            ]


            donnees = {

                "client_id": client_id,

                "receptionniste_id": 1,

                "type_materiel": type_materiel,

                "systeme_exploitation": (

                    self.systeme.currentText()

                    if est_pc

                    else None

                ),

                "version_office": (

                    self.office.currentText()

                    if est_pc

                    else None

                ),

                "origine_probleme": (

                    self.origine.currentText()

                    or None

                ),

                "intervention": (

                    self.intervention.currentText()

                    or None

                ),

                "probleme": (

                    self.probleme.toPlainText().strip()

                    or None

                ),

                "pieces_defectueuses": (

                    self.pieces.toPlainText().strip()

                    or None

                ),

                "remarques": (

                    self.remarques.toPlainText().strip()

                    or None

                ),

                "mot_de_passe_pc": (

                    self.mot_de_passe.text().strip()

                    if est_pc

                    else None

                ),

                "urgent": self.urgent.isChecked()

            }


            # =========================================
            # 3. CREER LA REPARATION
            # =========================================

            reparation_response = requests.post(

                "http://127.0.0.1:8000/reparations/",

                json=donnees,

                timeout=10

            )


            if reparation_response.status_code not in [

                200,

                201

            ]:

                QMessageBox.critical(

                    self,

                    "Erreur",

                    (

                        "Erreur lors de la création "

                        "de la réparation.\n\n"

                        + reparation_response.text

                    )

                )

                return


            reparation = reparation_response.json()

            reparation_id = reparation["id"]

            fiche_response = requests.get(

                f"http://127.0.0.1:8000"
                f"/reparations/{reparation_id}/fiche",

                timeout=15

            )


            if fiche_response.status_code == 200:

                chemin = (

                    f"fiche_"

                    f"{reparation['numero_dossier']}.pdf"

                )


                with open(

                    chemin,

                    "wb"

                ) as fichier:

                    fichier.write(

                        fiche_response.content

                    )


                os.startfile(

                    os.path.abspath(

                        chemin

                    )

                )


            else:

                QMessageBox.warning(

                    self,

                    "Fiche PDF",

                    "La réparation est créée, mais la fiche PDF n'a pas pu être générée."

                )
            # =========================================
            # 4. OUVRIR LA FICHE DE CONFIRMATION
            # =========================================

            from .confirmation_reparation import ConfirmationReparation


            self.confirmation = ConfirmationReparation(

                reparation

            )


            self.confirmation.show()


            self.close()


        except requests.exceptions.ConnectionError:

            QMessageBox.critical(

                self,

                "Erreur serveur",

                (

                    "Impossible de contacter "

                    "le serveur FastAPI."

                )

            )


        except Exception as e:

            QMessageBox.critical(

                self,

                "Erreur",

                str(e)

            )