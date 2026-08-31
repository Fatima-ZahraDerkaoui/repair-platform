import requests

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

# ============================================================
# CONFIGURATION API
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# STYLE GLOBAL STOCK PAGE
# ============================================================

PAGE_STYLE = """
QWidget {
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    font-size: 13px;
    color: #0F172A;
    background-color: #F8FAFC;
}

QFrame#card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    color: #0F172A;
    font-size: 13px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #2563EB;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 16px;
    color: #334155;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QPushButton#primaryButton {
    background-color: #2563EB;
    color: white;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #1D4ED8;
}

QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    gridline-color: #F1F5F9;
    outline: none;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #F1F5F9;
}

QTableWidget::item:selected {
    background-color: #EFF6FF;
    color: #1E40AF;
}

QHeaderView::section {
    background-color: #F1F5F9;
    color: #475569;
    font-weight: 700;
    font-size: 12px;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    text-transform: uppercase;
}
"""


# ============================================================
# STOCK PAGE
# ============================================================

class StockPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.stocks = []
        self.filtered_stocks = []
        self.current_stock = None
        self.form_mode = None

        self.setup_ui()
        self.load_all()

    def setup_ui(self):
        self.setStyleSheet(PAGE_STYLE)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        self.stack = QStackedWidget()
        self.list_page = self.create_list_page()
        self.form_page = self.create_form_page()

        self.stack.addWidget(self.list_page)
        self.stack.addWidget(self.form_page)

        main_layout.addWidget(self.stack)
        self.stack.setCurrentWidget(self.list_page)

    # ========================================================
    # PAGE LISTE
    # ========================================================

    def create_list_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(14)

        # En-tête
        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("Gestion du stock")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #0F172A;")
        title_layout.addWidget(title)

        subtitle = QLabel("Gestion des pièces, contrôle des quantités et seuils d'alerte.")
        subtitle.setStyleSheet("color: #64748B; font-size: 13px;")
        title_layout.addWidget(subtitle)

        header.addLayout(title_layout)
        header.addStretch()

        self.add_button = QPushButton("+ Ajouter une pièce")
        self.add_button.setObjectName("primaryButton")
        self.add_button.setFixedHeight(40)
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.add_stock)
        header.addWidget(self.add_button)

        main_layout.addLayout(header)

        # Cartes Statistiques
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self.total_card = self.create_stat_card("Pièces", "0")
        self.low_stock_card = self.create_stat_card("Stock faible", "0")
        self.out_stock_card = self.create_stat_card("Rupture", "0")
        self.unread_card = self.create_stat_card("Alertes non lues", "0")

        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.low_stock_card)
        stats_layout.addWidget(self.out_stock_card)
        stats_layout.addWidget(self.unread_card)

        main_layout.addLayout(stats_layout)

        # BARRE DE RECHERCHE RAPIDE
        search_frame = QFrame()
        search_frame.setObjectName("card")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(12, 10, 12, 10)
        search_layout.setSpacing(10)

        search_lbl = QLabel("Rechercher :")
        search_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        search_layout.addWidget(search_lbl)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nom de pièce, référence, catégorie, fournisseur...")
        self.search_input.textChanged.connect(self.apply_search)
        search_layout.addWidget(self.search_input, 1)

        reset_search_btn = QPushButton("Réinitialiser")
        reset_search_btn.setCursor(Qt.PointingHandCursor)
        reset_search_btn.clicked.connect(self.reset_search)
        search_layout.addWidget(reset_search_btn)

        main_layout.addWidget(search_frame)

        # Table Stock
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Pièce", "Référence", "Catégorie",
            "Quantité", "Seuil min.", "Prix unit.", "Fournisseur", "Actions"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Stretch)
        for col in [0, 4, 5, 6]:
            header_view.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        
        # Colonne Actions fixée très compacte
        header_view.setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 80)

        main_layout.addWidget(self.table, 1)

        # Section Alertes
        alerts_header = QHBoxLayout()
        alerts_title = QLabel("Alertes de stock")
        alerts_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0F172A;")
        alerts_header.addWidget(alerts_title)
        alerts_header.addStretch()

        self.alerts_count_label = QLabel("0 alerte")
        self.alerts_count_label.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 600;")
        alerts_header.addWidget(self.alerts_count_label)

        main_layout.addLayout(alerts_header)

        self.alerts_container = QFrame()
        self.alerts_container.setObjectName("card")
        alerts_container_layout = QVBoxLayout(self.alerts_container)
        alerts_container_layout.setContentsMargins(8, 8, 8, 8)

        self.no_alert_label = QLabel("✓  Aucune alerte de stock active")
        self.no_alert_label.setAlignment(Qt.AlignCenter)
        self.no_alert_label.setMinimumHeight(50)
        self.no_alert_label.setStyleSheet("color: #16A34A; font-size: 13px; font-weight: 700;")
        alerts_container_layout.addWidget(self.no_alert_label)

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels([
            "Pièce", "Quantité demandée", "Disponible", "Message", "Date d'alerte"
        ])
        self.alerts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.alerts_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.alerts_table.verticalHeader().setVisible(False)
        self.alerts_table.setMinimumHeight(120)

        alerts_header_view = self.alerts_table.horizontalHeader()
        alerts_header_view.setSectionResizeMode(QHeaderView.Stretch)
        for c in [1, 2, 4]:
            alerts_header_view.setSectionResizeMode(c, QHeaderView.ResizeToContents)

        alerts_container_layout.addWidget(self.alerts_table)
        main_layout.addWidget(self.alerts_container)

        return page

    # ========================================================
    # PAGE FORMULAIRE
    # ========================================================

    def create_form_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(10, 5, 10, 10)
        main_layout.setSpacing(15)

        header = QHBoxLayout()
        header.addStretch(1)

        self.form_title = QLabel("Ajouter une pièce")
        self.form_title.setAlignment(Qt.AlignCenter)
        self.form_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #0F172A;")
        header.addWidget(self.form_title, 2)

        self.back_button = QPushButton("← Retour")
        self.back_button.setFixedSize(110, 38)
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self.cancel_form)
        header.addWidget(self.back_button, 1, Qt.AlignRight)

        main_layout.addLayout(header)

        self.form_subtitle = QLabel("Saisissez les caractéristiques de la pièce de rechange.")
        self.form_subtitle.setAlignment(Qt.AlignCenter)
        self.form_subtitle.setStyleSheet("color: #64748B; font-size: 13px;")
        main_layout.addWidget(self.form_subtitle)

        form_frame = QFrame()
        form_frame.setObjectName("card")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(30, 24, 30, 24)
        form_layout.setSpacing(18)

        form = QGridLayout()
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(14)

        label_style = "font-size: 13px; font-weight: 600; color: #334155;"

        lbl = QLabel("Nom de la pièce *")
        lbl.setStyleSheet(label_style)
        form.addWidget(lbl, 0, 0)
        self.nom_piece = QLineEdit()
        self.nom_piece.setPlaceholderText("Ex : Tambour Ricoh / Ecran iPhone X")
        self.nom_piece.setMinimumHeight(38)
        form.addWidget(self.nom_piece, 0, 1)

        lbl = QLabel("Référence")
        lbl.setStyleSheet(label_style)
        form.addWidget(lbl, 1, 0)
        self.reference = QLineEdit()
        self.reference.setPlaceholderText("Ex : AF1015")
        self.reference.setMinimumHeight(38)
        form.addWidget(self.reference, 1, 1)

        lbl = QLabel("Catégorie")
        lbl.setStyleSheet(label_style)
        form.addWidget(lbl, 2, 0)
        self.categorie = QLineEdit()
        self.categorie.setPlaceholderText("Ex : Imprimante / Smartphone")
        self.categorie.setMinimumHeight(38)
        form.addWidget(self.categorie, 2, 1)

        lbl = QLabel("Quantité en stock")
        lbl.setStyleSheet(label_style)
        form.addWidget(lbl, 3, 0)
        self.quantite = QSpinBox()
        self.quantite.setRange(0, 999999)
        self.quantite.setMinimumHeight(38)
        form.addWidget(self.quantite, 3, 1)

        lbl = QLabel("Seuil minimum (Alerte)")
        lbl.setStyleSheet(label_style)
        form.addWidget(lbl, 4, 0)
        self.seuil_min = QSpinBox()
        self.seuil_min.setRange(0, 999999)
        self.seuil_min.setValue(5)
        self.seuil_min.setMinimumHeight(38)
        form.addWidget(self.seuil_min, 4, 1)

        lbl = QLabel("Prix unitaire")
        lbl.setStyleSheet(label_style)
        form.addWidget(lbl, 5, 0)
        self.prix_unitaire = QDoubleSpinBox()
        self.prix_unitaire.setRange(0, 99999999)
        self.prix_unitaire.setDecimals(2)
        self.prix_unitaire.setSuffix(" DH")
        self.prix_unitaire.setMinimumHeight(38)
        form.addWidget(self.prix_unitaire, 5, 1)

        lbl = QLabel("Fournisseur")
        lbl.setStyleSheet(label_style)
        form.addWidget(lbl, 6, 0)
        self.fournisseur = QLineEdit()
        self.fournisseur.setPlaceholderText("Ex : TechData, Maroc Composants")
        self.fournisseur.setMinimumHeight(38)
        form.addWidget(self.fournisseur, 6, 1)

        form.setColumnStretch(0, 1)
        form.setColumnStretch(1, 3)
        form_layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addStretch()

        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setFixedSize(140, 40)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.cancel_form)
        buttons.addWidget(self.cancel_button)

        self.save_button = QPushButton("Enregistrer")
        self.save_button.setObjectName("primaryButton")
        self.save_button.setFixedSize(140, 40)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_form)
        buttons.addWidget(self.save_button)

        buttons.addStretch()
        form_layout.addLayout(buttons)

        main_layout.addWidget(form_frame)
        main_layout.addStretch()

        return page

    # ========================================================
    # CARTE STATISTIQUE
    # ========================================================

    def create_stat_card(self, title, value):
        frame = QFrame()
        frame.setObjectName("card")
        frame.setMinimumHeight(80)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(2)

        label_title = QLabel(title)
        label_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;")

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 22px; font-weight: 800; color: #0F172A;")

        layout.addWidget(label_title)
        layout.addWidget(value_label)

        frame.value_label = value_label
        return frame

    # ========================================================
    # CHARGEMENT & API
    # ========================================================

    def load_all(self):
        self.load_stocks()
        self.load_alerts()

    def load_stocks(self):
        try:
            response = requests.get(f"{API_URL}/stock/", timeout=10)
            response.raise_for_status()
            self.stocks = response.json()
            self.apply_search()
            self.update_statistics()
        except requests.RequestException as e:
            QMessageBox.critical(self, "Erreur API", f"Impossible de charger le stock :\n\n{e}")

    # ========================================================
    # RECHERCHE ET FILTRAGE
    # ========================================================

    def apply_search(self):
        query = self.search_input.text().strip().lower()
        if not query:
            self.filtered_stocks = list(self.stocks)
        else:
            self.filtered_stocks = [
                s for s in self.stocks
                if query in str(s.get("nom_piece", "")).lower()
                or query in str(s.get("reference", "")).lower()
                or query in str(s.get("categorie", "")).lower()
                or query in str(s.get("fournisseur", "")).lower()
            ]
        self.display_stocks(self.filtered_stocks)

    def reset_search(self):
        self.search_input.clear()
        self.apply_search()

    # ========================================================
    # AFFICHAGE DU STOCK
    # ========================================================

    def display_stocks(self, stock_list):
        self.table.setRowCount(0)

        for stock in stock_list:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(stock.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(stock.get("nom_piece", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(stock.get("reference") or "-")))
            self.table.setItem(row, 3, QTableWidgetItem(str(stock.get("categorie") or "-")))

            quantite = int(stock.get("quantite", 0) or 0)
            seuil = int(stock.get("seuil_min", 0) or 0)

            quantite_item = QTableWidgetItem(str(quantite))
            seuil_item = QTableWidgetItem(str(seuil))

            self.table.setItem(row, 4, quantite_item)
            self.table.setItem(row, 5, seuil_item)

            prix = stock.get("prix_unitaire")
            prix_text = f"{float(prix):.2f} DH" if prix is not None else "-"
            self.table.setItem(row, 6, QTableWidgetItem(prix_text))
            self.table.setItem(row, 7, QTableWidgetItem(str(stock.get("fournisseur") or "-")))

            # Badges
            if quantite == 0:
                quantite_item.setText("0 — RUPTURE")
                quantite_item.setForeground(Qt.red)
            elif quantite <= seuil:
                quantite_item.setText(f"{quantite} — FAIBLE")
                quantite_item.setForeground(Qt.darkYellow)

            # Boutons Actions très compacts (28x24 px)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(4)
            actions_layout.setAlignment(Qt.AlignCenter)

            edit_button = QPushButton("✎")
            edit_button.setToolTip("Modifier cette pièce")
            edit_button.setFixedSize(28, 15)
            edit_button.setCursor(Qt.PointingHandCursor)
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #EFF6FF;
                    color: #2563EB;
                    border: 1px solid #BFDBFE;
                    border-radius: 5px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #DBEAFE;
                    color: #1D4ED8;
                }
            """)
            edit_button.clicked.connect(lambda checked=False, s=stock: self.edit_stock(s))

            delete_button = QPushButton("✕")
            delete_button.setToolTip("Supprimer du stock")
            delete_button.setFixedSize(28, 15)
            delete_button.setCursor(Qt.PointingHandCursor)
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #FEF2F2;
                    color: #DC2626;
                    border: 1px solid #FECACA;
                    border-radius: 5px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #FEE2E2;
                    color: #B91C1C;
                }
            """)
            delete_button.clicked.connect(lambda checked=False, s=stock: self.delete_stock(s))

            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)

            self.table.setCellWidget(row, 8, actions_widget)

    # ========================================================
    # STATISTIQUES
    # ========================================================

    def update_statistics(self):
        total = len(self.stocks)
        low = 0
        rupture = 0

        for stock in self.stocks:
            quantite = int(stock.get("quantite", 0) or 0)
            seuil = int(stock.get("seuil_min", 0) or 0)

            if quantite == 0:
                rupture += 1
            elif quantite <= seuil:
                low += 1

        self.total_card.value_label.setText(str(total))
        self.low_stock_card.value_label.setText(str(low))
        self.out_stock_card.value_label.setText(str(rupture))

    # ========================================================
    # GESTION FORMULAIRE
    # ========================================================

    def add_stock(self):
        self.form_mode = "add"
        self.current_stock = None
        self.clear_form()
        self.form_title.setText("Ajouter une pièce")
        self.form_subtitle.setText("Remplissez les informations de la nouvelle pièce.")
        self.save_button.setText("Enregistrer")
        self.stack.setCurrentWidget(self.form_page)
        self.nom_piece.setFocus()

    def edit_stock(self, stock):
        self.form_mode = "edit"
        self.current_stock = stock

        self.nom_piece.setText(str(stock.get("nom_piece") or ""))
        self.reference.setText(str(stock.get("reference") or ""))
        self.categorie.setText(str(stock.get("categorie") or ""))
        self.quantite.setValue(int(stock.get("quantite", 0) or 0))
        self.seuil_min.setValue(int(stock.get("seuil_min", 0) or 0))

        prix = stock.get("prix_unitaire")
        self.prix_unitaire.setValue(float(prix) if prix is not None else 0.0)
        self.fournisseur.setText(str(stock.get("fournisseur") or ""))

        self.form_title.setText("Modifier une pièce")
        self.form_subtitle.setText("Modifiez les caractéristiques de la pièce sélectionnée.")
        self.save_button.setText("Mettre à jour")
        self.stack.setCurrentWidget(self.form_page)
        self.nom_piece.setFocus()

    def cancel_form(self):
        self.form_mode = None
        self.current_stock = None
        self.clear_form()
        self.stack.setCurrentWidget(self.list_page)

    def clear_form(self):
        self.nom_piece.clear()
        self.reference.clear()
        self.categorie.clear()
        self.quantite.setValue(0)
        self.seuil_min.setValue(5)
        self.prix_unitaire.setValue(0.0)
        self.fournisseur.clear()

    def get_form_data(self):
        return {
            "nom_piece": self.nom_piece.text().strip(),
            "reference": self.reference.text().strip() or None,
            "categorie": self.categorie.text().strip() or None,
            "quantite": self.quantite.value(),
            "seuil_min": self.seuil_min.value(),
            "prix_unitaire": self.prix_unitaire.value(),
            "fournisseur": self.fournisseur.text().strip() or None,
        }

    def save_form(self):
        nom = self.nom_piece.text().strip()
        if not nom:
            QMessageBox.warning(self, "Champ obligatoire", "Le nom de la pièce est requis.")
            self.nom_piece.setFocus()
            return

        data = self.get_form_data()
        if self.form_mode == "add":
            self.create_stock(data)
        elif self.form_mode == "edit":
            self.update_stock(data)

    def create_stock(self, data):
        try:
            response = requests.post(f"{API_URL}/stock/", json=data, timeout=10)
            if not response.ok:
                detail = response.json().get("detail", response.text) if response.headers.get("content-type") == "application/json" else response.text
                QMessageBox.warning(self, "Erreur", f"Échec de la création :\n{detail}")
                return

            QMessageBox.information(self, "Succès", "La pièce a été ajoutée avec succès.")
            self.cancel_form()
            self.load_all()
        except requests.RequestException as e:
            QMessageBox.critical(self, "Erreur réseau", f"Impossible de contacter l'API :\n{e}")

    def update_stock(self, data):
        if not self.current_stock:
            return
        stock_id = self.current_stock.get("id")

        try:
            response = requests.put(f"{API_URL}/stock/{stock_id}", json=data, timeout=10)
            if not response.ok:
                detail = response.json().get("detail", response.text) if response.headers.get("content-type") == "application/json" else response.text
                QMessageBox.warning(self, "Erreur", f"Échec de la modification :\n{detail}")
                return

            QMessageBox.information(self, "Succès", "Pièce mise à jour avec succès.")
            self.cancel_form()
            self.load_all()
        except requests.RequestException as e:
            QMessageBox.critical(self, "Erreur réseau", f"Impossible de contacter l'API :\n{e}")

    def delete_stock(self, stock):
        stock_id = stock.get("id")
        nom = stock.get("nom_piece", f"#{stock_id}")

        reply = QMessageBox.question(
            self,
            "Suppression du stock",
            f"Voulez-vous vraiment supprimer la pièce '{nom}' du stock ?\n\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            response = requests.delete(f"{API_URL}/stock/{stock_id}", timeout=10)
            if not response.ok:
                detail = response.json().get("detail", response.text) if response.headers.get("content-type") == "application/json" else response.text
                QMessageBox.warning(self, "Échec de suppression", f"Erreur : {detail}")
                return

            QMessageBox.information(self, "Succès", f"La pièce '{nom}' a été supprimée du stock.")
            self.load_all()
        except requests.RequestException as e:
            QMessageBox.critical(self, "Erreur API", f"Impossible de contacter le serveur :\n{e}")

    # ========================================================
    # ALERTES
    # ========================================================
    def load_alerts(self):
        try:
            response = requests.get(f"{API_URL}/alertes-stock/", timeout=10)
            response.raise_for_status()
            alerts = response.json()

            # Dictionnaire pour retrouver rapidement la quantité en stock par ID de pièce
            stock_dict = {s.get("id"): int(s.get("quantite", 0) or 0) for s in self.stocks}

            active_alerts = []
            for alert in alerts:
                piece_id = alert.get("piece_id")
                q_dem = int(alert.get("quantite_demandee", 0) or 0)
                
                # Récupère le stock actuel réél
                q_disp_actuelle = stock_dict.get(piece_id, int(alert.get("quantite_disponible", 0) or 0))

                # SI LE STOCK A AUGMENTÉ (disponible >= demandé), L'ALERTE EST SUPPRIMÉE DE L'AFFICHAGE
                if q_disp_actuelle < q_dem:
                    # On met à jour la quantité disponible affichée
                    alert["quantite_disponible"] = q_disp_actuelle
                    active_alerts.append(alert)
                else:
                    # En arrière-plan : informe le serveur que l'alerte est résolue / lue
                    self.resolve_alert_on_server(alert.get("id"))

            self.display_alerts(active_alerts)
            self.unread_card.value_label.setText(str(len(active_alerts)))

        except requests.RequestException:
            self.alerts_table.setRowCount(0)
            self.alerts_table.setVisible(False)
            self.no_alert_label.setText("Impossible de charger les alertes de stock")
            self.no_alert_label.setStyleSheet("color: #DC2626; font-size: 13px; font-weight: 600;")
            self.no_alert_label.setVisible(True)
            self.alerts_count_label.setText("Erreur")
            self.unread_card.value_label.setText("0")

    def resolve_alert_on_server(self, alerte_id):
        """Supprime ou marque comme lue l'alerte sur l'API quand le stock a été réapprovisionné."""
        if not alerte_id:
            return
        try:
            # Tente de supprimer l'alerte résolue sur le serveur
            requests.delete(f"{API_URL}/alertes-stock/{alerte_id}", timeout=5)
        except requests.RequestException:
            pass  # Ignore si l'API ne gère pas la suppression directe par ID4
        
    def display_alerts(self, alerts):
        self.alerts_table.setRowCount(0)

        if not alerts:
            self.alerts_table.setVisible(False)
            self.no_alert_label.setVisible(True)
            self.no_alert_label.setText("✓  Aucune alerte de stock active")
            self.no_alert_label.setStyleSheet("color: #16A34A; font-size: 14px; font-weight: 700;")
            self.alerts_count_label.setText("0 alerte")
            return

        self.alerts_table.setVisible(True)
        self.no_alert_label.setVisible(False)
        count = len(alerts)
        self.alerts_count_label.setText(f"{count} alerte{'s' if count > 1 else ''} active{'s' if count > 1 else ''}")

        for alert in alerts:
            row = self.alerts_table.rowCount()
            self.alerts_table.insertRow(row)

            piece_name = self.get_piece_name(alert.get("piece_id"))
            q_dem = int(alert.get("quantite_demandee", 0) or 0)
            q_disp = int(alert.get("quantite_disponible", 0) or 0)
            msg = str(alert.get("message", ""))
            date_str = str(alert.get("date_creation", "")).replace("T", " ")[:19]

            self.alerts_table.setItem(row, 0, QTableWidgetItem(piece_name))
            self.alerts_table.setItem(row, 1, QTableWidgetItem(str(q_dem)))
            self.alerts_table.setItem(row, 2, QTableWidgetItem(str(q_disp)))
            self.alerts_table.setItem(row, 3, QTableWidgetItem(msg))
            self.alerts_table.setItem(row, 4, QTableWidgetItem(date_str))

    def get_piece_name(self, piece_id):
        for stock in self.stocks:
            if stock.get("id") == piece_id:
                return str(stock.get("nom_piece", f"Pièce #{piece_id}"))
        return f"Pièce #{piece_id}"
    