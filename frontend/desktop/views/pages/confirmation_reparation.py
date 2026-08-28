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
from PySide6.QtCore import Qt, QThread, Signal
import os
import tempfile
from services.backend_api import BackendAPI


# ============================================================
# WORKER ASYNCHRONE DÉLIVRANCE PDF
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
# FENÊTRE DE CONFIRMATION DU DOSSIER
# ============================================================

class ConfirmationReparation(QWidget):

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data or {}
        self.parent_window = parent
        self.pdf_worker = None

        self.setWindowTitle("Dossier de réparation créé avec succès")
        self.setMinimumSize(680, 680)
        self.resize(850, 750)

        self.init_ui()
        self.ajuster_fenetre()

    def ajuster_fenetre(self):
        try:
            screen = self.screen()
            if screen:
                available = screen.availableGeometry()
                largeur = min(850, available.width() - 80)
                hauteur = min(780, available.height() - 80)
                self.resize(largeur, hauteur)
                self.move(available.center() - self.rect().center())
        except Exception:
            pass

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #0f172a;
            }
            QFrame#card {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        contenu = QWidget()
        layout = QVBoxLayout(contenu)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # -----------------------------------------------------
        # EN-TÊTE
        # -----------------------------------------------------
        titre = QLabel("✓ DOSSIER CRÉÉ AVEC SUCCÈS")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size: 22px; font-weight: 800; color: #166534; padding-top: 5px;")
        layout.addWidget(titre)

        sous_titre = QLabel("La fiche de réception informatique a été enregistrée dans la base de données.")
        sous_titre.setAlignment(Qt.AlignCenter)
        sous_titre.setStyleSheet("color: #64748b; font-size: 14px;")
        layout.addWidget(sous_titre)

        # -----------------------------------------------------
        # BADGE NUMÉRO DOSSIER
        # -----------------------------------------------------
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
        
        numero_label = QLabel("NUMÉRO DE DOSSIER GENERÉ")
        numero_label.setAlignment(Qt.AlignCenter)
        numero_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 700; border: none;")
        numero_layout.addWidget(numero_label)

        num_valeur = self.valeur("numero_dossier", f"REP-{self.valeur('id', '-')}")
        numero = QLabel(num_valeur)
        numero.setAlignment(Qt.AlignCenter)
        numero.setStyleSheet("color: #1e293b; font-size: 28px; font-weight: 800; border: none;")
        numero_layout.addWidget(numero)

        layout.addWidget(numero_frame)

        # -----------------------------------------------------
        # RÉCAPITULATIF DES DÉTAILS
        # -----------------------------------------------------
        info_frame = QFrame()
        info_frame.setObjectName("card")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(25, 20, 25, 20)
        info_layout.setSpacing(14)

        info_layout.addWidget(self.creer_widget_ligne("Client", self.valeur("client_nom")))
        info_layout.addWidget(self.creer_widget_ligne("Téléphone", self.valeur("client_telephone")))
        info_layout.addWidget(self.creer_widget_ligne("Matériel", self.valeur("type_materiel")))
        info_layout.addWidget(self.creer_widget_ligne("Marque / Modèle", f"{self.valeur('marque', '-')} / {self.valeur('modele', '-')}"))
        info_layout.addWidget(self.creer_widget_ligne("Numéro de Série", self.valeur("numero_serie", "N/A")))
        
        urgent_txt = "URGENTE ⚠️" if self.data.get("urgent") else "Normale"
        info_layout.addWidget(self.creer_widget_ligne("Priorité", urgent_txt))

        layout.addWidget(info_frame)
        layout.addStretch()

        # -----------------------------------------------------
        # ACTIONS
        # -----------------------------------------------------
        actions = QHBoxLayout()
        actions.setSpacing(15)

        self.btn_imprimer = QPushButton("📄 Ouvrir la Fiche PDF")
        self.btn_imprimer.setMinimumHeight(48)
        self.btn_imprimer.setCursor(Qt.PointingHandCursor)
        self.btn_imprimer.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:disabled { background-color: #94a3b8; }
        """)
        self.btn_imprimer.clicked.connect(self.imprimer_fiche)
        actions.addWidget(self.btn_imprimer)

        self.btn_fermer = QPushButton("Fermer")
        self.btn_fermer.setMinimumHeight(48)
        self.btn_fermer.setCursor(Qt.PointingHandCursor)
        self.btn_fermer.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        self.btn_fermer.clicked.connect(self.retour_page)
        actions.addWidget(self.btn_fermer)

        layout.addLayout(actions)

        scroll.setWidget(contenu)
        layout_principal.addWidget(scroll)

    def creer_widget_ligne(self, titre, valeur):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        
        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet("color: #64748b; font-weight: 600; font-size: 13px;")
        
        lbl_val = QLabel(str(valeur))
        lbl_val.setStyleSheet("color: #0f172a; font-weight: 700; font-size: 14px;")
        lbl_val.setAlignment(Qt.AlignRight)

        l.addWidget(lbl_titre)
        l.addStretch()
        l.addWidget(lbl_val)
        return w

    def valeur(self, cle, defaut="-"):
        val = self.data.get(cle)
        return str(val).strip() if val is not None and str(val).strip() != "" else defaut

    def retour_page(self):
        if self.parent_window:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()
        self.close()

    def imprimer_fiche(self):
        reparation_id = self.data.get("id")
        if not reparation_id:
            QMessageBox.critical(self, "Erreur", "Identifiant du dossier introuvable.")
            return

        self.btn_imprimer.setEnabled(False)
        self.btn_imprimer.setText("Génération du PDF...")

        num_dossier = self.valeur("numero_dossier", f"reparation_{reparation_id}")

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
            QMessageBox.warning(self, "Erreur d'ouverture", f"Fichier généré dans : {chemin_pdf}\nMais impossible de l'ouvrir automatiquement : {e}")

    def on_pdf_error(self, message):
        self.btn_imprimer.setEnabled(True)
        self.btn_imprimer.setText("📄 Ouvrir la Fiche PDF")
        QMessageBox.critical(self, "Erreur PDF", f"Échec de la génération :\n{message}")