from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QMessageBox,
    QFrame,
    QAbstractItemView,
    QStackedWidget,
)

from PySide6.QtCore import Qt

import requests


# ============================================================
# CONFIGURATION API
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# STOCK PAGE
# ============================================================

class StockPage(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(parent)

        self.stocks = []

        self.current_stock = None

        self.form_mode = None

        self.setup_ui()

        self.load_stocks()

    # ========================================================
    # INTERFACE PRINCIPALE
    # ========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        main_layout.setSpacing(
            18
        )

        # ====================================================
        # STACK
        # ====================================================

        self.stack = QStackedWidget()

        self.list_page = self.create_list_page()

        self.form_page = self.create_form_page()

        self.stack.addWidget(
            self.list_page
        )

        self.stack.addWidget(
            self.form_page
        )

        main_layout.addWidget(
            self.stack
        )

        self.stack.setCurrentWidget(
            self.list_page
        )

    # ========================================================
    # PAGE LISTE
    # ========================================================

    def create_list_page(self):

        page = QWidget()

        main_layout = QVBoxLayout(
            page
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            18
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = QHBoxLayout()

        header.setSpacing(
            10
        )

        title = QLabel(
            "Gestion du stock"
        )

        title.setStyleSheet("""
            QLabel {
                font-size: 30px;
                font-weight: 700;
            }
        """)

        header.addWidget(
            title
        )

        header.addStretch()

        # ----------------------------------------------------
        # ACTUALISER
        # ----------------------------------------------------

        self.refresh_button = QPushButton(
            "↻  Actualiser"
        )

        self.refresh_button.setFixedHeight(
            42
        )

        self.refresh_button.setMinimumWidth(
            120
        )

        self.refresh_button.setCursor(
            Qt.PointingHandCursor
        )

        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f5;
                border: 1px solid #d9dde2;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #e9ecef;
            }

            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)

        self.refresh_button.clicked.connect(
            self.load_all
        )

        header.addWidget(
            self.refresh_button
        )

        # ----------------------------------------------------
        # AJOUTER
        # ----------------------------------------------------

        self.add_button = QPushButton(
            "+  Ajouter une pièce"
        )

        self.add_button.setFixedHeight(
            42
        )

        self.add_button.setMinimumWidth(
            170
        )

        self.add_button.setCursor(
            Qt.PointingHandCursor
        )

        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 18px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)

        self.add_button.clicked.connect(
            self.add_stock
        )

        header.addWidget(
            self.add_button
        )

        main_layout.addLayout(
            header
        )

        # ====================================================
        # SOUS-TITRE
        # ====================================================

        subtitle = QLabel(
            "Gestion des pièces, quantités et seuils minimum."
        )

        subtitle.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
            }
        """)

        main_layout.addWidget(
            subtitle
        )

        # ====================================================
        # STATISTIQUES
        # ====================================================

        stats_layout = QHBoxLayout()

        stats_layout.setSpacing(
            12
        )

        self.total_card = self.create_stat_card(
            "Pièces",
            "0"
        )

        self.low_stock_card = self.create_stat_card(
            "Stock faible",
            "0"
        )

        self.out_stock_card = self.create_stat_card(
            "Rupture",
            "0"
        )

        self.unread_card = self.create_stat_card(
            "Alertes non lues",
            "0"
        )

        stats_layout.addWidget(
            self.total_card
        )

        stats_layout.addWidget(
            self.low_stock_card
        )

        stats_layout.addWidget(
            self.out_stock_card
        )

        stats_layout.addWidget(
            self.unread_card
        )

        main_layout.addLayout(
            stats_layout
        )

        # ====================================================
        # TABLE STOCK
        # ====================================================

        self.table = QTableWidget()

        self.table.setColumnCount(
            9
        )

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Pièce",
            "Référence",
            "Catégorie",
            "Quantité",
            "Seuil min.",
            "Prix unitaire",
            "Fournisseur",
            "Actions"
        ])

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.setShowGrid(
            False
        )

        self.table.verticalHeader().setVisible(
            False
        )

        header_view = self.table.horizontalHeader()

        header_view.setSectionResizeMode(
            QHeaderView.Stretch
        )

        header_view.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header_view.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        header_view.setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        header_view.setSectionResizeMode(
            6,
            QHeaderView.ResizeToContents
        )

        header_view.setSectionResizeMode(
            8,
            QHeaderView.ResizeToContents
        )

        main_layout.addWidget(
            self.table
        )

        # ====================================================
        # TITRE ALERTES
        # ====================================================

        alerts_header = QHBoxLayout()

        alerts_title = QLabel(
            "Alertes de stock"
        )

        alerts_title.setStyleSheet("""
            QLabel {
                font-size: 21px;
                font-weight: 700;
            }
        """)

        alerts_header.addWidget(
            alerts_title
        )

        alerts_header.addStretch()

        self.alerts_count_label = QLabel(
            "0 alerte"
        )

        self.alerts_count_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 13px;
            }
        """)

        alerts_header.addWidget(
            self.alerts_count_label
        )

        main_layout.addLayout(
            alerts_header
        )

        # ====================================================
        # CONTENEUR ALERTES
        # ====================================================

        self.alerts_container = QFrame()

        self.alerts_container.setStyleSheet("""
            QFrame {
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                background-color: transparent;
            }
        """)

        alerts_container_layout = QVBoxLayout(
            self.alerts_container
        )

        alerts_container_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # ----------------------------------------------------
        # MESSAGE AUCUNE ALERTE
        # ----------------------------------------------------

        self.no_alert_label = QLabel(
            "✓  Aucune alerte de stock"
        )

        self.no_alert_label.setAlignment(
            Qt.AlignCenter
        )

        self.no_alert_label.setMinimumHeight(
            80
        )

        self.no_alert_label.setStyleSheet("""
            QLabel {
                color: #16a34a;
                font-size: 15px;
                font-weight: 600;
                border: none;
            }
        """)

        alerts_container_layout.addWidget(
            self.no_alert_label
        )

        # ----------------------------------------------------
        # TABLE ALERTES
        # ----------------------------------------------------

        self.alerts_table = QTableWidget()

        self.alerts_table.setColumnCount(
            5
        )

        self.alerts_table.setHorizontalHeaderLabels([
            "Pièce",
            "Quantité demandée",
            "Disponible",
            "Message",
            "Date de l'alerte"
        ])

        self.alerts_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.alerts_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.alerts_table.setShowGrid(
            False
        )

        self.alerts_table.verticalHeader().setVisible(
            False
        )

        alerts_header_view = (
            self.alerts_table.horizontalHeader()
        )

        alerts_header_view.setSectionResizeMode(
            QHeaderView.Stretch
        )

        alerts_header_view.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        alerts_header_view.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        alerts_header_view.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        alerts_container_layout.addWidget(
            self.alerts_table
        )

        main_layout.addWidget(
            self.alerts_container
        )

        return page

    # ========================================================
    # PAGE FORMULAIRE
    # ========================================================

    def create_form_page(self):

        page = QWidget()

        main_layout = QVBoxLayout(
            page
        )

        main_layout.setContentsMargins(
            10,
            5,
            10,
            10
        )

        main_layout.setSpacing(
            15
        )

        # ====================================================
        # HEADER FORMULAIRE
        # ====================================================

        header = QHBoxLayout()

        # Espace gauche pour permettre au titre
        # d'être visuellement centré
        header.addStretch(
            1
        )

        self.form_title = QLabel(
            "Ajouter une pièce"
        )

        self.form_title.setAlignment(
            Qt.AlignCenter
        )

        self.form_title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: 700;
            }
        """)

        header.addWidget(
            self.form_title,
            2
        )

        # ====================================================
        # BOUTON RETOUR À DROITE
        # ====================================================

        self.back_button = QPushButton(
            "←  Retour"
        )

        self.back_button.setFixedSize(
            120,
            42
        )

        self.back_button.setCursor(
            Qt.PointingHandCursor
        )

        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                color: #2563eb;
                border: 1px solid #bfdbfe;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #eff6ff;
                border-color: #2563eb;
            }

            QPushButton:pressed {
                background-color: #dbeafe;
            }
        """)

        self.back_button.clicked.connect(
            self.cancel_form
        )

        header.addWidget(
            self.back_button,
            1,
            Qt.AlignRight
        )

        main_layout.addLayout(
            header
        )

        # ====================================================
        # SOUS-TITRE
        # ====================================================

        self.form_subtitle = QLabel(
            "Remplissez les informations de la nouvelle pièce."
        )

        self.form_subtitle.setAlignment(
            Qt.AlignCenter
        )

        self.form_subtitle.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
            }
        """)

        main_layout.addWidget(
            self.form_subtitle
        )

        # ====================================================
        # FORMULAIRE
        # ====================================================

        form_frame = QFrame()

        form_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                background-color: transparent;
            }
        """)

        form_layout = QVBoxLayout(
            form_frame
        )

        form_layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        form_layout.setSpacing(
            20
        )

        form = QGridLayout()

        form.setHorizontalSpacing(
            25
        )

        form.setVerticalSpacing(
            16
        )

        # ====================================================
        # STYLE LABELS
        # ====================================================

        label_style = """
            QLabel {
                font-size: 14px;
                font-weight: 600;
            }
        """

        # ====================================================
        # NOM
        # ====================================================

        label = QLabel(
            "Nom de la pièce *"
        )

        label.setStyleSheet(
            label_style
        )

        form.addWidget(
            label,
            0,
            0
        )

        self.nom_piece = QLineEdit()

        self.nom_piece.setPlaceholderText(
            "Ex : Tambour Ricoh"
        )

        self.nom_piece.setMinimumHeight(
            42
        )

        form.addWidget(
            self.nom_piece,
            0,
            1
        )

        # ====================================================
        # RÉFÉRENCE
        # ====================================================

        label = QLabel(
            "Référence"
        )

        label.setStyleSheet(
            label_style
        )

        form.addWidget(
            label,
            1,
            0
        )

        self.reference = QLineEdit()

        self.reference.setPlaceholderText(
            "Ex : AF1015"
        )

        self.reference.setMinimumHeight(
            42
        )

        form.addWidget(
            self.reference,
            1,
            1
        )

        # ====================================================
        # CATÉGORIE
        # ====================================================

        label = QLabel(
            "Catégorie"
        )

        label.setStyleSheet(
            label_style
        )

        form.addWidget(
            label,
            2,
            0
        )

        self.categorie = QLineEdit()

        self.categorie.setPlaceholderText(
            "Ex : Imprimante"
        )

        self.categorie.setMinimumHeight(
            42
        )

        form.addWidget(
            self.categorie,
            2,
            1
        )

        # ====================================================
        # QUANTITÉ
        # ====================================================

        label = QLabel(
            "Quantité"
        )

        label.setStyleSheet(
            label_style
        )

        form.addWidget(
            label,
            3,
            0
        )

        self.quantite = QSpinBox()

        self.quantite.setRange(
            0,
            999999
        )

        self.quantite.setMinimumHeight(
            42
        )

        form.addWidget(
            self.quantite,
            3,
            1
        )

        # ====================================================
        # SEUIL
        # ====================================================

        label = QLabel(
            "Seuil minimum"
        )

        label.setStyleSheet(
            label_style
        )

        form.addWidget(
            label,
            4,
            0
        )

        self.seuil_min = QSpinBox()

        self.seuil_min.setRange(
            0,
            999999
        )

        self.seuil_min.setValue(
            5
        )

        self.seuil_min.setMinimumHeight(
            42
        )

        form.addWidget(
            self.seuil_min,
            4,
            1
        )

        # ====================================================
        # PRIX
        # ====================================================

        label = QLabel(
            "Prix unitaire"
        )

        label.setStyleSheet(
            label_style
        )

        form.addWidget(
            label,
            5,
            0
        )

        self.prix_unitaire = QDoubleSpinBox()

        self.prix_unitaire.setRange(
            0,
            999999999
        )

        self.prix_unitaire.setDecimals(
            2
        )

        self.prix_unitaire.setSuffix(
            " DH"
        )

        self.prix_unitaire.setMinimumHeight(
            42
        )

        form.addWidget(
            self.prix_unitaire,
            5,
            1
        )

        # ====================================================
        # FOURNISSEUR
        # ====================================================

        label = QLabel(
            "Fournisseur"
        )

        label.setStyleSheet(
            label_style
        )

        form.addWidget(
            label,
            6,
            0
        )

        self.fournisseur = QLineEdit()

        self.fournisseur.setPlaceholderText(
            "Nom du fournisseur"
        )

        self.fournisseur.setMinimumHeight(
            42
        )

        form.addWidget(
            self.fournisseur,
            6,
            1
        )

        form.setColumnStretch(
            0,
            1
        )

        form.setColumnStretch(
            1,
            3
        )

        form_layout.addLayout(
            form
        )

        # ====================================================
        # BOUTONS
        # ====================================================

        buttons = QHBoxLayout()

        buttons.setSpacing(
            12
        )

        buttons.addStretch()

        # ----------------------------------------------------
        # ANNULER
        # ----------------------------------------------------

        self.cancel_button = QPushButton(
            "Annuler"
        )

        self.cancel_button.setFixedSize(
            180,
            45
        )

        self.cancel_button.setCursor(
            Qt.PointingHandCursor
        )

        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #e5e7eb;
            }

            QPushButton:pressed {
                background-color: #d1d5db;
            }
        """)

        self.cancel_button.clicked.connect(
            self.cancel_form
        )

        buttons.addWidget(
            self.cancel_button
        )

        # ----------------------------------------------------
        # ENREGISTRER
        # ----------------------------------------------------

        self.save_button = QPushButton(
            "Enregistrer"
        )

        self.save_button.setFixedSize(
            180,
            45
        )

        self.save_button.setCursor(
            Qt.PointingHandCursor
        )

        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)

        self.save_button.clicked.connect(
            self.save_form
        )

        buttons.addWidget(
            self.save_button
        )

        buttons.addStretch()

        form_layout.addLayout(
            buttons
        )

        main_layout.addWidget(
            form_frame
        )

        main_layout.addStretch()

        return page

    # ========================================================
    # CARTE STATISTIQUE
    # ========================================================

    def create_stat_card(
        self,
        title,
        value
    ):

        frame = QFrame()

        frame.setMinimumHeight(
            90
        )

        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                background-color: transparent;
            }
        """)

        layout = QVBoxLayout(
            frame
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        label_title = QLabel(
            title
        )

        label_title.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #6b7280;
                border: none;
            }
        """)

        value_label = QLabel(
            value
        )

        value_label.setStyleSheet("""
            QLabel {
                font-size: 25px;
                font-weight: 700;
                border: none;
            }
        """)

        layout.addWidget(
            label_title
        )

        layout.addWidget(
            value_label
        )

        frame.value_label = value_label

        return frame

    # ========================================================
    # CHARGEMENT GLOBAL
    # ========================================================

    def load_all(self):

        self.load_stocks()

        self.load_alerts()

    # ========================================================
    # CHARGER STOCK
    # ========================================================

    def load_stocks(self):

        try:

            response = requests.get(
                f"{API_URL}/stock/",
                timeout=10
            )

            response.raise_for_status()

            self.stocks = response.json()

            self.display_stocks()

            self.update_statistics()

            self.load_alerts()

        except requests.RequestException as e:

            QMessageBox.critical(
                self,
                "Erreur",
                "Impossible de récupérer le stock.\n\n"
                f"Détail : {e}"
            )

    # ========================================================
    # AFFICHAGE STOCK
    # ========================================================

    def display_stocks(self):

        self.table.setRowCount(
            0
        )

        for stock in self.stocks:

            row = self.table.rowCount()

            self.table.insertRow(
                row
            )

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(
                        stock.get(
                            "id",
                            ""
                        )
                    )
                )
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(
                        stock.get(
                            "nom_piece",
                            ""
                        )
                    )
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(
                        stock.get(
                            "reference"
                        )
                        or "-"
                    )
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    str(
                        stock.get(
                            "categorie"
                        )
                        or "-"
                    )
                )
            )

            quantite = int(
                stock.get(
                    "quantite",
                    0
                )
                or 0
            )

            seuil = int(
                stock.get(
                    "seuil_min",
                    0
                )
                or 0
            )

            quantite_item = QTableWidgetItem(
                str(
                    quantite
                )
            )

            seuil_item = QTableWidgetItem(
                str(
                    seuil
                )
            )

            self.table.setItem(
                row,
                4,
                quantite_item
            )

            self.table.setItem(
                row,
                5,
                seuil_item
            )

            prix = stock.get(
                "prix_unitaire"
            )

            if prix is None:

                prix_text = "-"

            else:

                try:

                    prix_text = (
                        f"{float(prix):.2f} DH"
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    prix_text = str(
                        prix
                    )

            self.table.setItem(
                row,
                6,
                QTableWidgetItem(
                    prix_text
                )
            )

            self.table.setItem(
                row,
                7,
                QTableWidgetItem(
                    str(
                        stock.get(
                            "fournisseur"
                        )
                        or "-"
                    )
                )
            )

            if quantite == 0:

                quantite_item.setText(
                    "0 — RUPTURE"
                )

            elif quantite <= seuil:

                quantite_item.setText(
                    f"{quantite} — FAIBLE"
                )

            # =================================================
            # ACTIONS
            # =================================================

            actions_widget = QWidget()

            actions_layout = QHBoxLayout(
                actions_widget
            )

            actions_layout.setContentsMargins(
                3,
                3,
                3,
                3
            )

            actions_layout.setSpacing(
                5
            )

            edit_button = QPushButton(
                "Modifier"
            )

            edit_button.setCursor(
                Qt.PointingHandCursor
            )

            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #eff6ff;
                    color: #2563eb;
                    border: 1px solid #bfdbfe;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-weight: 600;
                }

                QPushButton:hover {
                    background-color: #dbeafe;
                }
            """)

            edit_button.clicked.connect(
                lambda checked=False,
                s=stock: self.edit_stock(s)
            )

            

            actions_layout.addWidget(
                edit_button
            )


            self.table.setCellWidget(
                row,
                8,
                actions_widget
            )

    # ========================================================
    # STATISTIQUES
    # ========================================================

    def update_statistics(self):

        total = len(
            self.stocks
        )

        low = 0

        rupture = 0

        for stock in self.stocks:

            quantite = int(
                stock.get(
                    "quantite",
                    0
                )
                or 0
            )

            seuil = int(
                stock.get(
                    "seuil_min",
                    0
                )
                or 0
            )

            if quantite == 0:

                rupture += 1

            elif quantite <= seuil:

                low += 1

        self.total_card.value_label.setText(
            str(
                total
            )
        )

        self.low_stock_card.value_label.setText(
            str(
                low
            )
        )

        self.out_stock_card.value_label.setText(
            str(
                rupture
            )
        )

    # ========================================================
    # AJOUTER
    # ========================================================

    def add_stock(self):

        self.form_mode = "add"

        self.current_stock = None

        self.clear_form()

        self.form_title.setText(
            "Ajouter une pièce"
        )

        self.form_subtitle.setText(
            "Remplissez les informations de la nouvelle pièce."
        )

        self.save_button.setText(
            "Enregistrer"
        )

        self.stack.setCurrentWidget(
            self.form_page
        )

        self.nom_piece.setFocus()

    # ========================================================
    # MODIFIER
    # ========================================================

    def edit_stock(
        self,
        stock
    ):

        self.form_mode = "edit"

        self.current_stock = stock

        self.nom_piece.setText(
            str(
                stock.get(
                    "nom_piece"
                )
                or ""
            )
        )

        self.reference.setText(
            str(
                stock.get(
                    "reference"
                )
                or ""
            )
        )

        self.categorie.setText(
            str(
                stock.get(
                    "categorie"
                )
                or ""
            )
        )

        self.quantite.setValue(
            int(
                stock.get(
                    "quantite",
                    0
                )
                or 0
            )
        )

        self.seuil_min.setValue(
            int(
                stock.get(
                    "seuil_min",
                    0
                )
                or 0
            )
        )

        prix = stock.get(
            "prix_unitaire"
        )

        if prix is not None:

            try:

                self.prix_unitaire.setValue(
                    float(
                        prix
                    )
                )

            except (
                ValueError,
                TypeError
            ):

                self.prix_unitaire.setValue(
                    0
                )

        else:

            self.prix_unitaire.setValue(
                0
            )

        self.fournisseur.setText(
            str(
                stock.get(
                    "fournisseur"
                )
                or ""
            )
        )

        self.form_title.setText(
            "Modifier une pièce"
        )

        self.form_subtitle.setText(
            "Modifiez les informations de la pièce."
        )

        self.save_button.setText(
            "Enregistrer"
        )

        self.stack.setCurrentWidget(
            self.form_page
        )

        self.nom_piece.setFocus()

    # ========================================================
    # RETOUR
    # ========================================================

    def cancel_form(self):

        self.form_mode = None

        self.current_stock = None

        self.clear_form()

        self.stack.setCurrentWidget(
            self.list_page
        )

    # ========================================================
    # RÉINITIALISER FORMULAIRE
    # ========================================================

    def clear_form(self):

        self.nom_piece.clear()

        self.reference.clear()

        self.categorie.clear()

        self.quantite.setValue(
            0
        )

        self.seuil_min.setValue(
            5
        )

        self.prix_unitaire.setValue(
            0
        )

        self.fournisseur.clear()

    # ========================================================
    # DONNÉES FORMULAIRE
    # ========================================================

    def get_form_data(self):

        return {

            "nom_piece":
                self.nom_piece.text().strip(),

            "reference":
                self.reference.text().strip()
                or None,

            "categorie":
                self.categorie.text().strip()
                or None,

            "quantite":
                self.quantite.value(),

            "seuil_min":
                self.seuil_min.value(),

            "prix_unitaire":
                self.prix_unitaire.value(),

            "fournisseur":
                self.fournisseur.text().strip()
                or None,
        }

    # ========================================================
    # ENREGISTRER
    # ========================================================

    def save_form(self):

        nom = self.nom_piece.text().strip()

        if not nom:

            QMessageBox.warning(
                self,
                "Champ obligatoire",
                "Le nom de la pièce est obligatoire."
            )

            self.nom_piece.setFocus()

            return

        data = self.get_form_data()

        if self.form_mode == "add":

            self.create_stock(
                data
            )

        elif self.form_mode == "edit":

            self.update_stock(
                data
            )

    # ========================================================
    # CRÉER STOCK
    # ========================================================

    def create_stock(
        self,
        data
    ):

        try:

            response = requests.post(
                f"{API_URL}/stock/",
                json=data,
                timeout=10
            )

            if not response.ok:

                try:

                    detail = response.json().get(
                        "detail",
                        response.text
                    )

                except Exception:

                    detail = response.text

                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Impossible d'ajouter la pièce.\n\n"
                    f"{detail}"
                )

                return

            QMessageBox.information(
                self,
                "Succès",
                "La pièce a été ajoutée avec succès."
            )

            self.cancel_form()

            self.load_all()

        except requests.RequestException as e:

            QMessageBox.critical(
                self,
                "Erreur",
                "Erreur de communication avec l'API.\n\n"
                f"{e}"
            )

    # ========================================================
    # MODIFIER STOCK
    # ========================================================

    def update_stock(
        self,
        data
    ):

        if not self.current_stock:

            return

        stock_id = self.current_stock.get(
            "id"
        )

        try:

            response = requests.put(
                f"{API_URL}/stock/{stock_id}",
                json=data,
                timeout=10
            )

            if not response.ok:

                try:

                    detail = response.json().get(
                        "detail",
                        response.text
                    )

                except Exception:

                    detail = response.text

                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Impossible de modifier la pièce.\n\n"
                    f"{detail}"
                )

                return

            QMessageBox.information(
                self,
                "Succès",
                "La pièce a été modifiée avec succès."
            )

            self.cancel_form()

            self.load_all()

        except requests.RequestException as e:

            QMessageBox.critical(
                self,
                "Erreur",
                "Erreur de communication avec l'API.\n\n"
                f"{e}"
            )

    # ========================================================
    # SUPPRIMER STOCK
    # ========================================================

    # ========================================================
    # CHARGER ALERTES
    # ========================================================

    def load_alerts(self):

        try:

            response = requests.get(
                f"{API_URL}/alertes-stock/",
                timeout=10
            )

            response.raise_for_status()

            alerts = response.json()

            # =================================================
            # FILTRER LES ALERTES RÉSOLUES
            # =================================================
            #
            # Une alerte reste affichée seulement si le stock
            # disponible est inférieur à la quantité demandée.
            #
            # Exemple :
            #
            # demandée = 10
            # disponible = 3
            # -> alerte conservée
            #
            # demandée = 10
            # disponible = 10
            # -> alerte retirée de l'affichage
            #
            # demandée = 10
            # disponible = 15
            # -> alerte retirée de l'affichage
            #
            # =================================================

            active_alerts = []

            for alert in alerts:

                quantite_demandee = int(
                    alert.get(
                        "quantite_demandee",
                        0
                    )
                    or 0
                )

                quantite_disponible = int(
                    alert.get(
                        "quantite_disponible",
                        0
                    )
                    or 0
                )

                if quantite_disponible < quantite_demandee:

                    active_alerts.append(
                        alert
                    )

            self.display_alerts(
                active_alerts
            )

            # =================================================
            # ALERTES NON LUES
            # =================================================

            unread_response = requests.get(
                f"{API_URL}/alertes-stock/non-lues",
                timeout=10
            )

            if unread_response.ok:

                unread = unread_response.json()

                active_unread = []

                for alert in unread:

                    quantite_demandee = int(
                        alert.get(
                            "quantite_demandee",
                            0
                        )
                        or 0
                    )

                    quantite_disponible = int(
                        alert.get(
                            "quantite_disponible",
                            0
                        )
                        or 0
                    )

                    if (
                        quantite_disponible
                        < quantite_demandee
                    ):

                        active_unread.append(
                            alert
                        )

                self.unread_card.value_label.setText(
                    str(
                        len(
                            active_unread
                        )
                    )
                )

        except requests.RequestException:

            self.alerts_table.setRowCount(
                0
            )

            self.alerts_table.setVisible(
                False
            )

            self.no_alert_label.setText(
                "Impossible de charger les alertes"
            )

            self.no_alert_label.setStyleSheet("""
                QLabel {
                    color: #dc2626;
                    font-size: 14px;
                    font-weight: 600;
                    border: none;
                }
            """)

            self.no_alert_label.setVisible(
                True
            )

            self.alerts_count_label.setText(
                "Erreur"
            )

            self.unread_card.value_label.setText(
                "0"
            )

    # ========================================================
    # AFFICHER ALERTES
    # ========================================================

    def display_alerts(
        self,
        alerts
    ):

        self.alerts_table.setRowCount(
            0
        )

        # ====================================================
        # AUCUNE ALERTE
        # ====================================================

        if not alerts:

            self.alerts_table.setVisible(
                False
            )

            self.no_alert_label.setVisible(
                True
            )

            self.no_alert_label.setText(
                "✓  Aucune alerte de stock"
            )

            self.no_alert_label.setStyleSheet("""
                QLabel {
                    color: #16a34a;
                    font-size: 15px;
                    font-weight: 600;
                    border: none;
                }
            """)

            self.alerts_count_label.setText(
                "0 alerte"
            )

            return

        # ====================================================
        # ALERTES EXISTANTES
        # ====================================================

        self.alerts_table.setVisible(
            True
        )

        self.no_alert_label.setVisible(
            False
        )

        count = len(
            alerts
        )

        if count == 1:

            self.alerts_count_label.setText(
                "1 alerte active"
            )

        else:

            self.alerts_count_label.setText(
                f"{count} alertes actives"
            )

        # ====================================================
        # REMPLIR TABLE
        # ====================================================

        for alert in alerts:

            row = self.alerts_table.rowCount()

            self.alerts_table.insertRow(
                row
            )

            # ------------------------------------------------
            # PIÈCE
            # ------------------------------------------------

            piece_name = self.get_piece_name(
                alert.get(
                    "piece_id"
                )
            )

            self.alerts_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    piece_name
                )
            )

            # ------------------------------------------------
            # DEMANDÉE
            # ------------------------------------------------

            quantite_demandee = int(
                alert.get(
                    "quantite_demandee",
                    0
                )
                or 0
            )

            self.alerts_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(
                        quantite_demandee
                    )
                )
            )

            # ------------------------------------------------
            # DISPONIBLE
            # ------------------------------------------------

            quantite_disponible = int(
                alert.get(
                    "quantite_disponible",
                    0
                )
                or 0
            )

            disponible_item = QTableWidgetItem(
                str(
                    quantite_disponible
                )
            )

            self.alerts_table.setItem(
                row,
                2,
                disponible_item
            )

            # ------------------------------------------------
            # MESSAGE
            # ------------------------------------------------

            message = str(
                alert.get(
                    "message",
                    ""
                )
            )

            self.alerts_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    message
                )
            )

            # ------------------------------------------------
            # DATE
            # ------------------------------------------------

            date = str(
                alert.get(
                    "date_creation",
                    ""
                )
            )

            date = date.replace(
                "T",
                " "
            )[:19]

            self.alerts_table.setItem(
                row,
                4,
                QTableWidgetItem(
                    date
                )
            )

            # ------------------------------------------------
            # ALIGNEMENT
            # ------------------------------------------------

            for column in range(
                5
            ):

                item = self.alerts_table.item(
                    row,
                    column
                )

                if item:

                    item.setTextAlignment(
                        Qt.AlignVCenter
                        | Qt.AlignLeft
                    )

    # ========================================================
    # NOM PIÈCE
    # ========================================================

    def get_piece_name(
        self,
        piece_id
    ):

        for stock in self.stocks:

            if stock.get(
                "id"
            ) == piece_id:

                return str(
                    stock.get(
                        "nom_piece",
                        f"Pièce #{piece_id}"
                    )
                )

        return f"Pièce #{piece_id}"
    