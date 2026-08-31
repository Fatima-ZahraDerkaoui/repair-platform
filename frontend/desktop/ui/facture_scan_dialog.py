from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, QTimer
from services.backend_api import BackendAPI


class FactureScanDialog(QDialog):

    ocrFinished = Signal(dict)

    def __init__(self, image_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scanner une facture")
        self.resize(500, 320)
        self.image_path = image_path

        if self.image_path is None:
            self.init_ui()
        else:
            self.init_ocr_ui()
            QTimer.singleShot(100, self.lancer_ocr_direct)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        titre = QLabel("Importation d'une facture")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size: 20px; font-weight: 800; color: #0F172A;")
        layout.addWidget(titre)

        description = QLabel("Choisissez le mode de numérisation souhaité :")
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #64748B; font-size: 13px;")
        layout.addWidget(description)

        layout.addStretch()

        boutons = QHBoxLayout()
        bouton_image = QPushButton("📁 Choisir un fichier")
        bouton_image.setFixedHeight(45)
        bouton_image.setCursor(Qt.PointingHandCursor)
        bouton_image.clicked.connect(self.choisir_image)
        boutons.addWidget(bouton_image)

        layout.addLayout(boutons)
        layout.addStretch()

        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.reject)
        layout.addWidget(bouton_annuler)

    def init_ocr_ui(self):
        layout = QVBoxLayout(self)
        titre = QLabel("Analyse en cours...")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A;")
        layout.addWidget(titre)

        self.ocr_status = QLabel("🔵 Transmission du document...")
        self.ocr_status.setAlignment(Qt.AlignCenter)
        self.ocr_status.setStyleSheet("color: #2563EB; font-size: 13px;")
        layout.addWidget(self.ocr_status)

    def choisir_image(self):
        fichier, _ = QFileDialog.getOpenFileName(
            self, "Choisir une facture", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if fichier:
            self.image_path = fichier
            self.init_ocr_ui()
            self.lancer_ocr_direct()

    def lancer_ocr_direct(self):
        if not self.image_path:
            return
        try:
            response = BackendAPI.analyser_facture_direct(self.image_path)
            resultat = response.get("resultat")
            if not resultat:
                raise Exception("Le serveur n'a renvoyé aucun résultat d'analyse.")

            self.ocrFinished.emit(resultat)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur OCR", str(e))
            self.reject()
            