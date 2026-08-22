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
    QScrollArea
)

from PySide6.QtCore import (
    QTimer,
    Qt
)

import requests


class NouvelleReparation(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.parent_window = parent

        self.setWindowTitle(
            "Nouvelle réparation"
        )

        self.setMinimumSize(
            700,
            650
        )

        self.resize(
            900,
            800
        )

        self.client_existe = False

        self.client_id = None

        self.timer_client = QTimer()

        self.timer_client.setSingleShot(
            True
        )

        self.timer_client.timeout.connect(
            self.rechercher_client
        )

        self.init_ui()

        self.ajuster_fenetre()

    # ======================================================
    # ADAPTER LA FENÊTRE
    # ======================================================

    def ajuster_fenetre(self):

        try:

            screen = self.screen()

            if screen:

                available = screen.availableGeometry()

                largeur = min(
                    950,
                    available.width() - 80
                )

                hauteur = min(
                    850,
                    available.height() - 80
                )

                self.resize(
                    largeur,
                    hauteur
                )

                self.move(
                    available.center()
                    - self.rect().center()
                )

        except Exception:
            pass

    # ======================================================
    # INTERFACE
    # ======================================================

    def init_ui(self):

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        # ==================================================
        # SCROLL AREA
        # ==================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        # ==================================================
        # FORMULAIRE
        # ==================================================

        formulaire = QWidget()

        formulaire_layout = QVBoxLayout(
            formulaire
        )

        formulaire_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        formulaire_layout.setSpacing(
            15
        )

        # ==================================================
        # CLIENT
        # ==================================================

        client_group = QGroupBox(
            "Informations client"
        )

        client_form = QFormLayout()

        self.nom_client = QLineEdit()

        self.nom_client.setPlaceholderText(
            "Nom et prénom du client"
        )

        self.nom_client.textChanged.connect(
            lambda: self.timer_client.start(500)
        )

        client_form.addRow(
            "Nom et prénom * :",
            self.nom_client
        )

        self.telephone = QLineEdit()

        self.telephone.setPlaceholderText(
            "Exemple : 0661234567"
        )

        client_form.addRow(
            "Téléphone * :",
            self.telephone
        )

        self.client_info = QLabel()

        self.client_info.setWordWrap(
            True
        )

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

        formulaire_layout.addWidget(
            client_group
        )

        # ==================================================
        # MATÉRIEL
        # ==================================================

        materiel_group = QGroupBox(
            "Informations matériel"
        )

        materiel_form = QFormLayout()

        self.type_materiel = QComboBox()

        self.type_materiel.addItems([
            "PC",
            "PC Portable",
            "Imprimante",
            "Unité centrale",
            "Autre"
        ])

        self.type_materiel.currentTextChanged.connect(
            self.gerer_type_materiel
        )

        materiel_form.addRow(
            "Type matériel * :",
            self.type_materiel
        )

        # Système
        self.systeme_label = QLabel(
            "Système d'exploitation :"
        )

        self.systeme = QComboBox()

        self.systeme.addItems([
            "",
            "Windows 10",
            "Windows 11",
            "Linux",
            "Autre"
        ])

        materiel_form.addRow(
            self.systeme_label,
            self.systeme
        )

        # Office
        self.office_label = QLabel(
            "Office :"
        )

        self.office = QComboBox()

        self.office.addItems([
            "",
            "Office 2013",
            "Office 2024",
            "Microsoft 365",
            "Aucun"
        ])

        materiel_form.addRow(
            self.office_label,
            self.office
        )

        # Mot de passe
        self.mot_de_passe_label = QLabel(
            "Mot de passe PC :"
        )

        self.mot_de_passe = QLineEdit()

        self.mot_de_passe.setPlaceholderText(
            "Facultatif"
        )

        self.mot_de_passe.setEchoMode(
            QLineEdit.Password
        )

        materiel_form.addRow(
            self.mot_de_passe_label,
            self.mot_de_passe
        )

        # Marque
        self.marque_label = QLabel(
            "Marque :"
        )

        self.marque = QLineEdit()

        self.marque.setPlaceholderText(
            "Exemple : HP, Dell, Lenovo..."
        )

        materiel_form.addRow(
            self.marque_label,
            self.marque
        )

        # Modèle
        self.modele_label = QLabel(
            "Modèle :"
        )

        self.modele = QLineEdit()

        self.modele.setPlaceholderText(
            "Exemple : ProBook 450 G8"
        )

        materiel_form.addRow(
            self.modele_label,
            self.modele
        )

        # Numéro de série
        self.numero_serie_label = QLabel(
            "Numéro de série :"
        )

        self.numero_serie = QLineEdit()

        self.numero_serie.setPlaceholderText(
            "Numéro de série du matériel"
        )

        materiel_form.addRow(
            self.numero_serie_label,
            self.numero_serie
        )

        materiel_group.setLayout(
            materiel_form
        )

        formulaire_layout.addWidget(
            materiel_group
        )

        # ==================================================
        # PROBLÈME
        # ==================================================

        probleme_group = QGroupBox(
            "Informations sur le problème"
        )

        probleme_form = QFormLayout()

        self.origine = QComboBox()

        self.origine.addItems([
            "",
            "Matériel",
            "Logiciel",
            "Réseau",
            "Virus",
            "Mise à jour",
            "Inconnue",
            "Autre"
        ])

        probleme_form.addRow(
            "Origine du problème :",
            self.origine
        )

        self.intervention = QComboBox()

        self.intervention.addItems([
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
        ])

        probleme_form.addRow(
            "Intervention :",
            self.intervention
        )

        self.probleme = QTextEdit()

        self.probleme.setPlaceholderText(
            "Décrire le problème constaté..."
        )

        self.probleme.setMinimumHeight(
            90
        )

        self.probleme.setMaximumHeight(
            120
        )

        probleme_form.addRow(
            "Problème constaté :",
            self.probleme
        )

        self.pieces = QTextEdit()

        self.pieces.setPlaceholderText(
            "Exemple : Disque dur, RAM..."
        )

        self.pieces.setMinimumHeight(
            70
        )

        self.pieces.setMaximumHeight(
            100
        )

        probleme_form.addRow(
            "Pièces défectueuses :",
            self.pieces
        )

        self.accessoires = QTextEdit()

        self.accessoires.setPlaceholderText(
            "Exemple : chargeur, câble secteur, souris, sacoche..."
        )

        self.accessoires.setMinimumHeight(
            70
        )

        self.accessoires.setMaximumHeight(
            100
        )

        probleme_form.addRow(
            "Accessoires déposés :",
            self.accessoires
        )

        self.remarques = QTextEdit()

        self.remarques.setPlaceholderText(
            "Remarques supplémentaires..."
        )

        self.remarques.setMinimumHeight(
            70
        )

        self.remarques.setMaximumHeight(
            100
        )

        probleme_form.addRow(
            "Remarques :",
            self.remarques
        )

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

        formulaire_layout.addWidget(
            probleme_group
        )

        # ==================================================
        # BOUTON
        # ==================================================

        bouton = QPushButton(
            "Créer le dossier de réparation"
        )

        bouton.setMinimumHeight(
            48
        )

        bouton.setStyleSheet(
            """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 7px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
            """
        )

        bouton.clicked.connect(
            self.creer_reparation
        )

        formulaire_layout.addWidget(
            bouton
        )

        formulaire_layout.addStretch()

        # ==================================================
        # INSTALLATION
        # ==================================================

        scroll.setWidget(
            formulaire
        )

        layout.addWidget(
            scroll
        )

        # ==================================================
        # ÉTAT INITIAL
        # ==================================================

        self.gerer_type_materiel(
            self.type_materiel.currentText()
        )

    # ======================================================
    # RECHERCHE CLIENT
    # ======================================================

    def rechercher_client(self):

        nom = self.nom_client.text().strip()

        if len(nom) < 3:

            self.client_existe = False
            self.client_id = None
            self.client_info.clear()

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

                self.client_existe = False
                self.client_id = None

                return

            client = response.json()

            if client:

                nom_trouve = str(
                    client.get(
                        "nom",
                        ""
                    )
                ).strip().casefold()

                nom_saisi = nom.casefold()

                if nom_trouve == nom_saisi:

                    self.client_existe = True

                    self.client_id = client[
                        "id"
                    ]

                    telephone = client.get(
                        "telephone"
                    )

                    if telephone:

                        self.telephone.setText(
                            telephone
                        )

                    self.client_info.setText(
                        "✓ Client existant"
                    )

                    self.client_info.setStyleSheet(
                        "color: #16a34a; font-weight: bold;"
                    )

                    return

            self.client_existe = False

            self.client_id = None

            self.client_info.setText(
                "Nouveau client"
            )

            self.client_info.setStyleSheet(
                "color: #2563eb;"
            )

        except requests.exceptions.RequestException:

            self.client_existe = False

            self.client_id = None

            self.client_info.setText(
                "Serveur inaccessible"
            )

            self.client_info.setStyleSheet(
                "color: #dc2626; font-weight: bold;"
            )

    # ======================================================
    # TYPE MATÉRIEL
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

        self.marque_label.setVisible(
            True
        )

        self.marque.setVisible(
            True
        )

        self.modele_label.setVisible(
            True
        )

        self.modele.setVisible(
            True
        )

        self.numero_serie_label.setVisible(
            True
        )

        self.numero_serie.setVisible(
            True
        )

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

        self.mot_de_passe_label.setVisible(
            est_pc
        )

        self.mot_de_passe.setVisible(
            est_pc
        )

    # ======================================================
    # CREATION
    # ======================================================

    def creer_reparation(self):

        nom = self.nom_client.text().strip()

        telephone = self.telephone.text().strip()

        type_materiel = (
            self.type_materiel.currentText()
        )

        # ==================================================
        # VALIDATION
        # ==================================================

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

            # ==================================================
            # 1. CLIENT
            # ==================================================

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
                    (
                        "Impossible de créer "
                        "ou récupérer le client."
                    )
                )

                return

            client = client_response.json()

            client_id = client["id"]

            # ==================================================
            # 2. DONNÉES
            # ==================================================

            est_pc = type_materiel in [
                "PC",
                "PC Portable",
                "Unité centrale"
            ]

            donnees = {

                "client_id": client_id,

                "receptionniste_id": 1,

                # ==============================
                # MATÉRIEL
                # ==============================

                "type_materiel": type_materiel,

                "marque": (
                    self.marque.text().strip()
                    or None
                ),

                "modele": (
                    self.modele.text().strip()
                    or None
                ),

                "numero_serie": (
                    self.numero_serie.text().strip()
                    or None
                ),

                "systeme_exploitation": (
                    self.systeme.currentText()
                    if est_pc
                    and self.systeme.currentText()
                    else None
                ),

                "version_office": (
                    self.office.currentText()
                    if est_pc
                    and self.office.currentText()
                    else None
                ),

                "mot_de_passe_pc": (
                    self.mot_de_passe.text().strip()
                    if est_pc
                    and self.mot_de_passe.text().strip()
                    else None
                ),

                # ==============================
                # PROBLÈME
                # ==============================

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

                "diagnostic": None,

                "pieces_defectueuses": (
                    self.pieces.toPlainText().strip()
                    or None
                ),

                "accessoires": (
                    self.accessoires.toPlainText().strip()
                    or None
                ),

                "remarques": (
                    self.remarques.toPlainText().strip()
                    or None
                ),

                # ==============================
                # ÉTAT
                # ==============================

                "urgent": self.urgent.isChecked(),

                "resolu": False
            }

            # ==================================================
            # 3. CREER REPARATION
            # ==================================================

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

            reparation = (
                reparation_response.json()
            )

            # ==================================================
            # AJOUTER LES INFORMATIONS CLIENT POUR CONFIRMATION
            # ==================================================

            reparation["client_nom"] = nom

            reparation["client_telephone"] = telephone

            # ==================================================
            # 4. CONFIRMATION
            # ==================================================

            from .confirmation_reparation import (
                ConfirmationReparation
            )

            self.confirmation = ConfirmationReparation(
                reparation,
                parent=self.parent_window or self.parent()
            )

            self.confirmation.show()

            self.close()

        except requests.exceptions.ConnectionError:

            QMessageBox.critical(
                self,
                "Erreur serveur",
                "Impossible de contacter le serveur FastAPI."
            )

        except requests.exceptions.RequestException as erreur:

            QMessageBox.critical(
                self,
                "Erreur réseau",
                str(erreur)
            )

        except Exception as erreur:

            QMessageBox.critical(
                self,
                "Erreur",
                str(erreur)
            )
            