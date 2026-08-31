from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QLineEdit,
    QAbstractItemView,
    QSizePolicy,
    QToolButton
)
from PySide6.QtCore import Signal, Qt

# ============================================================
# STYLE DU WIDGET RESULTAT
# ============================================================
WIDGET_STYLE = """
QGroupBox {
    font-weight: bold;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #1E293B;
}

QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #0F172A;
}

QLineEdit:read-only {
    background-color: #F8FAFC;
    color: #475569;
    border: 1px solid #E2E8F0;
}

QLineEdit:focus {
    border: 2px solid #2563EB;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 16px;
    color: #334155;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #F1F5F9;
}

QPushButton#btnValider {
    background-color: #2563EB;
    color: white;
    border: none;
}

QPushButton#btnValider:hover {
    background-color: #1D4ED8;
}

QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
}

QHeaderView::section {
    background-color: #F1F5F9;
    color: #475569;
    font-weight: 700;
    font-size: 11px;
    padding: 6px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
}
"""


class FactureResultWidget(QWidget):

    validated = Signal(dict)

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.data = data or {}
        self.edit_mode = False

        self.setMinimumWidth(650)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet(WIDGET_STYLE)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Titre
        titre = QLabel("Résultat de l'analyse de la facture")
        titre.setStyleSheet("font-size: 20px; font-weight: 800; color: #0F172A; padding: 4px 0;")
        layout.addWidget(titre)

        # Blocs de données
        layout.addWidget(self.create_infos_group())
        layout.addWidget(self.create_articles_group())
        layout.addWidget(self.create_totaux_group())
        layout.addLayout(self.create_buttons())

        self.set_editable(False)

    def create_infos_group(self):
        groupe = QGroupBox("Informations Générales")
        layout = QFormLayout()
        layout.setSpacing(10)

        self.numero = self.create_field(self.data.get("numero"))
        self.date = self.create_field(self.data.get("date"))

        fournisseur = self.data.get("fournisseur")
        fournisseur_nom = fournisseur.get("name", "") if isinstance(fournisseur, dict) else (fournisseur or "")
        self.fournisseur = self.create_field(fournisseur_nom)

        self.client = self.create_field(self.data.get("client"))

        layout.addRow("Numéro :", self.numero)
        layout.addRow("Date :", self.date)
        layout.addRow("Fournisseur :", self.fournisseur)
        layout.addRow("Client :", self.client)

        groupe.setLayout(layout)
        return groupe

    def create_articles_group(self):
        groupe = QGroupBox("Articles / Lignes de facture")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 12, 10, 10)

        self.table = QTableWidget()
        articles = self.data.get("articles", [])
        if not isinstance(articles, list):
            articles = []

        self.table.setColumnCount(6)
        self.table.setRowCount(len(articles))
        self.table.setHorizontalHeaderLabels(["Action", "Désignation", "Référence", "Quantité", "Prix unit.", "Total"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        for row, article in enumerate(articles):
            delete_button = QToolButton()
            delete_button.setText("🗑")
            delete_button.setToolTip("Supprimer cet article")
            delete_button.setCursor(Qt.PointingHandCursor)
            delete_button.setStyleSheet("QToolButton { border: none; color: #DC2626; font-size: 14px; } QToolButton:hover { color: #991B1B; }")
            delete_button.clicked.connect(self.supprimer_article_action)

            self.table.setCellWidget(row, 0, delete_button)

            if isinstance(article, dict):
                self.set_table_item(row, 1, article.get("designation", ""))
                self.set_table_item(row, 2, article.get("reference", ""))
                self.set_table_item(row, 3, article.get("quantite", article.get("qte", "")))
                self.set_table_item(row, 4, article.get("prix_unitaire", article.get("pu", "")))
                self.set_table_item(row, 5, article.get("total", ""))

        self.actualiser_hauteur_table()
        layout.addWidget(self.table)
        groupe.setLayout(layout)
        return groupe

    def create_totaux_group(self):
        groupe = QGroupBox("Totaux")
        layout = QFormLayout()
        layout.setSpacing(10)

        self.total_ht = self.create_field(self.data.get("total_ht"))
        self.total_tva = self.create_field(self.data.get("total_tva"))
        self.total_ttc = self.create_field(self.data.get("total_ttc"))

        layout.addRow("Total HT :", self.total_ht)
        layout.addRow("Total TVA :", self.total_tva)
        layout.addRow("Total TTC :", self.total_ttc)

        groupe.setLayout(layout)
        return groupe

    def create_buttons(self):
        layout = QHBoxLayout()
        layout.addStretch()

        self.bouton_modifier = QPushButton("Modifier")
        self.bouton_modifier.setMinimumSize(130, 40)
        self.bouton_modifier.setCursor(Qt.PointingHandCursor)
        self.bouton_modifier.clicked.connect(self.modifier)
        layout.addWidget(self.bouton_modifier)

        self.bouton_valider = QPushButton("Valider & Enregistrer")
        self.bouton_valider.setObjectName("btnValider")
        self.bouton_valider.setMinimumSize(160, 40)
        self.bouton_valider.setCursor(Qt.PointingHandCursor)
        self.bouton_valider.clicked.connect(self.valider)
        layout.addWidget(self.bouton_valider)

        return layout

    def create_field(self, value):
        field = QLineEdit()
        field.setText(str(value) if value is not None else "")
        field.setMinimumHeight(36)
        return field

    def set_table_item(self, row, column, value):
        item = QTableWidgetItem(str(value) if value is not None else "")
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, column, item)

    def modifier(self):
        self.edit_mode = not self.edit_mode
        self.set_editable(self.edit_mode)
        self.bouton_modifier.setText("Terminer modification" if self.edit_mode else "Modifier")

    def set_editable(self, editable):
        for field in [self.numero, self.date, self.fournisseur, self.client, self.total_ht, self.total_tva, self.total_ttc]:
            field.setReadOnly(not editable)

        if editable:
            self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        else:
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def table_value(self, row, column):
        item = self.table.item(row, column)
        return item.text().strip() if item else ""

    def construire_donnees(self):
        data = dict(self.data)
        data["numero"] = self.numero.text().strip()
        data["date"] = self.date.text().strip()
        data["client"] = self.client.text().strip()

        fournisseur_orig = data.get("fournisseur")
        if isinstance(fournisseur_orig, dict):
            fournisseur = dict(fournisseur_orig)
            fournisseur["name"] = self.fournisseur.text().strip()
            data["fournisseur"] = fournisseur
        else:
            data["fournisseur"] = {"name": self.fournisseur.text().strip()}

        data["total_ht"] = self.total_ht.text().strip()
        data["total_tva"] = self.total_tva.text().strip()
        data["total_ttc"] = self.total_ttc.text().strip()

        articles = []
        for row in range(self.table.rowCount()):
            designation = self.table_value(row, 1)
            reference = self.table_value(row, 2)
            quantite = self.table_value(row, 3)
            prix_unitaire = self.table_value(row, 4)
            total = self.table_value(row, 5)

            if not any([designation, reference, quantite, prix_unitaire, total]):
                continue

            articles.append({
                "designation": designation,
                "reference": reference,
                "quantite": quantite,
                "prix_unitaire": prix_unitaire,
                "total": total
            })

        data["articles"] = articles
        return data

    def valider(self):
        confirmation = QMessageBox.question(
            self, "Validation", "Voulez-vous valider et enregistrer cette facture ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if confirmation != QMessageBox.Yes:
            return

        data = self.construire_donnees()
        self.data = data
        self.set_editable(False)
        self.bouton_modifier.setText("Modifier")
        self.validated.emit(data)

    def supprimer_article_action(self):
        """Détermine la ligne exacte dynamiquement à partir du bouton cliqué."""
        button = self.sender()
        if not button:
            return
        
        index = self.table.indexAt(button.pos())
        if index.isValid():
            row = index.row()
            confirmation = QMessageBox.question(
                self, "Supprimer l'article", "Voulez-vous supprimer cet article ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if confirmation == QMessageBox.Yes:
                self.table.removeRow(row)
                self.actualiser_hauteur_table()

    def actualiser_hauteur_table(self):
        hauteur_header = self.table.horizontalHeader().sizeHint().height()
        hauteur_lignes = sum(max(self.table.rowHeight(r), 38) for r in range(self.table.rowCount()))
        hauteur = hauteur_header + hauteur_lignes + 10
        self.table.setMinimumHeight(hauteur)
        self.table.setMaximumHeight(hauteur)
        