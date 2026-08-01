from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QMessageBox
)

from PySide6.QtCore import Qt


class ResultWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.result = None

        self.build_ui()

    # --------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(self)

        titre = QLabel("Résultat OCR")

        titre.setAlignment(Qt.AlignCenter)

        titre.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
        """)

        layout.addWidget(titre)

        self.form = QFormLayout()

        self.lblType = QLabel("-")
        self.lblNumero = QLabel("-")
        self.lblDate = QLabel("-")
        self.lblFournisseur = QLabel("-")
        self.lblHT = QLabel("-")
        self.lblTVA = QLabel("-")
        self.lblTTC = QLabel("-")

        self.form.addRow("Document :", self.lblType)
        self.form.addRow("Numéro :", self.lblNumero)
        self.form.addRow("Date :", self.lblDate)
        self.form.addRow("Fournisseur :", self.lblFournisseur)
        self.form.addRow("Total HT :", self.lblHT)
        self.form.addRow("TVA :", self.lblTVA)
        self.form.addRow("Total TTC :", self.lblTTC)

        layout.addLayout(self.form)

        layout.addStretch()

        self.saveButton = QPushButton("Enregistrer")

        self.saveButton.setMinimumHeight(42)

        self.newButton = QPushButton("Nouvelle facture")

        self.newButton.setMinimumHeight(42)

        layout.addWidget(self.saveButton)
        layout.addWidget(self.newButton)

        self.hide()

    # --------------------------------------------------

    def set_result(self, result: dict):

        self.result = result

        self.lblType.setText(result.get("document_type", ""))

        data = result.get("data", {})

        self.lblNumero.setText(
            str(data.get("numero", "-"))
        )

        self.lblDate.setText(
            str(data.get("date", "-"))
        )

        self.lblFournisseur.setText(
            str(data.get("fournisseur", "-"))
        )

        self.lblHT.setText(
            str(data.get("total_ht", "-"))
        )

        self.lblTVA.setText(
            str(data.get("tva", "-"))
        )

        self.lblTTC.setText(
            str(data.get("total_ttc", "-"))
        )

        self.show()

    # --------------------------------------------------

    def clear(self):

        self.lblType.setText("-")
        self.lblNumero.setText("-")
        self.lblDate.setText("-")
        self.lblFournisseur.setText("-")
        self.lblHT.setText("-")
        self.lblTVA.setText("-")
        self.lblTTC.setText("-")

        self.hide()

    # --------------------------------------------------

    def saved(self):

        QMessageBox.information(

            self,

            "OCR",

            "Document enregistré avec succès."

        )
        