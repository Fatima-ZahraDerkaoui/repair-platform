from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QHBoxLayout
)

from PySide6.QtCore import Qt, Signal

from services.backend_api import BackendAPI


class FactureScanDialog(QDialog):

    ocrFinished = Signal(dict)

    def __init__(
        self,
        image_path=None,
        parent=None
    ):

        # =====================================================
        # CONSTRUCTEUR
        # =====================================================

        super().__init__(parent)

        self.setWindowTitle(
            "Scanner une facture"
        )

        self.resize(
            600,
            400
        )

        # Image éventuellement déjà sélectionnée
        self.image_path = image_path

        # =====================================================
        # CAS 1 :
        # aucune image fournie
        #
        # => afficher le choix :
        #    - choisir une image
        #    - téléphone
        # =====================================================

        if self.image_path is None:

            self.init_ui()

        # =====================================================
        # CAS 2 :
        # une image est déjà fournie
        #
        # => NE PAS afficher les boutons
        # => lancer directement l'OCR
        # =====================================================

        else:

            self.init_ocr_ui()

            # Petit délai pour laisser le dialog
            # s'afficher correctement
            from PySide6.QtCore import QTimer

            QTimer.singleShot(
                100,
                self.lancer_ocr_direct
            )

    # =========================================================
    # INTERFACE : CHOIX IMAGE / TELEPHONE
    # =========================================================

    def init_ui(self):

        layout = QVBoxLayout()

        # -----------------------------------------------------
        # TITRE
        # -----------------------------------------------------

        titre = QLabel(
            "IMPORTATION D'UNE FACTURE"
        )

        titre.setAlignment(
            Qt.AlignCenter
        )

        titre.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
            """
        )

        layout.addWidget(
            titre
        )

        # -----------------------------------------------------
        # DESCRIPTION
        # -----------------------------------------------------

        description = QLabel(
            "Choisissez la méthode d'importation de la facture."
        )

        description.setAlignment(
            Qt.AlignCenter
        )

        description.setStyleSheet(
            """
            font-size: 15px;
            color: #555;
            padding: 10px;
            """
        )

        layout.addWidget(
            description
        )

        layout.addStretch()

        # -----------------------------------------------------
        # BOUTONS
        # -----------------------------------------------------

        boutons = QHBoxLayout()

        # =====================================================
        # IMAGE PC
        # =====================================================

        bouton_image = QPushButton(
            "📁 Choisir une image"
        )

        bouton_image.setMinimumHeight(
            60
        )

        bouton_image.clicked.connect(
            self.choisir_image
        )

        boutons.addWidget(
            bouton_image
        )

        # =====================================================
        # TELEPHONE
        # =====================================================

        bouton_camera = QPushButton(
            "📱 Prendre une image"
        )

        bouton_camera.setMinimumHeight(
            60
        )

        bouton_camera.clicked.connect(
            self.prendre_image
        )

        boutons.addWidget(
            bouton_camera
        )

        layout.addLayout(
            boutons
        )

        layout.addStretch()

        # -----------------------------------------------------
        # ANNULER
        # -----------------------------------------------------

        bouton_annuler = QPushButton(
            "Annuler"
        )

        bouton_annuler.clicked.connect(
            self.reject
        )

        layout.addWidget(
            bouton_annuler
        )

        self.setLayout(
            layout
        )

    # =========================================================
    # INTERFACE PENDANT OCR DIRECT
    # =========================================================

    def init_ocr_ui(self):

        layout = QVBoxLayout()

        titre = QLabel(
            "ANALYSE DE LA FACTURE"
        )

        titre.setAlignment(
            Qt.AlignCenter
        )

        titre.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
            """
        )

        layout.addWidget(
            titre
        )

        self.ocr_status = QLabel(
            "🔵 Analyse OCR en cours..."
        )

        self.ocr_status.setAlignment(
            Qt.AlignCenter
        )

        self.ocr_status.setStyleSheet(
            """
            font-size: 16px;
            padding: 20px;
            """
        )

        layout.addWidget(
            self.ocr_status
        )

        self.setLayout(
            layout
        )

    # =========================================================
    # CHOISIR UNE IMAGE
    # =========================================================

    def choisir_image(self):

        fichier, _ = QFileDialog.getOpenFileName(

            self,

            "Choisir une facture",

            "",

            (
                "Images (*.png *.jpg *.jpeg *.bmp *.webp);;"
                "Tous les fichiers (*)"
            )
        )

        if not fichier:

            return

        self.image_path = fichier

        self.init_ocr_ui()

        self.lancer_ocr_direct()

    # =========================================================
    # OCR DIRECT
    # =========================================================

    def lancer_ocr_direct(self):

        if not self.image_path:

            return

        try:

            print()
            print("=" * 80)
            print("OCR DIRECT FRONTEND")
            print("=" * 80)

            print(
                "Image :",
                self.image_path
            )

            # =================================================
            # APPEL DIRECT DU BACKEND
            # =================================================

            response = (
                BackendAPI.analyser_facture_direct(
                    self.image_path
                )
            )

            # =================================================
            # RESULTAT
            # =================================================

            resultat = response.get(
                "resultat"
            )

            if resultat is None:

                raise Exception(
                    "Le backend n'a pas retourné "
                    "de résultat OCR."
                )

            print(
                "OCR terminé avec succès."
            )

            print(
                "=" * 80
            )

            # =================================================
            # SIGNAL
            # =================================================

            self.ocrFinished.emit(
                resultat
            )

            # =================================================
            # FERMER
            # =================================================

            self.accept()

        except Exception as e:

            print(
                "Erreur OCR :",
                e
            )

            QMessageBox.critical(

                self,

                "Erreur OCR",

                str(e)
            )

    # =========================================================
    # TELEPHONE
    # =========================================================

    def prendre_image(self):

        try:

            # =================================================
            # SESSION UNIQUEMENT POUR TELEPHONE
            # =================================================

            session = (
                BackendAPI.create_scan_session()
            )

            session_id = session.get(
                "session_id"
            )

            if not session_id:

                QMessageBox.critical(

                    self,

                    "Erreur",

                    "Impossible de créer la session de scan."
                )

                return

            print()
            print("=" * 80)
            print("SESSION TELEPHONE")
            print("=" * 80)

            print(
                "Session :",
                session_id
            )

            print(
                "QR Code :",
                session.get("qr_code")
            )

            print(
                "=" * 80
            )

            QMessageBox.information(

                self,

                "Scan téléphone",

                (
                    "La session téléphone a été créée.\n\n"
                    "Le QR Code sera affiché dans "
                    "l'interface principale."
                )
            )

            self.reject()

        except Exception as e:

            QMessageBox.critical(

                self,

                "Erreur scan téléphone",

                str(e)
            )
