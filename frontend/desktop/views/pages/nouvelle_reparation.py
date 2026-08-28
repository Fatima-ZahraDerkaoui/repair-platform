import os
import tempfile

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QMessageBox,
    QLabel,
    QGroupBox,
    QScrollArea,
    QFrame,
    QStackedLayout
)

from PySide6.QtCore import (
    QTimer,
    Qt,
    QThread,
    Signal
)

from services.backend_api import BackendAPI


# ============================================================
# WORKER : RECHERCHE CLIENT ASYNCHRONE
# ============================================================

class SearchClientWorker(QThread):
    result_ready = Signal(dict, str)  # (data, nom_recherche)
    error_occurred = Signal(str)

    def __init__(self, nom, parent=None):
        super().__init__(parent)
        self.nom = nom

    def run(self):
        try:
            import requests
            response = requests.get(
                f"{BackendAPI.BASE_URL}/clients/search",
                params={"nom": self.nom},
                timeout=BackendAPI.REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                self.result_ready.emit(response.json() or {}, self.nom)
            else:
                self.result_ready.emit({}, self.nom)
        except Exception as e:
            self.error_occurred.emit(str(e))


# ============================================================
# WORKER : CREATION REPARATION ASYNCHRONE
# ============================================================

class CreateReparationWorker(QThread):
    result_ready = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, nom, telephone, donnees, parent=None):
        super().__init__(parent)
        self.nom = nom
        self.telephone = telephone
        self.donnees = donnees

    def run(self):
        try:
            import requests
            # 1. Obtenir ou créer le client
            client_resp = requests.post(
                f"{BackendAPI.BASE_URL}/clients/get-or-create",
                json={"nom": self.nom, "telephone": self.telephone},
                timeout=BackendAPI.REQUEST_TIMEOUT
            )
            client_resp.raise_for_status()
            client_data = client_resp.json()

            self.donnees["client_id"] = client_data["id"]

            # 2. Créer la réparation
            rep_resp = requests.post(
                f"{BackendAPI.BASE_URL}/reparations/",
                json=self.donnees,
                timeout=BackendAPI.REQUEST_TIMEOUT
            )
            rep_resp.raise_for_status()
            res_data = rep_resp.json()
            res_data["client_nom"] = self.nom
            res_data["client_telephone"] = self.telephone

            self.result_ready.emit(res_data)

        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("Impossible de contacter le serveur FastAPI (Connexion refusée).")
        except Exception as e:
            self.error_occurred.emit(str(e))


# ============================================================
# WORKER : TÉLÉCHARGEMENT PDF ASYNCHRONE
# ============================================================

class DownloadPDFWorker(QThread):
    finished_success = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, reparation_id, numero_dossier, parent=None):
        super().__init__(parent)
        self.reparation_id = reparation_id
        self.numero_dossier = numero_dossier

    def run(self):
        try:
            import requests
            url = f"{BackendAPI.BASE_URL}/reparations/{self.reparation_id}/fiche"
            response = requests.get(url, timeout=30)

            if response.status_code != 200:
                self.error_occurred.emit(f"Impossible de générer la fiche PDF. Code HTTP : {response.status_code}")
                return

            dossier_temp = tempfile.gettempdir()
            nom_fichier = self.numero_dossier if self.numero_dossier else f"reparation_{self.reparation_id}"
            chemin_pdf = os.path.join(dossier_temp, f"{nom_fichier}.pdf")

            with open(chemin_pdf, "wb") as f:
                f.write(response.content)

            self.finished_success.emit(chemin_pdf)

        except Exception as e:
            self.error_occurred.emit(str(e))


# ============================================================
# WIDGET PRINCIPAL : NOUVELLE RÉPARATION
# ============================================================

class NouvelleReparation(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

        self.client_id = None
        self.reparation_data = {}
        self.search_worker = None
        self.create_worker = None
        self.pdf_worker = None

        # Timer pour la détection de frappe du nom client
        self.timer_client = QTimer()
        self.timer_client.setSingleShot(True)
        self.timer_client.timeout.connect(self.lancer_recherche_client)

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #0f172a;
            }
            QGroupBox {
                font-weight: 700;
                font-size: 14px;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 20px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                background-color: white;
            }
            QLabel {
                font-size: 13px;
                color: #475569;
                font-weight: 600;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #0f172a;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 2px solid #2563eb;
                background-color: white;
            }
            QCheckBox {
                font-size: 13px;
                font-weight: 700;
                color: #dc2626;
            }
        """)

        # Layout empilé à 2 vues
        self.stack = QStackedLayout(self)

        # Vue 0 : Formulaire
        self.widget_formulaire = self.creer_widget_formulaire()
        self.stack.addWidget(self.widget_formulaire)

        # Vue 1 : Confirmation
        self.widget_confirmation = self.creer_widget_confirmation()
        self.stack.addWidget(self.widget_confirmation)

        self.stack.setCurrentIndex(0)

    # =========================================================
    # PAGE 0 : FORMULAIRE DE SAISIE
    # =========================================================

    def creer_widget_formulaire(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 20, 25, 25)
        container_layout.setSpacing(20)

        # Header
        header_layout = QVBoxLayout()
        titre = QLabel("Nouvelle Réparation")
        titre.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")
        sous_titre = QLabel("Enregistrement de la fiche de réception et du diagnostic initial.")
        sous_titre.setStyleSheet("font-size: 13px; color: #64748b; font-weight: 400;")
        header_layout.addWidget(titre)
        header_layout.addWidget(sous_titre)
        container_layout.addLayout(header_layout)

        # Section 1: Client
        client_group = QGroupBox("1. Informations Client")
        client_grid = QGridLayout()
        client_grid.setSpacing(12)

        client_grid.addWidget(QLabel("Nom et Prénom * :"), 0, 0)
        self.nom_client = QLineEdit()
        self.nom_client.setPlaceholderText("Saisissez le nom complet...")
        self.nom_client.textChanged.connect(lambda: self.timer_client.start(400))
        client_grid.addWidget(self.nom_client, 0, 1)

        self.client_badge = QLabel("")
        self.client_badge.setStyleSheet("font-size: 12px; font-weight: 700;")
        client_grid.addWidget(self.client_badge, 0, 2)

        client_grid.addWidget(QLabel("Téléphone * :"), 1, 0)
        self.telephone = QLineEdit()
        self.telephone.setPlaceholderText("Ex: 0661234567")
        client_grid.addWidget(self.telephone, 1, 1, 1, 2)

        client_group.setLayout(client_grid)
        container_layout.addWidget(client_group)

        # Section 2: Matériel
        materiel_group = QGroupBox("2. Caractéristiques du Matériel")
        mat_grid = QGridLayout()
        mat_grid.setSpacing(12)

        mat_grid.addWidget(QLabel("Type Matériel * :"), 0, 0)
        self.type_materiel = QComboBox()
        self.type_materiel.addItems(["PC Portable", "PC", "Unité centrale", "Imprimante", "Autre"])
        self.type_materiel.currentTextChanged.connect(self.gerer_type_materiel)
        mat_grid.addWidget(self.type_materiel, 0, 1)

        mat_grid.addWidget(QLabel("Marque :"), 0, 2)
        self.marque = QLineEdit()
        self.marque.setPlaceholderText("Ex: HP, Dell, Lenovo...")
        mat_grid.addWidget(self.marque, 0, 3)

        mat_grid.addWidget(QLabel("Modèle :"), 1, 0)
        self.modele = QLineEdit()
        self.modele.setPlaceholderText("Ex: ProBook 450 G8")
        mat_grid.addWidget(self.modele, 1, 1)

        mat_grid.addWidget(QLabel("N° Série :"), 1, 2)
        self.numero_serie = QLineEdit()
        self.numero_serie.setPlaceholderText("Numéro de série matériel")
        mat_grid.addWidget(self.numero_serie, 1, 3)

        self.systeme_lbl = QLabel("Système d'expl. :")
        self.systeme = QComboBox()
        self.systeme.addItems(["", "Windows 11", "Windows 10", "Linux", "macOS", "Autre"])
        mat_grid.addWidget(self.systeme_lbl, 2, 0)
        mat_grid.addWidget(self.systeme, 2, 1)

        self.office_lbl = QLabel("Version Office :")
        self.office = QComboBox()
        self.office.addItems(["", "Microsoft 365", "Office 2024", "Office 2021", "Office 2019", "Aucun"])
        mat_grid.addWidget(self.office_lbl, 2, 2)
        mat_grid.addWidget(self.office, 2, 3)

        self.pass_lbl = QLabel("Mot de passe PC :")
        self.mot_de_passe = QLineEdit()
        self.mot_de_passe.setPlaceholderText("Facultatif")
        self.mot_de_passe.setEchoMode(QLineEdit.Password)
        mat_grid.addWidget(self.pass_lbl, 3, 0)
        mat_grid.addWidget(self.mot_de_passe, 3, 1, 1, 3)

        materiel_group.setLayout(mat_grid)
        container_layout.addWidget(materiel_group)

        # Section 3: Diagnostic
        prob_group = QGroupBox("3. Diagnostic Initial & Demande")
        prob_grid = QGridLayout()
        prob_grid.setSpacing(12)

        prob_grid.addWidget(QLabel("Origine probable :"), 0, 0)
        self.origine = QComboBox()
        self.origine.addItems(["", "Matériel", "Logiciel", "Réseau", "Virus", "Panne électrique", "Autre"])
        prob_grid.addWidget(self.origine, 0, 1)

        prob_grid.addWidget(QLabel("Type Intervention :"), 0, 2)
        self.intervention = QComboBox()
        self.intervention.addItems(["", "Dépannage", "Réinstallation Système", "Changement Pièce", "Formatage", "Nettoyage / Depoussiérage", "Autre"])
        prob_grid.addWidget(self.intervention, 0, 3)

        prob_grid.addWidget(QLabel("Problème constaté :"), 1, 0)
        self.probleme = QTextEdit()
        self.probleme.setPlaceholderText("Décrivez en détail les symptômes de la panne...")
        self.probleme.setMaximumHeight(80)
        prob_grid.addWidget(self.probleme, 1, 1, 1, 3)

        prob_grid.addWidget(QLabel("Pièces suspectes :"), 2, 0)
        self.pieces = QTextEdit()
        self.pieces.setPlaceholderText("Ex: Disque SSD, Barrette RAM, Écran...")
        self.pieces.setMaximumHeight(60)
        prob_grid.addWidget(self.pieces, 2, 1, 1, 3)

        prob_grid.addWidget(QLabel("Accessoires déposés :"), 3, 0)
        self.accessoires = QTextEdit()
        self.accessoires.setPlaceholderText("Ex: Chargeur, sacoche, câble secteur...")
        self.accessoires.setMaximumHeight(60)
        prob_grid.addWidget(self.accessoires, 3, 1, 1, 3)

        prob_grid.addWidget(QLabel("Remarques :"), 4, 0)
        self.remarques = QTextEdit()
        self.remarques.setPlaceholderText("Rayures, état physique du matériel, consignes...")
        self.remarques.setMaximumHeight(60)
        prob_grid.addWidget(self.remarques, 4, 1, 1, 3)

        self.urgent = QCheckBox("⚠ Traitement d'URGENCE (Prioritaire)")
        prob_grid.addWidget(self.urgent, 5, 1, 1, 3)

        prob_group.setLayout(prob_grid)
        container_layout.addWidget(prob_group)

        # Bouton soumission
        self.btn_submit = QPushButton("Créer le dossier de réparation")
        self.btn_submit.setCursor(Qt.PointingHandCursor)
        self.btn_submit.setMinimumHeight(48)
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; border: none;
                border-radius: 8px; font-size: 15px; font-weight: 700;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:disabled { background-color: #94a3b8; }
        """)
        self.btn_submit.clicked.connect(self.creer_reparation)
        container_layout.addWidget(self.btn_submit)

        scroll.setWidget(container)
        self.gerer_type_materiel(self.type_materiel.currentText())
        return scroll

    # =========================================================
    # PAGE 1 : ÉCRAN DE CONFIRMATION INTÉGRÉ
    # =========================================================

    def creer_widget_confirmation(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        contenu = QWidget()
        layout = QVBoxLayout(contenu)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # En-tête Succès
        titre = QLabel("✓ DOSSIER CRÉÉ AVEC SUCCÈS")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size: 22px; font-weight: 800; color: #166534; padding-top: 5px;")
        layout.addWidget(titre)

        sous_titre = QLabel("La fiche de réception informatique a été enregistrée dans la base de données.")
        sous_titre.setAlignment(Qt.AlignCenter)
        sous_titre.setStyleSheet("color: #64748b; font-size: 14px;")
        layout.addWidget(sous_titre)

        # Card numéro dossier
        numero_frame = QFrame()
        numero_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        numero_layout = QVBoxLayout(numero_frame)
        numero_label = QLabel("NUMÉRO DE DOSSIER GÉNÉRÉ")
        numero_label.setAlignment(Qt.AlignCenter)
        numero_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 700; border: none;")
        numero_layout.addWidget(numero_label)

        self.conf_numero = QLabel("-")
        self.conf_numero.setAlignment(Qt.AlignCenter)
        self.conf_numero.setStyleSheet("color: #1e293b; font-size: 28px; font-weight: 800; border: none;")
        numero_layout.addWidget(self.conf_numero)
        layout.addWidget(numero_frame)

        # Tableau des détails
        info_frame = QFrame()
        info_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; }")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(25, 20, 25, 20)
        info_layout.setSpacing(14)

        self.conf_client = QLabel("-")
        self.conf_telephone = QLabel("-")
        self.conf_materiel = QLabel("-")
        self.conf_marque_modele = QLabel("-")
        self.conf_serie = QLabel("-")
        self.conf_priorite = QLabel("-")

        info_layout.addWidget(self.creer_widget_ligne("Client", self.conf_client))
        info_layout.addWidget(self.creer_widget_ligne("Téléphone", self.conf_telephone))
        info_layout.addWidget(self.creer_widget_ligne("Matériel", self.conf_materiel))
        info_layout.addWidget(self.creer_widget_ligne("Marque / Modèle", self.conf_marque_modele))
        info_layout.addWidget(self.creer_widget_ligne("Numéro de Série", self.conf_serie))
        info_layout.addWidget(self.creer_widget_ligne("Priorité", self.conf_priorite))

        layout.addWidget(info_frame)
        layout.addStretch()

        # Boutons d'actions
        actions = QHBoxLayout()
        actions.setSpacing(15)

        self.btn_imprimer = QPushButton("📄 Ouvrir la Fiche PDF")
        self.btn_imprimer.setMinimumHeight(48)
        self.btn_imprimer.setCursor(Qt.PointingHandCursor)
        self.btn_imprimer.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; border: none;
                border-radius: 8px; font-size: 14px; font-weight: 700;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:disabled { background-color: #94a3b8; }
        """)
        self.btn_imprimer.clicked.connect(self.imprimer_fiche)
        actions.addWidget(self.btn_imprimer)

        self.btn_nouveau = QPushButton("➕ Créer une autre réparation")
        self.btn_nouveau.setMinimumHeight(48)
        self.btn_nouveau.setCursor(Qt.PointingHandCursor)
        self.btn_nouveau.setStyleSheet("""
            QPushButton {
                background-color: #475569; color: white; border: none;
                border-radius: 8px; font-size: 14px; font-weight: 700;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        self.btn_nouveau.clicked.connect(self.reset_formulaire)
        actions.addWidget(self.btn_nouveau)

        layout.addLayout(actions)
        scroll.setWidget(contenu)
        return scroll

    def creer_widget_ligne(self, titre, widget_valeur):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet("color: #64748b; font-weight: 600; font-size: 13px;")
        widget_valeur.setStyleSheet("color: #0f172a; font-weight: 700; font-size: 14px;")
        widget_valeur.setAlignment(Qt.AlignRight)

        l.addWidget(lbl_titre)
        l.addStretch()
        l.addWidget(widget_valeur)
        return w

    # =========================================================
    # LOGIQUE D'INTERFACE & RECHERCHE
    # =========================================================

    def gerer_type_materiel(self, type_materiel):
        est_pc = type_materiel in ["PC", "PC Portable", "Unité centrale"]
        self.systeme_lbl.setVisible(est_pc)
        self.systeme.setVisible(est_pc)
        self.office_lbl.setVisible(est_pc)
        self.office.setVisible(est_pc)
        self.pass_lbl.setVisible(est_pc)
        self.mot_de_passe.setVisible(est_pc)

    def lancer_recherche_client(self):
        nom = self.nom_client.text().strip()
        if len(nom) < 3:
            self.client_badge.setText("")
            return

        self.client_badge.setText("🔍 Recherche...")
        self.client_badge.setStyleSheet("color: #64748b;")

        self.search_worker = SearchClientWorker(nom)
        self.search_worker.result_ready.connect(self.on_client_search_result)
        self.search_worker.start()

    def on_client_search_result(self, client_data, nom_recherche):
        nom_actuel = self.nom_client.text().strip()

        if nom_actuel.casefold() != nom_recherche.casefold():
            return

        nom_trouve = str(client_data.get("nom", "")).strip() if client_data else ""

        if client_data and client_data.get("id") and nom_trouve.casefold() == nom_actuel.casefold():
            self.client_id = client_data["id"]
            if client_data.get("telephone"):
                self.telephone.setText(client_data["telephone"])
            self.client_badge.setText("✓ Client existant")
            self.client_badge.setStyleSheet("color: #16a34a; font-weight: 700;")
        else:
            self.client_id = None
            self.telephone.clear()
            self.client_badge.setText("✦ Nouveau client")
            self.client_badge.setStyleSheet("color: #2563eb; font-weight: 700;")

    # =========================================================
    # CRÉATION DE LA RÉPARATION
    # =========================================================

    def creer_reparation(self):
        nom = self.nom_client.text().strip()
        telephone = self.telephone.text().strip()
        type_materiel = self.type_materiel.currentText()

        if not nom:
            QMessageBox.warning(self, "Champ requis", "Le nom du client est obligatoire.")
            self.nom_client.setFocus()
            return

        if not telephone:
            QMessageBox.warning(self, "Champ requis", "Le numéro de téléphone est obligatoire.")
            self.telephone.setFocus()
            return

        est_pc = type_materiel in ["PC", "PC Portable", "Unité centrale"]

        donnees = {
            "receptionniste_id": 1,
            "type_materiel": type_materiel,
            "marque": self.marque.text().strip() or None,
            "modele": self.modele.text().strip() or None,
            "numero_serie": self.numero_serie.text().strip() or None,
            "systeme_exploitation": self.systeme.currentText() if est_pc and self.systeme.currentText() else None,
            "version_office": self.office.currentText() if est_pc and self.office.currentText() else None,
            "mot_de_passe_pc": self.mot_de_passe.text().strip() if est_pc and self.mot_de_passe.text().strip() else None,
            "origine_probleme": self.origine.currentText() or None,
            "intervention": self.intervention.currentText() or None,
            "probleme": self.probleme.toPlainText().strip() or None,
            "pieces_defectueuses": self.pieces.toPlainText().strip() or None,
            "accessoires": self.accessoires.toPlainText().strip() or None,
            "remarques": self.remarques.toPlainText().strip() or None,
            "urgent": self.urgent.isChecked(),
            "resolu": False
        }

        self.btn_submit.setEnabled(False)
        self.btn_submit.setText("Création en cours...")

        self.create_worker = CreateReparationWorker(nom, telephone, donnees)
        self.create_worker.result_ready.connect(self.on_creation_success)
        self.create_worker.error_occurred.connect(self.on_creation_error)
        self.create_worker.start()

    def on_creation_success(self, reparation_data):
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Créer le dossier de réparation")
        self.reparation_data = reparation_data

        # Mettre à jour les labels de confirmation
        num_dossier = reparation_data.get("numero_dossier") or f"REP-{reparation_data.get('id', '-')}"
        self.conf_numero.setText(str(num_dossier))
        self.conf_client.setText(str(reparation_data.get("client_nom", "-")))
        self.conf_telephone.setText(str(reparation_data.get("client_telephone", "-")))
        self.conf_materiel.setText(str(reparation_data.get("type_materiel", "-")))

        marque = reparation_data.get("marque") or "-"
        modele = reparation_data.get("modele") or "-"
        self.conf_marque_modele.setText(f"{marque} / {modele}")
        self.conf_serie.setText(str(reparation_data.get("numero_serie") or "N/A"))

        urgent_txt = "URGENTE ⚠️" if reparation_data.get("urgent") else "Normale"
        self.conf_priorite.setText(urgent_txt)

        # Afficher la page de confirmation directement dans le StackedLayout
        self.stack.setCurrentIndex(1)

    def on_creation_error(self, message):
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Créer le dossier de réparation")
        QMessageBox.critical(self, "Erreur", f"Échec de l'enregistrement :\n{message}")

    # =========================================================
    # ACTIONS CONFIRMATION & RESET
    # =========================================================

    def imprimer_fiche(self):
        reparation_id = self.reparation_data.get("id")
        if not reparation_id:
            QMessageBox.critical(self, "Erreur", "Identifiant du dossier introuvable.")
            return

        self.btn_imprimer.setEnabled(False)
        self.btn_imprimer.setText("Génération du PDF...")

        num_dossier = self.reparation_data.get("numero_dossier") or f"reparation_{reparation_id}"

        self.pdf_worker = DownloadPDFWorker(reparation_id, num_dossier)
        self.pdf_worker.finished_success.connect(self.on_pdf_success)
        self.pdf_worker.error_occurred.connect(self.on_pdf_error)
        self.pdf_worker.start()

    def on_pdf_success(self, chemin_pdf):
        self.btn_imprimer.setEnabled(True)
        self.btn_imprimer.setText("📄 Ouvrir la Fiche PDF")
        try:
            os.startfile(chemin_pdf)
        except Exception as e:
            QMessageBox.warning(self, "Erreur d'ouverture", f"Fichier généré dans : {chemin_pdf}\nImpossible de l'ouvrir automatiquement : {e}")

    def on_pdf_error(self, message):
        self.btn_imprimer.setEnabled(True)
        self.btn_imprimer.setText("📄 Ouvrir la Fiche PDF")
        QMessageBox.critical(self, "Erreur PDF", f"Échec de la génération :\n{message}")

    def reset_formulaire(self):
        self.nom_client.clear()
        self.telephone.clear()
        self.client_badge.setText("")
        self.type_materiel.setCurrentIndex(0)
        self.marque.clear()
        self.modele.clear()
        self.numero_serie.clear()
        self.systeme.setCurrentIndex(0)
        self.office.setCurrentIndex(0)
        self.mot_de_passe.clear()
        self.origine.setCurrentIndex(0)
        self.intervention.setCurrentIndex(0)
        self.probleme.clear()
        self.pieces.clear()
        self.accessoires.clear()
        self.remarques.clear()
        self.urgent.setChecked(False)

        self.reparation_data = {}
        self.stack.setCurrentIndex(0)
        