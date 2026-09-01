import socket
import qrcode
import requests
import traceback
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QFrame,
    QProgressBar,
    QScrollArea
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal, Qt, QThread

from services.backend_api import BackendAPI
from services.ocr_worker import OCRWorker
from services.scan_worker import ScanWorker
from ui.widgets.facture_result_widget import FactureResultWidget


class FacturesPage(QWidget):

    facture_validated = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.facture_data = None
        self.ocr_thread = None
        self.ocr_worker = None
        self.scan_thread = None
        self.scan_worker = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # En-tête
        titre = QLabel("Gestion des factures")
        titre.setStyleSheet("font-size: 26px; font-weight: 800; color: #0F172A;")
        main_layout.addWidget(titre)

        description = QLabel("Importez une facture ou utilisez le scan mobile pour extraire automatiquement ses informations.")
        description.setStyleSheet("color: #64748B; font-size: 13px;")
        main_layout.addWidget(description)

        # Barre d'actions
        actions = QHBoxLayout()
        actions.setSpacing(12)

        self.bouton_importer = QPushButton("📄 Importer une facture")
        self.bouton_importer.setFixedHeight(40)
        self.bouton_importer.setCursor(Qt.PointingHandCursor)
        self.bouton_importer.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border-radius: 8px;
                font-weight: 600;
                padding: 0 16px;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)
        self.bouton_importer.clicked.connect(self.importer_facture)
        actions.addWidget(self.bouton_importer)

        self.bouton_scan = QPushButton("📱 Scanner avec téléphone")
        self.bouton_scan.setFixedHeight(40)
        self.bouton_scan.setCursor(Qt.PointingHandCursor)
        self.bouton_scan.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-weight: 600;
                color: #334155;
                padding: 0 16px;
            }
            QPushButton:hover { background-color: #F1F5F9; }
        """)
        self.bouton_scan.clicked.connect(self.scanner_telephone)
        actions.addWidget(self.bouton_scan)

        actions.addStretch()
        main_layout.addLayout(actions)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.result_container = QFrame()
        self.result_container.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;")
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(20, 20, 20, 20)
        self.result_layout.setSpacing(15)

        self.scroll_area.setWidget(self.result_container)
        main_layout.addWidget(self.scroll_area, 1)

        self.show_empty_state()

    def show_empty_state(self):
        self.clear_result()
        label = QLabel("Aucune facture analysée.\n\nImportez un document pour commencer l'extraction.")
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumHeight(200)
        label.setStyleSheet("color: #94A3B8; font-size: 15px; font-weight: 500;")
        self.result_layout.addWidget(label)

    def clear_result(self):
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def importer_facture(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner une facture", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            self.start_ocr(file_path)

    def start_ocr(self, file_path):
        self.bouton_importer.setEnabled(False)
        self.bouton_scan.setEnabled(False)
        self.show_loading()

        self.ocr_thread = QThread()
        self.ocr_worker = OCRWorker(file_path)
        self.ocr_worker.moveToThread(self.ocr_thread)

        self.ocr_thread.started.connect(self.ocr_worker.run)
        self.ocr_worker.progress.connect(self.update_loading)
        self.ocr_worker.finished.connect(self.ocr_finished)
        self.ocr_worker.error.connect(self.ocr_error)

        self.ocr_worker.finished.connect(self.ocr_thread.quit)
        self.ocr_worker.error.connect(self.ocr_thread.quit)
        self.ocr_thread.finished.connect(self.ocr_worker.deleteLater)
        self.ocr_thread.finished.connect(self.ocr_thread.deleteLater)
        self.ocr_thread.finished.connect(self.ocr_thread_finished)

        self.ocr_thread.start()

    def show_loading(self):
        self.clear_result()
        container = QVBoxLayout()
        container.setContentsMargins(30, 40, 30, 40)

        label = QLabel("Analyse OCR en cours...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: 700; color: #0F172A;")
        container.addWidget(label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(6)
        container.addWidget(self.progress_bar)

        self.loading_info = QLabel("Connexion au serveur d'analyse...")
        self.loading_info.setAlignment(Qt.AlignCenter)
        self.loading_info.setStyleSheet("color: #64748B; font-size: 12px; margin-top: 8px;")
        container.addWidget(self.loading_info)

        wrapper = QWidget()
        wrapper.setLayout(container)
        self.result_layout.addWidget(wrapper)

    def update_loading(self, message):
        if hasattr(self, "loading_info"):
            self.loading_info.setText(message)

    def ocr_finished(self, data):
        self.facture_data = data
        self.show_result(data)

    def ocr_error(self, message):
        self.clear_result()
        QMessageBox.critical(self, "Erreur OCR", f"L'analyse de la facture a échoué :\n\n{message}")
        self.show_empty_state()

    def ocr_thread_finished(self):
        self.bouton_importer.setEnabled(True)
        self.bouton_scan.setEnabled(True)
        self.ocr_thread = None
        self.ocr_worker = None

    def show_result(self, data):
        if not isinstance(data, dict):
            QMessageBox.critical(self, "Erreur OCR", "Format de réponse invalide.")
            return

        facture_data = data.get("data") or data.get("resultat", {}).get("data") or data
        self.facture_data = facture_data
        self.clear_result()

        widget = FactureResultWidget(facture_data, self)
        widget.validated.connect(self.validate_facture)
        self.result_layout.addWidget(widget)
        self.scroll_area.verticalScrollBar().setValue(0)

    def validate_facture(self, data):
        try:
            # Conversion des données UI -> API
            facture_api = self.prepare_facture_for_api(data)

            # Enregistrement dans la base via BackendAPI
            resultat = BackendAPI.enregistrer_facture(facture_api)

            # Confirmation du succès
            QMessageBox.information(
                self,
                "Facture enregistrée",
                "La facture a été validée et enregistrée avec succès."
            )

            # Signal vers le composant parent et retour à l'état initial
            self.facture_validated.emit(resultat)
            self.show_empty_state()

        except requests.exceptions.HTTPError as e:
            # =========================================================
            # GESTION DES DOUBLONS (CODE HTTP 409 CONFLICT)
            # =========================================================
            if e.response is not None and e.response.status_code == 409:
                num_facture = data.get("numero", "inconnu")
                QMessageBox.warning(
                    self,
                    "Facture déjà existante",
                    f"La facture numéro '{num_facture}' a déjà été enregistrée dans le système.\n\n"
                    "Aucun doublon n'a été créé."
                )
                return

            # Gestion des autres erreurs HTTP (ex: 400, 422, 500)
            detail = ""
            try:
                if e.response is not None:
                    response_data = e.response.json()
                    detail = response_data.get("detail", str(response_data))
            except Exception:
                detail = str(e)

            QMessageBox.critical(
                self,
                "Erreur d'enregistrement",
                f"Impossible d'enregistrer la facture.\n\n{detail}"
            )
            traceback.print_exc()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur d'enregistrement",
                f"Une erreur est survenue lors de l'enregistrement.\n\n{str(e)}"
            )
            traceback.print_exc()
            
    def prepare_facture_for_api(self, data):
        fournisseur = data.get("fournisseur")
        fournisseur_id = fournisseur.get("id") if isinstance(fournisseur, dict) else None
        
        fournisseur_data = None
        if isinstance(fournisseur, dict):
            fournisseur_data = {
                "name": fournisseur.get("name") or fournisseur.get("nom"),
                "address": fournisseur.get("address") or fournisseur.get("adresse"),
                "city": fournisseur.get("city") or fournisseur.get("ville"),
                "phone": fournisseur.get("phone") or fournisseur.get("telephone"),
                "email": fournisseur.get("email"),
                "ice": fournisseur.get("ice")
            }
            fournisseur_data = {k: v for k, v in fournisseur_data.items() if v and str(v).strip()}

        lignes = []
        for article in data.get("articles", []):
            if isinstance(article, dict):
                lignes.append({
                    "designation": article.get("designation"),
                    "reference": article.get("reference"),
                    "quantite": self.to_decimal(article.get("quantite")),
                    "prix_unitaire": self.to_decimal(article.get("prix_unitaire")),
                    "total": self.to_decimal(article.get("total")),
                })

        return {
            "fournisseur_id": fournisseur_id,
            "fournisseur": fournisseur_data or None,
            "numero": self.clean_value(data.get("numero")),
            "date_facture": self.convert_date(data.get("date")),
            "total_ht": self.to_decimal(data.get("total_ht")),
            "total_tva": self.to_decimal(data.get("total_tva")),
            "total_ttc": self.to_decimal(data.get("total_ttc")),
            "statut": "VALIDEE",
            "lignes": lignes
        }

    def scanner_telephone(self):
        try:
            session = BackendAPI.create_scan_session()
            session_id = session.get("session_id")
            if not session_id:
                raise ValueError("Aucun ID de session généré.")

            ip = self.get_local_ip()
            url = f"http://{ip}:8000/facture-scan/mobile/{session_id}"
            self.show_scan_interface(url)
            self.start_scan_worker(session_id)
        except Exception as e:
            QMessageBox.critical(self, "Erreur Scan", f"Erreur de session mobile :\n\n{str(e)}")

    def show_scan_interface(self, url):
        self.clear_result()
        container = QVBoxLayout()
        container.setAlignment(Qt.AlignCenter)

        titre = QLabel("📱 Scanner la facture avec votre téléphone")
        titre.setStyleSheet("font-size: 18px; font-weight: 800; color: #0F172A;")
        container.addWidget(titre, alignment=Qt.AlignCenter)

        qr = qrcode.make(url)
        qr_path = Path("temp_scan_qr.png")
        qr.save(str(qr_path))

        pixmap = QPixmap(str(qr_path)).scaled(240, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        container.addWidget(qr_label, alignment=Qt.AlignCenter)

        self.scan_status_label = QLabel(" En attente du transfert mobile...")
        self.scan_status_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #2563EB;")
        container.addWidget(self.scan_status_label, alignment=Qt.AlignCenter)

        wrapper = QWidget()
        wrapper.setLayout(container)
        self.result_layout.addWidget(wrapper)

    def start_scan_worker(self, session_id):
        self.bouton_importer.setEnabled(False)
        self.bouton_scan.setEnabled(False)

        self.scan_thread = QThread()
        self.scan_worker = ScanWorker(session_id)
        self.scan_worker.moveToThread(self.scan_thread)

        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.progress.connect(self.update_scan_progress)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.error.connect(self.scan_error)

        self.scan_worker.finished.connect(self.scan_thread.quit)
        self.scan_worker.error.connect(self.scan_thread.quit)
        self.scan_thread.finished.connect(self.scan_worker.deleteLater)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)
        self.scan_thread.finished.connect(self.scan_thread_finished)

        self.scan_thread.start()

    def update_scan_progress(self, message):
        if hasattr(self, "scan_status_label"):
            self.scan_status_label.setText(message)

    def scan_finished(self, data):
        self.show_result(data)

    def scan_error(self, message):
        self.clear_result()
        QMessageBox.critical(self, "Erreur scan", f"Le scan mobile a échoué :\n\n{message}")
        self.show_empty_state()

    def scan_thread_finished(self):
        self.bouton_importer.setEnabled(True)
        self.bouton_scan.setEnabled(True)
        self.scan_thread = None
        self.scan_worker = None

    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    @staticmethod
    def clean_value(value):
        return str(value).strip() if value and str(value).strip() else None

    @staticmethod
    def to_decimal(value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        val = str(value).replace("\u00a0", "").replace(" ", "")
        if "," in val:
            val = val.replace(".", "").replace(",", ".")
        try:
            return float(val)
        except ValueError:
            return None

    @staticmethod
    def convert_date(value):
        if not value:
            return None
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
            try:
                return datetime.strptime(str(value).strip(), fmt).strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError:
                continue
        return None
    