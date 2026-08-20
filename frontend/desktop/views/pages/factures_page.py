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
    QScrollArea,
    QDialog
)
from pathlib import Path
from PySide6.QtGui import QPixmap
from PySide6.QtCore import (
    Signal,
    Qt,
    QThread
)
import socket
import qrcode

from services.backend_api import BackendAPI
from services.ocr_worker import OCRWorker
from services.scan_worker import ScanWorker

class FacturesPage(QWidget):

    facture_validated = Signal(dict)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.facture_data = None

        self.ocr_thread = None
        self.ocr_worker = None

        self.init_ui()

    # =========================================================
    # UI
    # =========================================================

    def init_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            30,
            25,
            30,
            20
        )

        main_layout.setSpacing(15)

        # =====================================================
        # HEADER
        # =====================================================

        titre = QLabel(
            "Gestion des factures"
        )

        titre.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
            }
        """)

        main_layout.addWidget(titre)

        description = QLabel(
            "Importez une facture ou utilisez le scan mobile "
            "pour extraire automatiquement ses informations."
        )

        description.setWordWrap(True)

        description.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
            }
        """)

        main_layout.addWidget(description)

        # =====================================================
        # ACTIONS
        # =====================================================

        actions = QHBoxLayout()

        actions.setSpacing(12)

        self.bouton_importer = QPushButton(
            "📄  Importer une facture"
        )

        self.bouton_importer.setMinimumSize(
            190,
            48
        )

        self.bouton_importer.clicked.connect(
            self.importer_facture
        )

        actions.addWidget(
            self.bouton_importer
        )

        self.bouton_scan = QPushButton(
            "📱  Scanner avec téléphone"
        )

        self.bouton_scan.setMinimumSize(
            210,
            48
        )

        self.bouton_scan.clicked.connect(
            self.scanner_telephone
        )

        actions.addWidget(
            self.bouton_scan
        )

        actions.addStretch()

        main_layout.addLayout(actions)

        # =====================================================
        # SCROLL AREA
        # =====================================================

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        # -----------------------------------------------------
        # CONTENU DU SCROLL
        # -----------------------------------------------------

        self.result_container = QFrame()

        self.result_container.setFrameShape(
            QFrame.StyledPanel
        )

        self.result_container.setMinimumWidth(
            0
        )

        self.result_layout = QVBoxLayout(
            self.result_container
        )

        self.result_layout.setContentsMargins(
            20,
            20,
            20,
            30
        )

        self.result_layout.setSpacing(
            15
        )

        self.scroll_area.setWidget(
            self.result_container
        )

        main_layout.addWidget(
            self.scroll_area,
            1
        )

        # =====================================================
        # EMPTY STATE
        # =====================================================

        self.show_empty_state()

    # =========================================================
    # EMPTY STATE
    # =========================================================

    def show_empty_state(self):

        self.clear_result()

        label = QLabel(
            "Aucune facture analysée.\n\n"
            "Importez une facture pour commencer."
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setMinimumHeight(
            250
        )

        label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 16px;
                padding: 40px;
            }
        """)

        self.result_layout.addWidget(
            label
        )

        self.result_layout.addStretch()

    # =========================================================
    # IMPORT FACTURE
    # =========================================================

    def importer_facture(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une facture",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if not file_path:
            return

        self.start_ocr(
            file_path
        )

    # =========================================================
    # START OCR
    # =========================================================

    def start_ocr(self, file_path):

        self.bouton_importer.setEnabled(
            False
        )

        self.bouton_scan.setEnabled(
            False
        )

        self.show_loading()

        # -----------------------------------------------------
        # THREAD
        # -----------------------------------------------------

        self.ocr_thread = QThread()

        self.ocr_worker = OCRWorker(
            file_path
        )

        self.ocr_worker.moveToThread(
            self.ocr_thread
        )

        # -----------------------------------------------------
        # CONNECTIONS
        # -----------------------------------------------------

        self.ocr_thread.started.connect(
            self.ocr_worker.run
        )

        self.ocr_worker.progress.connect(
            self.update_loading
        )

        self.ocr_worker.finished.connect(
            self.ocr_finished
        )

        self.ocr_worker.error.connect(
            self.ocr_error
        )

        self.ocr_worker.finished.connect(
            self.ocr_thread.quit
        )

        self.ocr_worker.error.connect(
            self.ocr_thread.quit
        )

        self.ocr_thread.finished.connect(
            self.ocr_worker.deleteLater
        )

        self.ocr_thread.finished.connect(
            self.ocr_thread.deleteLater
        )

        self.ocr_thread.finished.connect(
            self.ocr_thread_finished
        )

        self.ocr_thread.start()

    # =========================================================
    # LOADING
    # =========================================================

    def show_loading(self):

        self.clear_result()

        container = QVBoxLayout()

        container.setContentsMargins(
            30,
            50,
            30,
            50
        )

        label = QLabel(
            "Analyse de la facture en cours..."
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
        """)

        container.addWidget(
            label
        )

        self.loading_label = label

        # -----------------------------------------------------

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            0
        )

        self.progress_bar.setMinimumHeight(
            10
        )

        container.addWidget(
            self.progress_bar
        )

        # -----------------------------------------------------

        self.loading_info = QLabel(
            "Connexion au serveur OCR..."
        )

        self.loading_info.setAlignment(
            Qt.AlignCenter
        )

        self.loading_info.setStyleSheet("""
            QLabel {
                color: #6b7280;
                padding: 10px;
            }
        """)

        container.addWidget(
            self.loading_info
        )

        wrapper = QWidget()

        wrapper.setLayout(
            container
        )

        self.result_layout.addWidget(
            wrapper
        )

        self.result_layout.addStretch()

    # =========================================================
    # UPDATE LOADING
    # =========================================================

    def update_loading(self, message):

        if hasattr(
            self,
            "loading_info"
        ):

            self.loading_info.setText(
                message
            )

    # =========================================================
    # OCR FINISHED
    # =========================================================

    def ocr_finished(self, data):

        self.facture_data = data

        self.show_result(
            data
        )

    # =========================================================
    # OCR ERROR
    # =========================================================

    def ocr_error(self, message):

        self.clear_result()

        label = QLabel(
            "❌ Erreur pendant l'analyse OCR"
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setStyleSheet("""
            QLabel {
                color: #b91c1c;
                font-size: 18px;
                font-weight: bold;
                padding: 30px;
            }
        """)

        self.result_layout.addWidget(
            label
        )

        self.result_layout.addStretch()

        QMessageBox.critical(
            self,
            "Erreur OCR",
            (
                "L'analyse de la facture a échoué.\n\n"
                f"{message}"
            )
        )

    # =========================================================
    # THREAD FINISHED
    # =========================================================

    def ocr_thread_finished(self):

        self.bouton_importer.setEnabled(
            True
        )

        self.bouton_scan.setEnabled(
            True
        )

        self.ocr_thread = None
        self.ocr_worker = None

    # =========================================================
    # SHOW RESULT
    # =========================================================

    def show_result(self, data):

        if not isinstance(data, dict):

            QMessageBox.critical(
                self,
                "Erreur OCR",
                "Le serveur a retourné une réponse invalide."
            )

            return

        # =====================================================
        # EXTRACTION DES DONNÉES
        # =====================================================

        facture_data = data.get("data")

        if not isinstance(facture_data, dict):

            resultat = data.get("resultat")

            if isinstance(resultat, dict):

                facture_data = resultat.get("data")

        if not isinstance(facture_data, dict):

            facture_data = data

        self.facture_data = facture_data

        # =====================================================
        # NETTOYER
        # =====================================================

        self.clear_result()

        # =====================================================
        # WIDGET RESULTAT
        # =====================================================

        from ui.widgets.facture_result_widget import (
            FactureResultWidget
        )

        widget = FactureResultWidget(
            facture_data,
            self
        )

        # IMPORTANT :
        # permet au widget de prendre toute la largeur
        widget.setSizePolicy(
            widget.sizePolicy().horizontalPolicy(),
            widget.sizePolicy().verticalPolicy()
        )

        widget.validated.connect(
            self.validate_facture
        )

        self.result_layout.addWidget(
            widget
        )

        # Espace après la facture
        self.result_layout.addSpacing(
            20
        )

        # =====================================================
        # REVENIR EN HAUT
        # =====================================================

        self.scroll_area.verticalScrollBar().setValue(
            0
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    def validate_facture(self, data):

        self.facture_data = data

        self.facture_validated.emit(
            data
        )

    # =========================================================
    # SCAN TELEPHONE
    # =========================================================
    # =========================================================
    # SCAN TELEPHONE
    # =========================================================

    def scanner_telephone(self):

        try:

            # =====================================================
            # 1. CREER SESSION
            # =====================================================

            session = BackendAPI.create_scan_session()

            session_id = session.get(
                "session_id"
            )

            if not session_id:

                raise ValueError(
                    "Le serveur n'a pas retourné de session_id."
                )

            self.scan_session_id = session_id

            # =====================================================
            # 2. IP DU PC
            # =====================================================

            ip = self.get_local_ip()

            # =====================================================
            # 3. URL MOBILE
            # =====================================================

            url = (
                f"http://{ip}:8000"
                f"/facture-scan/mobile/{session_id}"
            )

            print()
            print("=" * 80)
            print("SCAN TELEPHONE")
            print("=" * 80)

            print(
                "SESSION ID :",
                session_id
            )

            print(
                "IP PC :",
                ip
            )

            print(
                "URL MOBILE :",
                url
            )

            print("=" * 80)

            # =====================================================
            # 4. AFFICHER LE SCAN DANS L'INTERFACE PRINCIPALE
            # =====================================================

            self.show_scan_interface(
                url
            )

            # =====================================================
            # 5. LANCER LE POLLING
            # =====================================================

            self.start_scan_worker(
                session_id
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erreur scan téléphone",
                (
                    "Impossible de démarrer le scan téléphone.\n\n"
                    f"{str(e)}"
                )
            )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear_result(self):

        while self.result_layout.count():

            item = self.result_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

    def get_local_ip(self):

        try:

            socket_conn = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )

            socket_conn.connect(
                ("8.8.8.8", 80)
            )

            ip = socket_conn.getsockname()[0]

            socket_conn.close()

            return ip

        except Exception:

            return "127.0.0.1"

    
    def start_scan_worker(
        self,
        session_id
    ):

        self.bouton_importer.setEnabled(
            False
        )

        self.bouton_scan.setEnabled(
            False
        )

        self.scan_thread = QThread()

        self.scan_worker = ScanWorker(
            session_id
        )

        self.scan_worker.moveToThread(
            self.scan_thread
        )

        # =====================================================
        # SIGNALS
        # =====================================================

        self.scan_thread.started.connect(
            self.scan_worker.run
        )

        self.scan_worker.progress.connect(
            self.update_scan_progress
        )

        self.scan_worker.finished.connect(
            self.scan_finished
        )

        self.scan_worker.error.connect(
            self.scan_error
        )

        self.scan_worker.finished.connect(
            self.scan_thread.quit
        )

        self.scan_worker.error.connect(
            self.scan_thread.quit
        )

        self.scan_thread.finished.connect(
            self.scan_worker.deleteLater
        )

        self.scan_thread.finished.connect(
            self.scan_thread.deleteLater
        )

        self.scan_thread.finished.connect(
            self.scan_thread_finished
        )

        self.scan_thread.start()

    def update_scan_progress(
        self,
        message
    ):

        print(
            "[SCAN]",
            message
        )

        if hasattr(
            self,
            "scan_status_label"
        ):

            self.scan_status_label.setText(
                message
            )
            
    def scan_finished(
        self,
        data
    ):

        print()
        print("=" * 80)
        print("RESULTAT SCAN TELEPHONE")
        print("=" * 80)

        print(
            data
        )

        print("=" * 80)

        # =====================================================
        # AFFICHER RESULTAT
        # =====================================================

        self.show_result(
            data
        )

    def scan_error(
        self,
        message
    ):

        self.clear_result()

        label = QLabel(
            "❌ Erreur pendant le scan de la facture"
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setWordWrap(
            True
        )

        label.setStyleSheet("""
            QLabel {
                color: #b91c1c;
                font-size: 18px;
                font-weight: bold;
                padding: 30px;
            }
        """)

        self.result_layout.addWidget(
            label
        )

        detail = QLabel(
            str(message)
        )

        detail.setAlignment(
            Qt.AlignCenter
        )

        detail.setWordWrap(
            True
        )

        detail.setStyleSheet("""
            QLabel {
                color: #6b7280;
                padding: 15px;
            }
        """)

        self.result_layout.addWidget(
            detail
        )

        self.result_layout.addStretch()

        QMessageBox.critical(
            self,
            "Erreur scan téléphone",
            (
                "Le scan de la facture a échoué.\n\n"
                f"{message}"
            )
        )

    def scan_thread_finished(self):

        self.bouton_importer.setEnabled(
            True
        )

        self.bouton_scan.setEnabled(
            True
        )

        self.scan_thread = None
        self.scan_worker = None

    # =========================================================
    # INTERFACE SCAN TELEPHONE
    # =========================================================

    def show_scan_interface(self, url):

        self.clear_result()

        # =====================================================
        # TITRE
        # =====================================================

        titre = QLabel(
            "📱 Scanner la facture avec votre téléphone"
        )

        titre.setAlignment(
            Qt.AlignCenter
        )

        titre.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 15px;
            }
        """)

        self.result_layout.addWidget(
            titre
        )

        # =====================================================
        # INSTRUCTIONS
        # =====================================================

        instructions = QLabel(
            "1. Scannez le QR Code avec votre téléphone.\n"
            "2. Prenez une photo de la facture ou choisissez-la depuis la galerie.\n"
            "3. Envoyez la facture.\n"
            "4. Attendez la fin de l'analyse OCR."
        )

        instructions.setAlignment(
            Qt.AlignCenter
        )

        instructions.setWordWrap(
            True
        )

        instructions.setStyleSheet("""
            QLabel {
                color: #4b5563;
                font-size: 14px;
                padding: 10px;
            }
        """)

        self.result_layout.addWidget(
            instructions
        )

        # =====================================================
        # QR CODE
        # =====================================================

        qr = qrcode.make(
            url
        )

        qr_path = (
            Path("temp_scan_qr.png")
        )

        qr.save(
            str(qr_path)
        )

        image = QPixmap(
            str(qr_path)
        )

        image = image.scaled(
            320,
            320,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        qr_label = QLabel()

        qr_label.setPixmap(
            image
        )

        qr_label.setAlignment(
            Qt.AlignCenter
        )

        self.result_layout.addWidget(
            qr_label
        )

        # =====================================================
        # URL
        # =====================================================

        url_label = QLabel(
            url
        )

        url_label.setAlignment(
            Qt.AlignCenter
        )

        url_label.setWordWrap(
            True
        )

        url_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 11px;
                padding: 8px;
            }
        """)

        self.result_layout.addWidget(
            url_label
        )

        # =====================================================
        # STATUT
        # =====================================================

        self.scan_status_label = QLabel(
            "⏳ En attente de la facture..."
        )

        self.scan_status_label.setAlignment(
            Qt.AlignCenter
        )

        self.scan_status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
        """)

        self.result_layout.addWidget(
            self.scan_status_label
        )

        # =====================================================
        # PROGRESSION
        # =====================================================

        self.scan_progress_bar = QProgressBar()

        self.scan_progress_bar.setRange(
            0,
            0
        )

        self.scan_progress_bar.setMinimumHeight(
            8
        )

        self.result_layout.addWidget(
            self.scan_progress_bar
        )

        self.result_layout.addStretch()

        # =====================================================
        # RETOUR EN HAUT
        # =====================================================

        self.scroll_area.verticalScrollBar().setValue(
            0
        )