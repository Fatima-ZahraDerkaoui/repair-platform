from tkinter import dialog

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
    QComboBox,
    QMessageBox,
    QFrame,
    QAbstractItemView,
    QScrollArea,
    QGroupBox,
    QStackedWidget,
    QSizePolicy,
    QDialog,
    QDialogButtonBox,
    QTextEdit,
)

from PySide6.QtCore import (
    Qt,
    Signal,
)

from PySide6.QtGui import (
    QColor,
    QFont,
)

import requests
import requests

from views.pages.dossiers_utils import (
    safe_int,
    safe_float,
    format_money,
    format_date,
)

from views.pages.dossiers_utils import (
    API_URL,
    DEFAULT_UTILISATEUR_ID,
    safe_int,
    safe_float,
    format_money,
    format_date,
)

from views.pages.dossiers_detail import DossierDetailMixin

# ============================================================
# STYLE
# ============================================================

PAGE_STYLE = """

QWidget {
    font-family: "Segoe UI";
    font-size: 13px;
    color: #111827;
}

QFrame#card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
}

QFrame#headerCard {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    margin-top: 12px;
    padding: 15px;
    background: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background: white;
}

QLineEdit,
QComboBox,
QSpinBox,
QTextEdit {
    border: 1px solid #D1D5DB;
    border-radius: 7px;
    padding: 8px;
    background: white;
    color: #111827;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QTextEdit:focus {
    border: 1px solid #2563EB;
}

QComboBox QAbstractItemView {
    background: white;
    color: #111827;
    selection-background-color: #2563EB;
    selection-color: white;
}

QPushButton {
    border: 1px solid #D1D5DB;
    border-radius: 7px;
    padding: 8px 14px;
    background: white;
    color: #111827;
}

QPushButton:hover {
    background: #F3F4F6;
}

QPushButton#primaryButton {
    background: #2563EB;
    color: white;
    border: none;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background: #1D4ED8;
}

QPushButton#successButton {
    background: #16A34A;
    color: white;
    border: none;
    font-weight: bold;
}

QPushButton#successButton:hover {
    background: #15803D;
}

QPushButton#dangerButton {
    background: #DC2626;
    color: white;
    border: none;
    font-weight: bold;
}

QPushButton#dangerButton:hover {
    background: #B91C1C;
}

QPushButton#backButton {
    border: none;
    background: transparent;
    color: #2563EB;
    font-size: 15px;
    font-weight: bold;
    padding: 5px;
}

QPushButton#backButton:hover {
    background: #EFF6FF;
}

QTableWidget {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    gridline-color: #E5E7EB;
    selection-background-color: #DBEAFE;
    selection-color: #111827;
}

QTableWidget::item {
    padding: 8px;
}

QHeaderView::section {
    background: #F8FAFC;
    color: #374151;
    font-weight: bold;
    padding: 9px;
    border: none;
    border-bottom: 1px solid #E5E7EB;
}

QScrollArea {
    border: none;
    background: transparent;
}

/* =========================================================
   BOUTONS ACTIONS TABLE
   ========================================================= */
QPushButton#editIconButton {
    background: #EFF6FF;
    color: #2563EB;
    border: 1px solid #BFDBFE;
    border-radius: 4px;
    font-size: 9px;
    font-weight: bold;
    padding: 0px;
    margin: 0px;
}

QPushButton#deleteIconButton {
    background: #FEF2F2;
    color: #DC2626;
    border: 1px solid #FECACA;
    border-radius: 4px;
    font-size: 9px;
    font-weight: bold;
    padding: 0px;
    margin: 0px;
}

"""


# ============================================================
# CARTE STATISTIQUE
# ============================================================

class StatCard(QFrame):

    def __init__(
        self,
        title,
        value="0",
        subtitle="",
        parent=None
    ):

        super().__init__(parent)

        self.setObjectName("card")

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            18,
            15,
            18,
            15
        )

        layout.setSpacing(4)

        title_label = QLabel(title)

        title_label.setStyleSheet("""
            color: #6B7280;
            font-size: 13px;
        """)

        layout.addWidget(title_label)

        self.value_label = QLabel(value)

        self.value_label.setStyleSheet("""
            color: #111827;
            font-size: 27px;
            font-weight: bold;
        """)

        layout.addWidget(self.value_label)

        subtitle_label = QLabel(subtitle)

        subtitle_label.setStyleSheet("""
            color: #9CA3AF;
            font-size: 11px;
        """)

        layout.addWidget(subtitle_label)

    def set_value(self, value):

        self.value_label.setText(
            str(value)
        )


# ============================================================
# DOSSIERS PAGE
# ============================================================

class DossiersPage(
    DossierDetailMixin,
    QWidget
):

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

    # ========================================================
    # INTERFACE
    # ========================================================

    def setup_ui(self):

        self.setStyleSheet(PAGE_STYLE)

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        main_layout.setSpacing(15)

        self.stack = QStackedWidget()

        main_layout.addWidget(
            self.stack
        )

        # ----------------------------------------------------
        # PAGE LISTE
        # ----------------------------------------------------

        self.list_page = QWidget()

        self.setup_list_page()

        self.stack.addWidget(
            self.list_page
        )

        # ----------------------------------------------------
        # PAGE DETAIL
        # ----------------------------------------------------

        self.detail_page = QWidget()

        self.setup_detail_page()

        self.stack.addWidget(
            self.detail_page
        )

        self.stack.setCurrentWidget(
            self.list_page
        )

    # ========================================================
    # PAGE LISTE
    # ========================================================

    def setup_list_page(self):

        layout = QVBoxLayout(
            self.list_page
        )

        layout.setSpacing(15)

        # ====================================================
        # HEADER
        # ====================================================

        header = QHBoxLayout()

        title_layout = QVBoxLayout()

        title = QLabel(
            "Dossiers de réparation"
        )

        title.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #111827;
        """)

        title_layout.addWidget(title)

        subtitle = QLabel(
            "Suivi des réparations, des statuts et des pièces utilisées."
        )

        subtitle.setStyleSheet("""
            color: #6B7280;
            font-size: 13px;
        """)

        title_layout.addWidget(subtitle)

        header.addLayout(
            title_layout
        )

        header.addStretch()

        self.refresh_button = QPushButton(
            "↻  Actualiser"
        )

        self.refresh_button.clicked.connect(
            self.load_all
        )

        header.addWidget(
            self.refresh_button
        )

        layout.addLayout(header)

        # ====================================================
        # STATISTIQUES
        # ====================================================

        stats = QHBoxLayout()

        self.total_card = StatCard(
            "Total dossiers",
            "0",
            "Tous les dossiers"
        )

        self.waiting_card = StatCard(
            "En attente",
            "0",
            "À traiter"
        )

        self.diagnostic_card = StatCard(
            "Diagnostic",
            "0",
            "En cours d'analyse"
        )

        self.repair_card = StatCard(
            "En réparation",
            "0",
            "Interventions en cours"
        )

        self.finished_card = StatCard(
            "Terminés",
            "0",
            "Réparations terminées"
        )

        self.urgent_card = StatCard(
            "Urgents",
            "0",
            "Priorité élevée"
        )

        stats.addWidget(
            self.total_card
        )

        stats.addWidget(
            self.waiting_card
        )

        stats.addWidget(
            self.diagnostic_card
        )

        stats.addWidget(
            self.repair_card
        )

        stats.addWidget(
            self.finished_card
        )

        stats.addWidget(
            self.urgent_card
        )

        layout.addLayout(stats)

        # ====================================================
        # FILTRES
        # ====================================================

        filters = QFrame()

        filters.setObjectName(
            "card"
        )

        filters_layout = QHBoxLayout(
            filters
        )

        filters_layout.setContentsMargins(
            12,
            10,
            12,
            10
        )

        # Recherche

        filters_layout.addWidget(
            QLabel("Recherche :")
        )

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "N° dossier, client, téléphone, machine, marque, série..."
        )

        self.search_input.textChanged.connect(
            self.apply_filters
        )

        filters_layout.addWidget(
            self.search_input,
            1
        )

        # Statut

        filters_layout.addWidget(
            QLabel("Statut :")
        )

        self.status_filter = QComboBox()

        self.status_filter.addItems([
            "Tous",
            "En attente",
            "En diagnostic",
            "En réparation",
            "Terminé"
        ])

        self.status_filter.currentTextChanged.connect(
            self.apply_filters
        )

        filters_layout.addWidget(
            self.status_filter
        )

        # Urgent

        filters_layout.addWidget(
            QLabel("Priorité :")
        )

        self.urgent_filter = QComboBox()

        self.urgent_filter.addItems([
            "Tous",
            "Urgents",
            "Non urgents"
        ])

        self.urgent_filter.currentTextChanged.connect(
            self.apply_filters
        )

        filters_layout.addWidget(
            self.urgent_filter
        )

        # Reset

        reset_button = QPushButton(
            "Réinitialiser"
        )

        reset_button.clicked.connect(
            self.reset_filters
        )

        filters_layout.addWidget(
            reset_button
        )

        layout.addWidget(
            filters
        )

        # ====================================================
        # TITRE TABLE
        # ====================================================

        table_title = QLabel(
            "Liste des dossiers"
        )

        table_title.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
            color: #111827;
        """)

        layout.addWidget(
            table_title
        )

        # ====================================================
        # TABLE
        # ====================================================

        self.table = QTableWidget()

        self.table.setColumnCount(10)

        self.table.setHorizontalHeaderLabels([
            "Dossier",
            "Client",
            "Téléphone",
            "Matériel",
            "Marque / Modèle",
            "N° série",
            "Statut",
            "Réception",
            "Priorité",
            "Action"
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

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.doubleClicked.connect(
            self.on_table_double_click
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            6,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            7,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            8,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            9,
            QHeaderView.Fixed
        )

        self.table.setColumnWidth(9, 75)

        layout.addWidget(
            self.table,
            1
        )

        # ====================================================
        # FOOTER
        # ====================================================

        footer = QHBoxLayout()

        self.result_label = QLabel(
            "0 dossier"
        )

        self.result_label.setStyleSheet("""
            color: #6B7280;
        """)

        footer.addWidget(
            self.result_label
        )

        footer.addStretch()

        help_label = QLabel(
            "Double-cliquez sur un dossier ou utilisez « Ouvrir »."
        )

        help_label.setStyleSheet("""
            color: #9CA3AF;
        """)

        footer.addWidget(
            help_label
        )

        layout.addLayout(
            footer
        )

   
    # ========================================================
    # LABEL INFO
    # ========================================================

    def create_info_label(self):

        label = QLabel("-")

        label.setStyleSheet("""
            color: #111827;
            font-weight: 600;
        """)

        label.setWordWrap(
            True
        )

        return label


    # ========================================================
    # CHARGEMENT
    # ========================================================

    def load_all(self):

        self.load_dossiers()

    # ========================================================
    # DOSSIERS
    # ========================================================
    def load_dossiers(self):

        try:

            response = requests.get(
                f"{API_URL}/reparations/",
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            self.dossiers = (
                data
                if isinstance(data, list)
                else []
            )

            # IMPORTANT :
            # Ne pas charger le stock ici.
            # Le stock sera chargé uniquement
            # lorsqu'on entre en mode modification.

            self.update_statistics()

            self.apply_filters()

        except requests.RequestException as error:

            QMessageBox.critical(
                self,
                "Erreur",
                "Impossible de récupérer les dossiers.\n\n"
                f"{error}"
            )
  
    def load_stock(self):

        try:

            response = requests.get(
                f"{API_URL}/stock/",
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            self.stocks = (
                data
                if isinstance(data, list)
                else []
            )

        except requests.RequestException as error:

            print(
                "[DOSSIERS] Erreur stock :",
                error
            )

            self.stocks = []

    # ========================================================
    # STATISTIQUES
    # ========================================================

    def update_statistics(self):

        total = len(
            self.dossiers
        )

        waiting = 0
        diagnostic = 0
        repairing = 0
        finished = 0
        urgent = 0

        for dossier in self.dossiers:

            statut = str(
                dossier.get(
                    "statut",
                    ""
                )
            )

            if statut == "En attente":
                waiting += 1

            elif statut == "En diagnostic":
                diagnostic += 1

            elif statut == "En réparation":
                repairing += 1

            elif statut == "Terminé":
                finished += 1

            if bool(
                dossier.get(
                    "urgent",
                    False
                )
            ):
                urgent += 1

        self.total_card.set_value(
            total
        )

        self.waiting_card.set_value(
            waiting
        )

        self.diagnostic_card.set_value(
            diagnostic
        )

        self.repair_card.set_value(
            repairing
        )

        self.finished_card.set_value(
            finished
        )

        self.urgent_card.set_value(
            urgent
        )

    # ========================================================
    # FILTRES
    # ========================================================

    def apply_filters(self):

        search = (
            self.search_input
            .text()
            .strip()
            .lower()
        )

        selected_status = (
            self.status_filter
            .currentText()
        )

        selected_priority = (
            self.urgent_filter
            .currentText()
        )

        filtered = []

        for dossier in self.dossiers:

            client = dossier.get(
                "client"
            )

            if isinstance(
                client,
                dict
            ):

                client_nom = str(
                    client.get(
                        "nom",
                        ""
                    )
                )

                client_tel = str(
                    client.get(
                        "telephone",
                        ""
                    )
                )

            else:

                client_nom = str(
                    dossier.get(
                        "client_nom",
                        ""
                    )
                )

                client_tel = str(
                    dossier.get(
                        "client_telephone",
                        ""
                    )
                )

            searchable = " ".join([
                str(
                    dossier.get(
                        "numero_dossier",
                        ""
                    )
                ),
                client_nom,
                client_tel,
                str(
                    dossier.get(
                        "type_materiel",
                        ""
                    )
                ),
                str(
                    dossier.get(
                        "marque",
                        ""
                    )
                ),
                str(
                    dossier.get(
                        "modele",
                        ""
                    )
                ),
                str(
                    dossier.get(
                        "numero_serie",
                        ""
                    )
                )
            ]).lower()

            if (
                search
                and search not in searchable
            ):
                continue

            dossier_status = str(
                dossier.get(
                    "statut",
                    ""
                )
            )

            if (
                selected_status != "Tous"
                and dossier_status != selected_status
            ):
                continue

            is_urgent = bool(
                dossier.get(
                    "urgent",
                    False
                )
            )

            if (
                selected_priority == "Urgents"
                and not is_urgent
            ):
                continue

            if (
                selected_priority == "Non urgents"
                and is_urgent
            ):
                continue

            filtered.append(
                dossier
            )

        self.filtered_dossiers = filtered

        self.display_dossiers(
            filtered
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset_filters(self):

        self.search_input.clear()

        self.status_filter.setCurrentIndex(
            0
        )

        self.urgent_filter.setCurrentIndex(
            0
        )

    # ========================================================
    # AFFICHAGE TABLE
    # ========================================================

    def display_dossiers(
        self,
        dossiers
    ):

        self.table.setRowCount(len(dossiers))

        for row, dossier in enumerate(dossiers):

            client = dossier.get(
                "client"
            )

            if isinstance(
                client,
                dict
            ):

                client_nom = (
                    client.get("nom")
                    or "-"
                )

                client_tel = (
                    client.get("telephone")
                    or "-"
                )

            else:

                client_nom = (
                    dossier.get(
                        "client_nom"
                    )
                    or "-"
                )

                client_tel = (
                    dossier.get(
                        "client_telephone"
                    )
                    or "-"
                )

            numero = (
                dossier.get(
                    "numero_dossier"
                )
                or f"#{dossier.get('id')}"
            )

            marque = (
                dossier.get("marque")
                or ""
            )

            modele = (
                dossier.get("modele")
                or ""
            )

            marque_modele = (
                f"{marque} / {modele}"
                if marque or modele
                else "-"
            )

            values = [
                numero,
                client_nom,
                client_tel,
                dossier.get(
                    "type_materiel"
                ) or "-",
                marque_modele,
                dossier.get(
                    "numero_serie"
                ) or "-",
                dossier.get(
                    "statut"
                ) or "-",
                format_date(
                    dossier.get(
                        "date_reception"
                    )
                ),
                (
                    "URGENT"
                    if dossier.get(
                        "urgent",
                        False
                    )
                    else "Normal"
                )
            ]

            for col, value in enumerate(
                values
            ):

                item = QTableWidgetItem(
                    str(value)
                )

                item.setTextAlignment(
                    Qt.AlignVCenter
                    | (
                        Qt.AlignCenter
                        if col in [6, 8]
                        else Qt.AlignLeft
                    )
                )

                self.table.setItem(
                    row,
                    col,
                    item
                )

            # ------------------------------------------------
            # STATUT
            # ------------------------------------------------

            status_item = self.table.item(
                row,
                6
            )

            self.apply_status_color(
                status_item,
                dossier.get(
                    "statut"
                )
            )

            # ------------------------------------------------
            # PRIORITÉ
            # ------------------------------------------------

            priority_item = self.table.item(
                row,
                8
            )

            if dossier.get(
                "urgent",
                False
            ):

                priority_item.setForeground(
                    QColor("#DC2626")
                )

                priority_item.setFont(
                    QFont(
                        "Segoe UI",
                        9,
                        QFont.Bold
                    )
                )

            else:

                priority_item.setForeground(
                    QColor("#6B7280")
                )

            # ------------------------------------------------
            # ACTIONS
            # ------------------------------------------------
            action_widget = QWidget()

            action_layout = QHBoxLayout(action_widget)

            action_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            action_layout.setSpacing(5)

            action_layout.setAlignment(
                Qt.AlignCenter
            )

            # ------------------------------------------------
            # MODIFIER
            # ------------------------------------------------

            edit_button = QPushButton("✎")
            edit_button.setObjectName("editIconButton")
            edit_button.setToolTip("Modifier le dossier")
            edit_button.setFixedSize(30, 15)
            edit_button.setCursor(Qt.PointingHandCursor)

            edit_button.clicked.connect(
                lambda checked=False, d=dossier:
                self.open_dossier(d)
            )

            action_layout.addWidget(edit_button)

            # ------------------------------------------------
            # SUPPRIMER
            # ------------------------------------------------

            delete_button = QPushButton("×")
            delete_button.setObjectName("deleteIconButton")
            delete_button.setToolTip("Supprimer le dossier")
            delete_button.setFixedSize(30, 15)
            delete_button.setCursor(Qt.PointingHandCursor)

            delete_button.clicked.connect(
                lambda checked=False, d=dossier:
                self.delete_dossier(d)
            )

            action_layout.addWidget(delete_button)

            action_layout.addStretch()

            self.table.setCellWidget(
                row,
                9,
                action_widget
            )
            

            # ID caché

            self.table.item(
                row,
                0
            ).setData(
                Qt.UserRole,
                dossier.get(
                    "id"
                )
            )

        self.result_label.setText(
            f"{len(dossiers)} dossier(s) affiché(s)"
        )

    # ========================================================
    # COULEUR STATUT
    # ========================================================

    def apply_status_color(
        self,
        item,
        statut
    ):

        if not item:
            return

        colors = {
            "En attente": "#92400E",
            "En diagnostic": "#1D4ED8",
            "En réparation": "#4338CA",
            "Terminé": "#15803D"
        }

        item.setForeground(
            QColor(
                colors.get(
                    statut,
                    "#374151"
                )
            )
        )

        item.setFont(
            QFont(
                "Segoe UI",
                9,
                QFont.Bold
            )
        )

    # ========================================================
    # DOUBLE CLIC
    # ========================================================

    def on_table_double_click(
        self,
        index
    ):

        row = index.row()

        if row < 0:
            return

        if row >= len(
            self.filtered_dossiers
        ):
            return

        self.open_dossier(
            self.filtered_dossiers[row]
        )

    # ========================================================
    # OUVRIR DOSSIER
    # ========================================================

    def open_dossier(
        self,
        dossier
    ):

        dossier_id = dossier.get(
            "id"
        )

        if not dossier_id:

            QMessageBox.warning(
                self,
                "Erreur",
                "Identifiant du dossier introuvable."
            )

            return

        try:

            response = requests.get(
                f"{API_URL}/reparations/{dossier_id}",
                timeout=15
            )

            response.raise_for_status()

            full_dossier = response.json()

            self.current_dossier = (
                full_dossier
                if isinstance(
                    full_dossier,
                    dict
                )
                else dossier
            )

        except requests.RequestException as error:

            QMessageBox.warning(
                self,
                "Erreur",
                "Impossible de récupérer le dossier complet.\n\n"
                f"{error}"
            )

            self.current_dossier = dossier

        self.load_detail_data()

        self.stack.setCurrentWidget(
            self.detail_page
        )

    # ========================================================
    # MODIFIER DOSSIER
    # ========================================================

    def open_edit_dialog(self, dossier):
        """Redirige vers la page de détail et active le mode édition."""
        dossier_id = dossier.get("id")

        if not dossier_id:
            QMessageBox.warning(
                self,
                "Erreur",
                "Identifiant du dossier introuvable."
            )
            return

        # 1. Récupérer la version complète du dossier depuis l'API
        try:
            response = requests.get(
                f"{API_URL}/reparations/{dossier_id}",
                timeout=15
            )
            response.raise_for_status()
            full_dossier = response.json()

            self.current_dossier = (
                full_dossier if isinstance(full_dossier, dict) else dossier
            )
        except requests.RequestException as error:
            QMessageBox.warning(
                self,
                "Erreur",
                "Impossible de récupérer les données complètes du dossier.\n\n"
                f"{error}"
            )
            self.current_dossier = dossier

        # 2. Charger les données dans l'interface de détail
        self.load_detail_data()

        # 3. Basculer la vue vers la page de détail
        self.stack.setCurrentWidget(self.detail_page)

        # 4. Activer directement le mode édition sur la page
        self.enter_edit_mode()

    # ========================================================
    # SUPPRIMER DOSSIER
    # ========================================================

    def delete_dossier(self, dossier):

        dossier_id = dossier.get(
            "id"
        )

        numero = (
            dossier.get(
                "numero_dossier"
            )
            or f"#{dossier_id}"
        )

        if not dossier_id:

            QMessageBox.warning(
                self,
                "Erreur",
                "Identifiant du dossier introuvable."
            )

            return

        reply = QMessageBox.question(
            self,
            "Confirmation de suppression",
            "Voulez-vous vraiment supprimer ce dossier ?\n\n"
            f"Dossier : {numero}\n\n"
            "Cette opération est irréversible.",
            QMessageBox.Yes |
            QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:

            response = requests.delete(
                f"{API_URL}/reparations/{dossier_id}",
                timeout=15
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
                    "Suppression impossible",
                    "Le dossier n'a pas pu être supprimé.\n\n"
                    f"{detail}"
                )

                return

            # Si le dossier supprimé était ouvert
            if (
                self.current_dossier
                and self.current_dossier.get("id")
                == dossier_id
            ):

                self.current_dossier = None

                self.stack.setCurrentWidget(
                    self.list_page
                )

            self.load_dossiers()

            self.status_changed.emit()

            QMessageBox.information(
                self,
                "Dossier supprimé",
                f"Le dossier {numero} a été supprimé."
            )

        except requests.RequestException as error:

            QMessageBox.critical(
                self,
                "Erreur API",
                "Impossible de communiquer avec le serveur.\n\n"
                f"{error}"
            )
        
    def predict_cost(self, materiel, probleme):

        try:

            response = requests.post(
                f"{API_URL}/reparations/cout/predire",
                json={
                    "materiel": materiel,
                    "probleme": probleme
                },
                timeout=15
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:

            print(
                "[COUT ML] Erreur :",
                error
            )

            return None

    