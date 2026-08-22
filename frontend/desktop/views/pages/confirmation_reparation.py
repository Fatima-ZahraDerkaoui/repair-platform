from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QFrame,
    QScrollArea,
    QSizePolicy
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
        self.parent_window = parent

        self.setWindowTitle(
            "Dossier de réparation créé"
        )

        # =====================================================
        # FENÊTRE
        # =====================================================

        self.setMinimumSize(
            650,
            650
        )

        self.resize(
            800,
            750
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.init_ui()

        # Adapter la fenêtre à l'écran disponible
        self.ajuster_fenetre()

    # =========================================================
    # ADAPTATION DE LA FENÊTRE
    # =========================================================

    def ajuster_fenetre(self):

        try:

            screen = self.screen()

            if screen:

                available = screen.availableGeometry()

                largeur = min(
                    850,
                    available.width() - 80
                )

                hauteur = min(
                    800,
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

    # =========================================================
    # INTERFACE
    # =========================================================

    def init_ui(self):

        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # =====================================================
        # SCROLL
        # =====================================================

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

        # =====================================================
        # CONTENU
        # =====================================================

        contenu = QWidget()

        layout = QVBoxLayout(
            contenu
        )

        layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        layout.setSpacing(
            15
        )

        # =====================================================
        # EN-TÊTE
        # =====================================================

        titre = QLabel(
            "✓ DOSSIER CRÉÉ AVEC SUCCÈS"
        )

        titre.setAlignment(
            Qt.AlignCenter
        )

        titre.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #166534;
                padding: 10px;
            }
            """
        )

        layout.addWidget(
            titre
        )

        sous_titre = QLabel(
            "La réception a été enregistrée dans le système."
        )

        sous_titre.setAlignment(
            Qt.AlignCenter
        )

        sous_titre.setWordWrap(
            True
        )

        sous_titre.setStyleSheet(
            """
            QLabel {
                color: #64748b;
                font-size: 14px;
            }
            """
        )

        layout.addWidget(
            sous_titre
        )

        # =====================================================
        # NUMÉRO DOSSIER
        # =====================================================

        numero_frame = QFrame()

        numero_frame.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        numero_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
            }
            """
        )

        numero_layout = QVBoxLayout(
            numero_frame
        )

        numero_label = QLabel(
            "NUMÉRO DU DOSSIER"
        )

        numero_label.setAlignment(
            Qt.AlignCenter
        )

        numero_label.setStyleSheet(
            """
            QLabel {
                color: #64748b;
                font-size: 12px;
                font-weight: bold;
            }
            """
        )

        numero_layout.addWidget(
            numero_label
        )

        numero = QLabel(
            self.valeur(
                "numero_dossier",
                "-"
            )
        )

        numero.setAlignment(
            Qt.AlignCenter
        )

        numero.setWordWrap(
            True
        )

        numero.setStyleSheet(
            """
            QLabel {
                color: #0f172a;
                font-size: 24px;
                font-weight: bold;
                padding: 5px;
            }
            """
        )

        numero_layout.addWidget(
            numero
        )

        layout.addWidget(
            numero_frame
        )

        # =====================================================
        # INFORMATIONS
        # =====================================================

        informations = QFrame()

        informations.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        informations.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            """
        )

        infos_layout = QVBoxLayout(
            informations
        )

        infos_layout.setContentsMargins(
            20,
            15,
            20,
            15
        )

        infos_layout.setSpacing(
            12
        )

        # Client
        infos_layout.addWidget(
            QLabel(
                self.creer_ligne(
                    "CLIENT",
                    self.valeur(
                        "client_nom"
                    )
                )
            )
        )

        infos_layout.addWidget(
            QLabel(
                self.creer_ligne(
                    "TÉLÉPHONE",
                    self.valeur(
                        "client_telephone"
                    )
                )
            )
        )

        # Matériel
        infos_layout.addWidget(
            QLabel(
                self.creer_ligne(
                    "MATÉRIEL",
                    self.valeur(
                        "type_materiel"
                    )
                )
            )
        )

        infos_layout.addWidget(
            QLabel(
                self.creer_ligne(
                    "MARQUE",
                    self.valeur(
                        "marque"
                    )
                )
            )

        )

        infos_layout.addWidget(
            QLabel(
                self.creer_ligne(
                    "MODÈLE",
                    self.valeur(
                        "modele"
                    )
                )
            )
        )

        infos_layout.addWidget(
            QLabel(
                self.creer_ligne(
                    "NUMÉRO DE SÉRIE",
                    self.valeur(
                        "numero_serie"
                    )
                )
            )
        )

        # Statut
        infos_layout.addWidget(
            QLabel(
                self.creer_ligne(
                    "STATUT",
                    self.valeur(
                        "statut",
                        "En attente"
                    )
                )
            )
        )

        layout.addWidget(
            informations
        )

        # =====================================================
        # ESPACE
        # =====================================================

        layout.addStretch()

        # =====================================================
        # ACTIONS
        # =====================================================

        actions = QHBoxLayout()

        actions.setSpacing(
            12
        )

        bouton_imprimer = QPushButton(
            "Ouvrir la fiche PDF"
        )

        bouton_imprimer.setMinimumHeight(
            48
        )

        bouton_imprimer.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        bouton_imprimer.setStyleSheet(
            """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 7px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
            """
        )

        bouton_imprimer.clicked.connect(
            self.imprimer_fiche
        )

        actions.addWidget(
            bouton_imprimer
        )

        bouton_fermer = QPushButton(
            "Fermer"
        )

        bouton_fermer.setMinimumHeight(
            48
        )

        bouton_fermer.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        bouton_fermer.setStyleSheet(
            """
            QPushButton {
                background-color: #64748b;
                color: white;
                border: none;
                border-radius: 7px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }

            QPushButton:hover {
                background-color: #475569;
            }
            """
        )

        bouton_fermer.clicked.connect(
            self.retour_page
        )

        actions.addWidget(
            bouton_fermer
        )

        layout.addLayout(
            actions
        )

        # =====================================================
        # INSTALLATION
        # =====================================================

        scroll.setWidget(
            contenu
        )

        layout_principal.addWidget(
            scroll
        )

    # =========================================================
    # VALEUR
    # =========================================================

    def valeur(
        self,
        cle,
        valeur_defaut=""
    ):

        valeur = self.data.get(
            cle,
            valeur_defaut
        )

        if valeur is None:
            return valeur_defaut

        valeur = str(
            valeur
        ).strip()

        return (
            valeur
            if valeur
            else valeur_defaut
        )

    # =========================================================
    # FORMATAGE
    # =========================================================

    def creer_ligne(
        self,
        titre,
        valeur
    ):

        return (
            f"<b>{titre}</b>"
            f"<br>"
            f"<span style='font-size:14px;'>"
            f"{valeur}"
            f"</span>"
        )

    # =========================================================
    # RETOUR
    # =========================================================

    def retour_page(self):

        try:

            if self.parent_window:

                self.parent_window.show()

                self.parent_window.raise_()

                self.parent_window.activateWindow()

        except Exception:
            pass

        self.close()

    # =========================================================
    # PDF
    # =========================================================

    def imprimer_fiche(self):

        reparation_id = self.data.get(
            "id"
        )

        if not reparation_id:

            QMessageBox.critical(
                self,
                "Erreur",
                "Identifiant du dossier introuvable."
            )

            return

        url = (
            "http://127.0.0.1:8000"
            f"/reparations/{reparation_id}"
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
                    (
                        "Impossible de générer "
                        "la fiche PDF.\n\n"
                        f"Code HTTP : "
                        f"{response.status_code}"
                    )
                )

                return

            dossier_temp = tempfile.gettempdir()

            numero_dossier = self.valeur(
                "numero_dossier",
                f"reparation_{reparation_id}"
            )

            chemin_pdf = os.path.join(
                dossier_temp,
                f"{numero_dossier}.pdf"
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

        except requests.exceptions.RequestException as erreur:

            QMessageBox.critical(
                self,
                "Erreur serveur",
                (
                    "Impossible de contacter "
                    "le serveur FastAPI.\n\n"
                    f"{erreur}"
                )
            )

        except Exception as erreur:

            QMessageBox.critical(
                self,
                "Erreur",
                str(erreur)
            )
            