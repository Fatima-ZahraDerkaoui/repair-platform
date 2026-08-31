import requests

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QFrame,
    QAbstractItemView,
    QStackedWidget,
)

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from views.pages.dossiers_utils import (
    API_URL,
    format_date,
)
from views.pages.dossiers_detail import DossierDetailMixin


# ============================================================
# DESIGN GLOBAL SYSTEM
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

QLineEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    color: #0F172A;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus {
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
    padding: 10px 12px;
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
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    text-transform: uppercase;
}

/* BOUTONS ACTIONS TABLEAU PRINCIPAL */
QPushButton#editIconButton {
    background-color: #EFF6FF;
    color: #2563EB;
    border: 1px solid #BFDBFE;
    border-radius: 6px;
    font-weight: bold;
    font-size: 12px;
    padding: 0px;
}

QPushButton#editIconButton:hover {
    background-color: #DBEAFE;
}

QPushButton#deleteIconButton {
    background-color: #FEF2F2;
    color: #DC2626;
    border: 1px solid #FECACA;
    border-radius: 6px;
    font-weight: bold;
    font-size: 12px;
    padding: 0px;
}

QPushButton#deleteIconButton:hover {
    background-color: #FEE2E2;
}
"""


# ============================================================
# COMPOSANT CARTE DE STATISTIQUE
# ============================================================

class StatCard(QFrame):
    def __init__(self, title, value="0", subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 600; text-transform: uppercase;")
        layout.addWidget(title_label)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #0F172A; font-size: 26px; font-weight: 800;")
        layout.addWidget(self.value_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(subtitle_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


# ============================================================
# VUE DOSSIERS
# ============================================================

class DossiersPage(DossierDetailMixin, QWidget):
    status_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dossiers = []
        self.filtered_dossiers = []
        self.stocks = []
        self.pieces_utilisees = []
        self.current_dossier = None
        self.edit_mode = False

        self.setup_ui()
        self.load_dossiers()

    def setup_ui(self):
        self.setStyleSheet(PAGE_STYLE)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # 1. Page Liste
        self.list_page = QWidget()
        self.setup_list_page()
        self.stack.addWidget(self.list_page)

        # 2. Page Détail
        self.detail_page = QWidget()
        self.setup_detail_page()
        self.stack.addWidget(self.detail_page)

        self.stack.setCurrentWidget(self.list_page)

    def setup_list_page(self):
        layout = QVBoxLayout(self.list_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # En-tête (Bouton actualiser supprimé)
        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("Dossiers de réparation")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #0F172A;")
        title_layout.addWidget(title)

        subtitle = QLabel("Gestion, diagnostic, attribution des pièces et suivi des réparations.")
        subtitle.setStyleSheet("color: #64748B; font-size: 13px;")
        title_layout.addWidget(subtitle)

        header.addLayout(title_layout)
        header.addStretch()
        layout.addLayout(header)

        # Cartes Statistiques
        stats = QHBoxLayout()
        stats.setSpacing(12)

        self.total_card = StatCard("Total", "0", "Tous les dossiers")
        self.waiting_card = StatCard("En attente", "0", "À traiter")
        self.diagnostic_card = StatCard("Diagnostic", "0", "Analyse en cours")
        self.repair_card = StatCard("Réparation", "0", "Intervention en cours")
        self.finished_card = StatCard("Terminés", "0", "Prêts pour livraison")
        self.urgent_card = StatCard("Urgents", "0", "Priorité élevée")

        for card in [self.total_card, self.waiting_card, self.diagnostic_card, self.repair_card, self.finished_card, self.urgent_card]:
            stats.addWidget(card)

        layout.addLayout(stats)

        # Barre de filtres
        filters = QFrame()
        filters.setObjectName("card")
        filters_layout = QHBoxLayout(filters)
        filters_layout.setContentsMargins(14, 12, 14, 12)
        filters_layout.setSpacing(12)

        filters_layout.addWidget(QLabel("Recherche :"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Numéro, client, téléphone, marque, série...")
        self.search_input.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.search_input, 1)

        filters_layout.addWidget(QLabel("Statut :"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "En attente", "En diagnostic", "En réparation", "Terminé"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.status_filter)

        filters_layout.addWidget(QLabel("Priorité :"))
        self.urgent_filter = QComboBox()
        self.urgent_filter.addItems(["Tous", "Urgents", "Non urgents"])
        self.urgent_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.urgent_filter)

        reset_button = QPushButton("Réinitialiser")
        reset_button.setCursor(Qt.PointingHandCursor)
        reset_button.clicked.connect(self.reset_filters)
        filters_layout.addWidget(reset_button)

        layout.addWidget(filters)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Dossier", "Client", "Téléphone", "Matériel", 
            "Marque / Modèle", "N° Série", "Statut", "Réception", "Priorité", "Actions"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.on_table_double_click)

        header_tbl = self.table.horizontalHeader()
        header_tbl.setSectionResizeMode(QHeaderView.Stretch)
        for col in [0, 2, 5, 6, 7, 8]:
            header_tbl.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header_tbl.setSectionResizeMode(9, QHeaderView.Fixed)
        self.table.setColumnWidth(9, 85)

        layout.addWidget(self.table, 1)

        # Pied de page
        footer = QHBoxLayout()
        self.result_label = QLabel("0 dossier(s)")
        self.result_label.setStyleSheet("color: #64748B; font-weight: 600;")
        footer.addWidget(self.result_label)
        footer.addStretch()
        
        help_lbl = QLabel("Astuce: Double-cliquez sur une ligne pour afficher les détails du dossier.")
        help_lbl.setStyleSheet("color: #94A3B8; font-style: italic;")
        footer.addWidget(help_lbl)

        layout.addLayout(footer)

    def create_info_label(self):
        label = QLabel("-")
        label.setStyleSheet("color: #0F172A; font-weight: 600;")
        label.setWordWrap(True)
        return label

    def load_all(self):
        self.load_dossiers()

    def load_dossiers(self):
        try:
            response = requests.get(f"{API_URL}/reparations/", timeout=10)
            response.raise_for_status()
            data = response.json()
            self.dossiers = data if isinstance(data, list) else []
            self.update_statistics()
            self.apply_filters()
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur API", f"Impossible de charger les dossiers :\n\n{error}")

    def load_stock(self):
        try:
            response = requests.get(f"{API_URL}/stock/", timeout=10)
            response.raise_for_status()
            data = response.json()
            self.stocks = data if isinstance(data, list) else []
        except requests.RequestException as error:
            print("[DOSSIERS] Erreur chargement stock :", error)
            self.stocks = []

    def update_statistics(self):
        total = len(self.dossiers)
        waiting = sum(1 for d in self.dossiers if d.get("statut") == "En attente")
        diagnostic = sum(1 for d in self.dossiers if d.get("statut") == "En diagnostic")
        repairing = sum(1 for d in self.dossiers if d.get("statut") == "En réparation")
        finished = sum(1 for d in self.dossiers if d.get("statut") == "Terminé")
        urgent = sum(1 for d in self.dossiers if bool(d.get("urgent", False)))

        self.total_card.set_value(total)
        self.waiting_card.set_value(waiting)
        self.diagnostic_card.set_value(diagnostic)
        self.repair_card.set_value(repairing)
        self.finished_card.set_value(finished)
        self.urgent_card.set_value(urgent)

    def apply_filters(self):
        search = self.search_input.text().strip().lower()
        selected_status = self.status_filter.currentText()
        selected_priority = self.urgent_filter.currentText()
        filtered = []

        for dossier in self.dossiers:
            client = dossier.get("client")
            if isinstance(client, dict):
                client_nom = str(client.get("nom", ""))
                client_tel = str(client.get("telephone", ""))
            else:
                client_nom = str(dossier.get("client_nom", ""))
                client_tel = str(dossier.get("client_telephone", ""))

            searchable = " ".join([
                str(dossier.get("numero_dossier", "")),
                client_nom, client_tel,
                str(dossier.get("type_materiel", "")),
                str(dossier.get("marque", "")),
                str(dossier.get("modele", "")),
                str(dossier.get("numero_serie", ""))
            ]).lower()

            if search and search not in searchable:
                continue

            dossier_status = str(dossier.get("statut", ""))
            if selected_status != "Tous" and dossier_status != selected_status:
                continue

            is_urgent = bool(dossier.get("urgent", False))
            if selected_priority == "Urgents" and not is_urgent:
                continue
            if selected_priority == "Non urgents" and is_urgent:
                continue

            filtered.append(dossier)

        self.filtered_dossiers = filtered
        self.display_dossiers(filtered)

    def reset_filters(self):
        self.search_input.clear()
        self.status_filter.setCurrentIndex(0)
        self.urgent_filter.setCurrentIndex(0)

    def display_dossiers(self, dossiers):
        self.table.setRowCount(len(dossiers))

        for row, dossier in enumerate(dossiers):
            client = dossier.get("client")
            if isinstance(client, dict):
                client_nom = client.get("nom") or "-"
                client_tel = client.get("telephone") or "-"
            else:
                client_nom = dossier.get("client_nom") or "-"
                client_tel = dossier.get("client_telephone") or "-"

            numero = dossier.get("numero_dossier") or f"#{dossier.get('id')}"
            marque = dossier.get("marque") or ""
            modele = dossier.get("modele") or ""
            marque_modele = f"{marque} / {modele}".strip(" /") if (marque or modele) else "-"

            values = [
                numero, client_nom, client_tel,
                dossier.get("type_materiel") or "-",
                marque_modele,
                dossier.get("numero_serie") or "-",
                dossier.get("statut") or "-",
                format_date(dossier.get("date_reception")),
                "⚠️ URGENT" if dossier.get("urgent", False) else "Normal"
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignCenter if col in [6, 8] else Qt.AlignLeft))
                self.table.setItem(row, col, item)

            self.apply_status_color(self.table.item(row, 6), dossier.get("statut"))

            p_item = self.table.item(row, 8)
            if dossier.get("urgent", False):
                p_item.setForeground(QColor("#DC2626"))
                p_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            else:
                p_item.setForeground(QColor("#64748B"))

            # Boutons d'Action (taille fixe compacte et visible)
            # Boutons d'Action (Taille ajustée + Style forcé)
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(4)
            action_layout.setAlignment(Qt.AlignCenter)

            edit_btn = QPushButton("✎")
            edit_btn.setToolTip("Modifier le dossier")
            edit_btn.setFixedSize(30, 10)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #EFF6FF;
                    color: #2563EB;
                    border: 1px solid #BFDBFE;
                    border-radius: 2px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #DBEAFE;
                    color: #1D4ED8;
                }
            """)
            edit_btn.clicked.connect(lambda checked=False, d=dossier: self.open_edit_dialog(d))

            delete_btn = QPushButton("✕")
            delete_btn.setToolTip("Supprimer le dossier")
            delete_btn.setFixedSize(30, 10)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FEF2F2;
                    color: #DC2626;
                    border: 1px solid #FECACA;
                    border-radius: 2px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #FEE2E2;
                    color: #B91C1C;
                }
            """)
            delete_btn.clicked.connect(lambda checked=False, d=dossier: self.delete_dossier(d))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            self.table.setCellWidget(row, 9, action_widget)

            self.table.item(row, 0).setData(Qt.UserRole, dossier.get("id"))

        self.result_label.setText(f"{len(dossiers)} dossier(s) affiché(s)")

    def apply_status_color(self, item, statut):
        if not item:
            return
        colors = {
            "En attente": "#B45309",
            "En diagnostic": "#0284C7",
            "En réparation": "#6D28D9",
            "Terminé": "#15803D"
        }
        item.setForeground(QColor(colors.get(statut, "#334155")))
        item.setFont(QFont("Segoe UI", 9, QFont.Bold))

    def on_table_double_click(self, index):
        row = index.row()
        if 0 <= row < len(self.filtered_dossiers):
            self.open_dossier(self.filtered_dossiers[row])

    def open_dossier(self, dossier):
        dossier_id = dossier.get("id")
        if not dossier_id:
            QMessageBox.warning(self, "Erreur", "Identifiant du dossier introuvable.")
            return

        try:
            response = requests.get(f"{API_URL}/reparations/{dossier_id}", timeout=15)
            response.raise_for_status()
            full_dossier = response.json()
            self.current_dossier = full_dossier if isinstance(full_dossier, dict) else dossier
        except requests.RequestException as error:
            QMessageBox.warning(self, "Avertissement", f"Données partielles chargées :\n{error}")
            self.current_dossier = dossier

        self.load_detail_data()
        self.stack.setCurrentWidget(self.detail_page)

    def open_edit_dialog(self, dossier):
        self.open_dossier(dossier)
        self.enter_edit_mode()

    def delete_dossier(self, dossier):
        dossier_id = dossier.get("id")
        numero = dossier.get("numero_dossier") or f"#{dossier_id}"

        if not dossier_id:
            QMessageBox.warning(self, "Erreur", "Identifiant du dossier introuvable.")
            return

        reply = QMessageBox.question(
            self,
            "Suppression du dossier",
            f"Voulez-vous vraiment supprimer définitivement le dossier {numero} ?\n\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            response = requests.delete(f"{API_URL}/reparations/{dossier_id}", timeout=15)
            if not response.ok:
                detail = response.json().get("detail", response.text) if response.headers.get("content-type") == "application/json" else response.text
                QMessageBox.warning(self, "Échec de la suppression", f"Erreur : {detail}")
                return

            if self.current_dossier and self.current_dossier.get("id") == dossier_id:
                self.current_dossier = None
                self.stack.setCurrentWidget(self.list_page)

            self.load_dossiers()
            self.status_changed.emit()
            QMessageBox.information(self, "Succès", f"Dossier {numero} supprimé.")

        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur API", f"Impossible de contacter le serveur :\n{error}")

    def predict_cost(self, materiel, probleme):
        try:
            response = requests.post(
                f"{API_URL}/prediction/cout",
                json={"materiel": materiel, "probleme": probleme},
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            print("[COUT ML] Erreur lors de l'appel au service de prédiction :", error)
            return None
        