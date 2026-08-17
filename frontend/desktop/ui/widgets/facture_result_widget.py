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


class FactureResultWidget(QWidget):

    validated = Signal(dict)

    def __init__(self, data=None, parent=None):

        super().__init__(parent)

        self.data = data or {}

        self.edit_mode = False

        self.setMinimumWidth(700)
        self.setMinimumHeight(0)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.init_ui()

    # =========================================================
    # INITIALISATION UI
    # =========================================================

    def init_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        layout.setSpacing(15)

        # =====================================================
        # TITRE
        # =====================================================

        titre = QLabel(
            "Résultat de l'analyse de la facture"
        )

        titre.setAlignment(
            Qt.AlignLeft
        )

        titre.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 8px 0;
            }
        """)

        layout.addWidget(titre)

        # =====================================================
        # INFORMATIONS
        # =====================================================

        layout.addWidget(
            self.create_infos_group()
        )

        # =====================================================
        # ARTICLES
        # =====================================================

        layout.addWidget(
            self.create_articles_group()
        )

        # =====================================================
        # TOTAUX
        # =====================================================

        layout.addWidget(
            self.create_totaux_group()
        )

        # =====================================================
        # BOUTONS
        # =====================================================

        layout.addLayout(
            self.create_buttons()
        )

        # =====================================================
        # MODE INITIAL
        # =====================================================

        self.set_editable(False)

    # =========================================================
    # INFORMATIONS FACTURE
    # =========================================================

    def create_infos_group(self):

        groupe = QGroupBox(
            "Informations de la facture"
        )

        layout = QFormLayout()

        layout.setSpacing(10)

        # -----------------------------------------------------
        # NUMERO
        # -----------------------------------------------------

        self.numero = self.create_field(
            self.data.get("numero")
        )

        # -----------------------------------------------------
        # DATE
        # -----------------------------------------------------

        self.date = self.create_field(
            self.data.get("date")
        )

        # -----------------------------------------------------
        # FOURNISSEUR
        # -----------------------------------------------------

        fournisseur = self.data.get(
            "fournisseur"
        )

        if isinstance(fournisseur, dict):

            fournisseur_nom = fournisseur.get(
                "name",
                ""
            )

        else:

            fournisseur_nom = (
                fournisseur or ""
            )

        self.fournisseur = self.create_field(
            fournisseur_nom
        )

        # -----------------------------------------------------
        # CLIENT
        # -----------------------------------------------------

        self.client = self.create_field(
            self.data.get("client")
        )

        # -----------------------------------------------------
        # FORM
        # -----------------------------------------------------

        layout.addRow(
            "Numéro :",
            self.numero
        )

        layout.addRow(
            "Date :",
            self.date
        )

        layout.addRow(
            "Fournisseur :",
            self.fournisseur
        )

        layout.addRow(
            "Client :",
            self.client
        )

        groupe.setLayout(
            layout
        )

        return groupe

    # =========================================================
    # ARTICLES
    # =========================================================
    def create_articles_group(self):

        groupe = QGroupBox(
            "Articles"
        )

        layout = QVBoxLayout()

        layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        layout.setSpacing(10)

        # =====================================================
        # TABLE
        # =====================================================

        self.table = QTableWidget()

        articles = self.data.get(
            "articles",
            []
        )

        if not isinstance(articles, list):
            articles = []

        self.table.setColumnCount(6)

        self.table.setRowCount(
            len(articles)
        )

        self.table.setHorizontalHeaderLabels([
            "Action",
            "Désignation",
            "Référence",
            "Quantité",
            "Prix unitaire",
            "Total"
        ])

        # =====================================================
        # HEADER
        # =====================================================

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        # =====================================================
        # APPARENCE
        # =====================================================

        self.table.verticalHeader().setDefaultSectionSize(
            40
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.setWordWrap(
            True
        )

        # =====================================================
        # SCROLLBAR
        # =====================================================

        # Pas de scrollbar INTERNE.
        # La scrollbar de FacturesPage gère toute la facture.
        self.table.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        # =====================================================
        # ARTICLES
        # =====================================================

        for row, article in enumerate(articles):

            # -------------------------------------------------
            # SUPPRIMER
            # -------------------------------------------------

            delete_button = QToolButton()

            delete_button.setText("🗑")

            delete_button.setToolTip(
                "Supprimer cet article"
            )

            delete_button.setCursor(
                Qt.PointingHandCursor
            )

            delete_button.clicked.connect(
                lambda checked=False, r=row: self.supprimer_article(r)
            )

            self.table.setCellWidget(
                row,
                0,
                delete_button
            )

            if not isinstance(article, dict):
                continue

            # -------------------------------------------------
            # DESIGNATION
            # -------------------------------------------------

            self.set_table_item(
                row,
                1,
                article.get(
                    "designation",
                    ""
                )
            )

            # -------------------------------------------------
            # REFERENCE
            # -------------------------------------------------

            self.set_table_item(
                row,
                2,
                article.get(
                    "reference",
                    ""
                )
            )

            # -------------------------------------------------
            # QUANTITE
            # -------------------------------------------------

            quantite = article.get(
                "quantite",
                article.get(
                    "qte",
                    ""
                )
            )

            self.set_table_item(
                row,
                3,
                quantite
            )

            # -------------------------------------------------
            # PRIX UNITAIRE
            # -------------------------------------------------

            prix_unitaire = article.get(
                "prix_unitaire",
                article.get(
                    "pu",
                    ""
                )
            )

            self.set_table_item(
                row,
                4,
                prix_unitaire
            )

            # -------------------------------------------------
            # TOTAL
            # -------------------------------------------------

            self.set_table_item(
                row,
                5,
                article.get(
                    "total",
                    ""
                )
            )

        # =====================================================
        # HAUTEUR AUTOMATIQUE
        # =====================================================

        # On force Qt à calculer correctement les tailles.
        self.table.resizeRowsToContents()

        hauteur_header = (
            self.table.horizontalHeader().sizeHint().height()
        )

        hauteur_lignes = 0

        for row in range(
            self.table.rowCount()
        ):
            hauteur_lignes += max(
                self.table.rowHeight(row),
                40
            )

        # Petite marge pour le cadre de la table
        hauteur = (
            hauteur_header
            + hauteur_lignes
            + 8
        )

        self.table.setMinimumHeight(
            hauteur
        )

        self.table.setMaximumHeight(
            hauteur
        )

        # =====================================================
        # LAYOUT
        # =====================================================

        layout.addWidget(
            self.table
        )

        groupe.setLayout(
            layout
        )

        return groupe

    # =========================================================
    # TOTAUX
    # =========================================================

    def create_totaux_group(self):

        groupe = QGroupBox(
            "Totaux"
        )

        layout = QFormLayout()

        layout.setSpacing(10)

        self.total_ht = self.create_field(
            self.data.get("total_ht")
        )

        self.total_tva = self.create_field(
            self.data.get("total_tva")
        )

        self.total_ttc = self.create_field(
            self.data.get("total_ttc")
        )

        layout.addRow(
            "Total HT :",
            self.total_ht
        )

        layout.addRow(
            "Total TVA :",
            self.total_tva
        )

        layout.addRow(
            "Total TTC :",
            self.total_ttc
        )

        groupe.setLayout(
            layout
        )

        return groupe

    # =========================================================
    # BOUTONS
    # =========================================================

    def create_buttons(self):

        layout = QHBoxLayout()

        layout.addStretch()

        # -----------------------------------------------------
        # MODIFIER
        # -----------------------------------------------------

        self.bouton_modifier = QPushButton(
            "Modifier"
        )

        self.bouton_modifier.setMinimumSize(
            150,
            45
        )

        self.bouton_modifier.clicked.connect(
            self.modifier
        )

        layout.addWidget(
            self.bouton_modifier
        )

        # -----------------------------------------------------
        # VALIDER
        # -----------------------------------------------------

        self.bouton_valider = QPushButton(
            "Valider"
        )

        self.bouton_valider.setMinimumSize(
            150,
            45
        )

        self.bouton_valider.clicked.connect(
            self.valider
        )

        layout.addWidget(
            self.bouton_valider
        )

        return layout

    # =========================================================
    # CREER CHAMP
    # =========================================================

    def create_field(self, value):

        field = QLineEdit()

        if value is None:
            value = ""

        field.setText(
            str(value)
        )

        field.setMinimumHeight(
            35
        )

        return field

    # =========================================================
    # TABLE ITEM
    # =========================================================

    def set_table_item(
        self,
        row,
        column,
        value
    ):

        if value is None:
            value = ""

        item = QTableWidgetItem(
            str(value)
        )

        item.setTextAlignment(
            Qt.AlignCenter
        )

        self.table.setItem(
            row,
            column,
            item
        )

    # =========================================================
    # MODIFIER
    # =========================================================

    def modifier(self):

        self.edit_mode = not self.edit_mode

        self.set_editable(
            self.edit_mode
        )

        if self.edit_mode:

            self.bouton_modifier.setText(
                "Terminer modification"
            )

        else:

            self.bouton_modifier.setText(
                "Modifier"
            )

    # =========================================================
    # MODE EDITION
    # =========================================================

    def set_editable(self, editable):

        self.numero.setReadOnly(
            not editable
        )

        self.date.setReadOnly(
            not editable
        )

        self.fournisseur.setReadOnly(
            not editable
        )

        self.client.setReadOnly(
            not editable
        )

        self.total_ht.setReadOnly(
            not editable
        )

        self.total_tva.setReadOnly(
            not editable
        )

        self.total_ttc.setReadOnly(
            not editable
        )

        if editable:

            self.table.setEditTriggers(
                QAbstractItemView.DoubleClicked
                | QAbstractItemView.EditKeyPressed
                | QAbstractItemView.SelectedClicked
            )

        else:

            self.table.setEditTriggers(
                QAbstractItemView.NoEditTriggers
            )

    # =========================================================
    # RECUPERER VALEUR TABLE
    # =========================================================

    def table_value(
        self,
        row,
        column
    ):

        item = self.table.item(
            row,
            column
        )

        if item is None:
            return ""

        return item.text().strip()

    # =========================================================
    # CONSTRUIRE DONNEES
    # =========================================================

    def construire_donnees(self):

        data = dict(
            self.data
        )

        # -----------------------------------------------------
        # INFORMATIONS
        # -----------------------------------------------------

        data["numero"] = (
            self.numero.text().strip()
        )

        data["date"] = (
            self.date.text().strip()
        )

        data["client"] = (
            self.client.text().strip()
        )

        # -----------------------------------------------------
        # FOURNISSEUR
        # -----------------------------------------------------

        fournisseur_original = data.get(
            "fournisseur"
        )

        if isinstance(
            fournisseur_original,
            dict
        ):

            fournisseur = dict(
                fournisseur_original
            )

            fournisseur["name"] = (
                self.fournisseur.text().strip()
            )

            data["fournisseur"] = (
                fournisseur
            )

        else:

            data["fournisseur"] = {
                "name": (
                    self.fournisseur.text().strip()
                )
            }

        # -----------------------------------------------------
        # TOTAUX
        # -----------------------------------------------------

        data["total_ht"] = (
            self.total_ht.text().strip()
        )

        data["total_tva"] = (
            self.total_tva.text().strip()
        )

        data["total_ttc"] = (
            self.total_ttc.text().strip()
        )

        # -----------------------------------------------------
        # ARTICLES
        # -----------------------------------------------------

        articles = []

        for row in range(
            self.table.rowCount()
        ):

            designation = self.table_value(
                row,
                1
            )

            reference = self.table_value(
                row,
                2
            )

            quantite = self.table_value(
                row,
                3
            )

            prix_unitaire = self.table_value(
                row,
                4
            )

            total = self.table_value(
                row,
                5
            )

            # Ignorer une ligne totalement vide
            if not any([
                designation,
                reference,
                quantite,
                prix_unitaire,
                total
            ]):
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

    # =========================================================
    # VALIDER
    # =========================================================

    def valider(self):

        confirmation = QMessageBox.question(
            self,
            "Validation",
            "Voulez-vous valider cette facture ?",
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation != QMessageBox.Yes:
            return

        # -----------------------------------------------------
        # RECUPERER LES MODIFICATIONS
        # -----------------------------------------------------

        data = self.construire_donnees()

        self.data = data

        self.edit_mode = False

        self.set_editable(
            False
        )

        self.bouton_modifier.setText(
            "Modifier"
        )

        # -----------------------------------------------------
        # ENVOYER AU PARENT
        # -----------------------------------------------------

        self.validated.emit(
            data
        )

    def supprimer_article(self, row):

        if row < 0 or row >= self.table.rowCount():
            return

        confirmation = QMessageBox.question(
            self,
            "Supprimer l'article",
            "Voulez-vous supprimer cet article ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation != QMessageBox.Yes:
            return

        self.table.removeRow(row)

        self.table.resizeRowsToContents()

        self.actualiser_hauteur_table()

    def actualiser_hauteur_table(self):

        hauteur_header = (
            self.table.horizontalHeader().sizeHint().height()
        )

        hauteur_lignes = 0

        for row in range(self.table.rowCount()):

            hauteur_lignes += max(
                self.table.rowHeight(row),
                40
            )

        hauteur = (
            hauteur_header
            + hauteur_lignes
            + 8
        )

        self.table.setMinimumHeight(
            hauteur
        )

        self.table.setMaximumHeight(
            hauteur
        )
