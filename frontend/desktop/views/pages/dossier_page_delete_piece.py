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


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"

# À remplacer plus tard par l'utilisateur connecté.
DEFAULT_UTILISATEUR_ID = 1


# ============================================================
# UTILITAIRES
# ============================================================

def safe_int(value, default=0):

    try:
        return int(value or default)

    except (ValueError, TypeError):

        return default


def safe_float(value, default=0.0):

    try:
        return float(value or default)

    except (ValueError, TypeError):

        return default


def format_money(value):

    try:

        return f"{float(value or 0):,.2f} DH".replace(",", " ")

    except (ValueError, TypeError):

        return "0.00 DH"


def format_date(value):

    if not value:
        return "-"

    return str(value).replace("T", " ")[:19]


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
    border-radius: 5px;
    font-size: 12px;
    font-weight: bold;
    padding: 0px;
}

QPushButton#editIconButton:hover {
    background: #DBEAFE;
    color: #1D4ED8;
}

QPushButton#deleteIconButton {
    background: #FEF2F2;
    color: #DC2626;
    border: 1px solid #FECACA;
    border-radius: 5px;
    font-size: 12px;
    font-weight: bold;
    padding: 0px;
}

QPushButton#deleteIconButton:hover {
    background: #FEE2E2;
    color: #B91C1C;
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

class DossiersPage(QWidget):

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
            QHeaderView.ResizeToContents
        )

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
    # PAGE DETAIL
    # ========================================================
    def setup_detail_page(self):

        layout = QVBoxLayout(self.detail_page)
        layout.setSpacing(12)

        # ========================================================
        # HEADER
        # ========================================================

        header = QHBoxLayout()

        self.back_button = QPushButton(
            "←  Retour aux dossiers"
        )

        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(
            self.back_to_list
        )

        header.addWidget(self.back_button)
        header.addStretch()

        self.detail_refresh_button = QPushButton(
            "↻ Actualiser"
        )

        self.detail_refresh_button.clicked.connect(
            self.refresh_current_dossier
        )

        header.addWidget(
            self.detail_refresh_button
        )

        self.pdf_button = QPushButton("PDF")

        self.pdf_button.clicked.connect(
            self.download_pdf
        )

        header.addWidget(
            self.pdf_button
        )

        layout.addLayout(header)

        # ========================================================
        # SCROLL
        # ========================================================

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()

        content = QVBoxLayout(container)

        content.setContentsMargins(
            5, 5, 5, 20
        )

        content.setSpacing(15)

        # ========================================================
        # IDENTIFICATION
        # ========================================================

        header_card = QFrame()
        header_card.setObjectName("headerCard")

        header_layout = QHBoxLayout(header_card)

        left = QVBoxLayout()

        self.detail_numero = QLabel()

        self.detail_numero.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #111827;
        """)

        left.addWidget(
            self.detail_numero
        )

        self.detail_date = QLabel()

        self.detail_date.setStyleSheet("""
            color: #6B7280;
        """)

        left.addWidget(
            self.detail_date
        )

        header_layout.addLayout(left)
        header_layout.addStretch()

        self.detail_status_label = QLabel()

        self.detail_status_label.setAlignment(
            Qt.AlignCenter
        )

        self.detail_status_label.setMinimumWidth(150)

        header_layout.addWidget(
            self.detail_status_label
        )

        content.addWidget(header_card)

        # ========================================================
        # CLIENT
        # ========================================================

        client_group = QGroupBox("Client")

        client_layout = QGridLayout(client_group)

        # Consultation
        self.client_nom = self.create_info_label()
        self.client_tel = self.create_info_label()
        self.client_email = self.create_info_label()

        # Modification
        self.edit_client_nom = QLineEdit()
        self.edit_client_tel = QLineEdit()
        self.edit_client_email = QLineEdit()

        client_layout.addWidget(
            QLabel("Nom"),
            0, 0
        )

        client_layout.addWidget(
            self.client_nom,
            0, 1
        )

        client_layout.addWidget(
            self.edit_client_nom,
            0, 1
        )

        client_layout.addWidget(
            QLabel("Téléphone"),
            1, 0
        )

        client_layout.addWidget(
            self.client_tel,
            1, 1
        )

        client_layout.addWidget(
            self.edit_client_tel,
            1, 1
        )

        client_layout.addWidget(
            QLabel("Email"),
            2, 0
        )

        client_layout.addWidget(
            self.client_email,
            2, 1
        )

        client_layout.addWidget(
            self.edit_client_email,
            2, 1
        )

        content.addWidget(client_group)

        # ========================================================
        # MATÉRIEL
        # ========================================================

        machine_group = QGroupBox("Matériel")

        machine_layout = QGridLayout(machine_group)

        self.machine_type = self.create_info_label()
        self.machine_marque = self.create_info_label()
        self.machine_modele = self.create_info_label()
        self.machine_serie = self.create_info_label()

        self.edit_machine_type = QLineEdit()
        self.edit_machine_marque = QLineEdit()
        self.edit_machine_modele = QLineEdit()
        self.edit_machine_serie = QLineEdit()

        fields = [
            ("Type", self.machine_type, self.edit_machine_type),
            ("Marque", self.machine_marque, self.edit_machine_marque),
            ("Modèle", self.machine_modele, self.edit_machine_modele),
            ("N° série", self.machine_serie, self.edit_machine_serie),
        ]

        for row, (label, view, edit) in enumerate(fields):

            machine_layout.addWidget(
                QLabel(label),
                row,
                0
            )

            machine_layout.addWidget(
                view,
                row,
                1
            )

            machine_layout.addWidget(
                edit,
                row,
                1
            )

        content.addWidget(machine_group)

        # ========================================================
        # DIAGNOSTIC / INTERVENTION
        # ========================================================

        problem_group = QGroupBox(
            "Diagnostic et intervention"
        )

        problem_layout = QGridLayout(problem_group)

        self.probleme_view = self.create_info_label()
        self.diagnostic_view = self.create_info_label()
        self.intervention_view = self.create_info_label()
        self.pieces_defectueuses_view = self.create_info_label()
        self.remarques_view = self.create_info_label()

        self.probleme_edit = QTextEdit()
        self.diagnostic_edit = QTextEdit()
        self.intervention_edit = QTextEdit()
        self.pieces_defectueuses_edit = QTextEdit()
        self.remarques_edit = QTextEdit()

        edit_fields = [
            (
                "Problème",
                self.probleme_view,
                self.probleme_edit
            ),
            (
                "Diagnostic",
                self.diagnostic_view,
                self.diagnostic_edit
            ),
            (
                "Intervention",
                self.intervention_view,
                self.intervention_edit
            ),
            (
                "Pièces défectueuses",
                self.pieces_defectueuses_view,
                self.pieces_defectueuses_edit
            ),
            (
                "Remarques",
                self.remarques_view,
                self.remarques_edit
            ),
        ]

        for row, (label, view, edit) in enumerate(edit_fields):

            edit.setMinimumHeight(55)

            problem_layout.addWidget(
                QLabel(label),
                row,
                0,
                Qt.AlignTop
            )

            problem_layout.addWidget(
                view,
                row,
                1
            )

            problem_layout.addWidget(
                edit,
                row,
                1
            )

        content.addWidget(problem_group)

        # ========================================================
        # STATUT
        # ========================================================

        status_group = QGroupBox("Statut")

        status_layout = QHBoxLayout(status_group)

        status_layout.addWidget(
            QLabel("Statut :")
        )

        self.status_combo = QComboBox()

        self.status_combo.addItems([
            "En attente",
            "En diagnostic",
            "En réparation",
            "Terminé"
        ])

        status_layout.addWidget(
            self.status_combo
        )

        status_layout.addStretch()

        content.addWidget(status_group)

        # ========================================================
        # PIÈCES UTILISÉES
        # ========================================================

        pieces_group = QGroupBox(
            "Pièces utilisées"
        )

        pieces_layout = QVBoxLayout(
            pieces_group
        )

        self.pieces_edit_controls = QWidget()

        edit_piece_layout = QVBoxLayout(
            self.pieces_edit_controls
        )

        edit_piece_layout.setContentsMargins(
            0, 0, 0, 0
        )

        # Recherche
        search_layout = QHBoxLayout()

        search_layout.addWidget(
            QLabel("Rechercher :")
        )

        self.piece_search = QLineEdit()

        self.piece_search.setPlaceholderText(
            "Nom ou référence..."
        )

        self.piece_search.textChanged.connect(
            self.filter_stock
        )

        search_layout.addWidget(
            self.piece_search,
            1
        )

        edit_piece_layout.addLayout(
            search_layout
        )

        # Sélection
        selection_layout = QHBoxLayout()

        selection_layout.addWidget(
            QLabel("Pièce :")
        )

        self.piece_combo = QComboBox()

        self.piece_combo.currentIndexChanged.connect(
            self.on_piece_selected
        )

        selection_layout.addWidget(
            self.piece_combo,
            1
        )

        selection_layout.addWidget(
            QLabel("Quantité :")
        )

        self.piece_quantity = QSpinBox()

        self.piece_quantity.setRange(
            1,
            999999
        )

        self.piece_quantity.setValue(1)

        selection_layout.addWidget(
            self.piece_quantity
        )

        self.add_piece_button = QPushButton(
            "+ Ajouter"
        )

        self.add_piece_button.setObjectName(
            "successButton"
        )

        self.add_piece_button.clicked.connect(
            self.add_piece_to_dossier
        )

        selection_layout.addWidget(
            self.add_piece_button
        )

        edit_piece_layout.addLayout(
            selection_layout
        )

        self.piece_info_label = QLabel(
            "Sélectionnez une pièce."
        )

        self.piece_info_label.setStyleSheet("""
            color: #6B7280;
            padding: 3px;
        """)

        edit_piece_layout.addWidget(
            self.piece_info_label
        )

        pieces_layout.addWidget(
            self.pieces_edit_controls
        )

        # TABLE

        self.pieces_table = QTableWidget()

        self.pieces_table.setColumnCount(6)

        self.pieces_table.setHorizontalHeaderLabels([
            "Pièce",
            "Référence",
            "Qté",
            "Prix",
            "Total",
            "Action"
        ])

        self.pieces_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.pieces_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.pieces_table.verticalHeader().setVisible(
            False
        )

        pieces_header = (
            self.pieces_table.horizontalHeader()
        )

        pieces_header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        pieces_header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        pieces_header.setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        pieces_header.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        pieces_header.setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        pieces_layout.addWidget(
            self.pieces_table
        )

        self.pieces_total_label = QLabel(
            "Total pièces : 0.00 DH"
        )

        self.pieces_total_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2563EB;
        """)

        pieces_layout.addWidget(
            self.pieces_total_label
        )

        content.addWidget(
            pieces_group
        )

        # ========================================================
        # ESTIMATION
        # ========================================================

        estimation_group = QGroupBox("Estimation")

        estimation_layout = QGridLayout(
            estimation_group
        )

        self.delai_label = self.create_info_label()
        self.cout_estime_label = self.create_info_label()
        self.cout_reel_label = self.create_info_label()

        estimation_layout.addWidget(
            QLabel("Délai estimé"),
            0, 0
        )

        estimation_layout.addWidget(
            self.delai_label,
            0, 1
        )

        estimation_layout.addWidget(
            QLabel("Coût estimé"),
            1, 0
        )

        estimation_layout.addWidget(
            self.cout_estime_label,
            1, 1
        )

        estimation_layout.addWidget(
            QLabel("Coût réel"),
            2, 0
        )

        estimation_layout.addWidget(
            self.cout_reel_label,
            2, 1
        )

        content.addWidget(
            estimation_group
        )

        # ========================================================
        # ACTIONS
        # ========================================================

        self.detail_actions = QHBoxLayout()

        self.edit_detail_button = QPushButton(
            "✏ Modifier"
        )

        self.edit_detail_button.setObjectName(
            "primaryButton"
        )

        self.edit_detail_button.clicked.connect(
            self.enter_edit_mode
        )

        self.detail_actions.addStretch()

        self.detail_actions.addWidget(
            self.edit_detail_button
        )

        # Boutons modification
        self.cancel_edit_button = QPushButton(
            "Annuler"
        )

        self.save_detail_button = QPushButton(
            "Enregistrer"
        )

        self.save_detail_button.setObjectName(
            "primaryButton"
        )

        self.cancel_edit_button.clicked.connect(
            self.cancel_edit_mode
        )

        self.save_detail_button.clicked.connect(
            self.save_dossier
        )

        self.detail_actions.addWidget(
            self.cancel_edit_button
        )

        self.detail_actions.addWidget(
            self.save_detail_button
        )

        content.addLayout(
            self.detail_actions
        )

        scroll.setWidget(container)

        layout.addWidget(
            scroll,
            1
        )

        # Initialisation
        self.set_edit_mode(False)

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

    def set_edit_mode(self, enabled):

        self.edit_mode = enabled

        # ========================================================
        # CLIENT
        # ========================================================

        self.client_nom.setVisible(not enabled)
        self.client_tel.setVisible(not enabled)
        self.client_email.setVisible(not enabled)

        self.edit_client_nom.setVisible(enabled)
        self.edit_client_tel.setVisible(enabled)
        self.edit_client_email.setVisible(enabled)

        # ========================================================
        # MATÉRIEL
        # ========================================================

        self.machine_type.setVisible(not enabled)
        self.machine_marque.setVisible(not enabled)
        self.machine_modele.setVisible(not enabled)
        self.machine_serie.setVisible(not enabled)

        self.edit_machine_type.setVisible(enabled)
        self.edit_machine_marque.setVisible(enabled)
        self.edit_machine_modele.setVisible(enabled)
        self.edit_machine_serie.setVisible(enabled)

        # ========================================================
        # DIAGNOSTIC
        # ========================================================

        self.probleme_view.setVisible(not enabled)
        self.diagnostic_view.setVisible(not enabled)
        self.intervention_view.setVisible(not enabled)
        self.pieces_defectueuses_view.setVisible(not enabled)
        self.remarques_view.setVisible(not enabled)

        self.probleme_edit.setVisible(enabled)
        self.diagnostic_edit.setVisible(enabled)
        self.intervention_edit.setVisible(enabled)
        self.pieces_defectueuses_edit.setVisible(enabled)
        self.remarques_edit.setVisible(enabled)

        # ========================================================
        # STATUT
        # ========================================================

        self.status_combo.setVisible(enabled)

        # ========================================================
        # PIÈCES UTILISÉES
        # ========================================================

        self.pieces_edit_controls.setVisible(enabled)

        # ========================================================
        # BOUTONS
        # ========================================================

        self.edit_detail_button.setVisible(not enabled)

        self.cancel_edit_button.setVisible(enabled)
        self.save_detail_button.setVisible(enabled)

        # ========================================================
        # TITRE DU MODE
        # ========================================================

        if enabled:

            self.edit_detail_button.setText(
                "✏ Modifier"
            )

            self.save_detail_button.setText(
                "Enregistrer"
            )

            self.cancel_edit_button.setText(
                "Annuler"
            )

    def enter_edit_mode(self):

        if not self.current_dossier:
            return

        dossier = self.current_dossier

        client = dossier.get("client")

        if not isinstance(client, dict):
            client = {}

        # ========================================================
        # CLIENT
        # ========================================================

        self.edit_client_nom.setText(
            str(
                client.get(
                    "nom",
                    dossier.get("client_nom", "")
                ) or ""
            )
        )

        self.edit_client_tel.setText(
            str(
                client.get(
                    "telephone",
                    dossier.get("client_telephone", "")
                ) or ""
            )
        )

        self.edit_client_email.setText(
            str(
                client.get("email", "")
            ) or ""
        )

        # ========================================================
        # MATÉRIEL
        # ========================================================

        self.edit_machine_type.setText(
            str(
                dossier.get(
                    "type_materiel",
                    ""
                ) or ""
            )
        )

        self.edit_machine_marque.setText(
            str(
                dossier.get(
                    "marque",
                    ""
                ) or ""
            )
        )

        self.edit_machine_modele.setText(
            str(
                dossier.get(
                    "modele",
                    ""
                ) or ""
            )
        )

        self.edit_machine_serie.setText(
            str(
                dossier.get(
                    "numero_serie",
                    ""
                ) or ""
            )
        )

        # ========================================================
        # DIAGNOSTIC
        # ========================================================

        self.probleme_edit.setPlainText(
            str(
                dossier.get(
                    "probleme",
                    ""
                ) or ""
            )
        )

        self.diagnostic_edit.setPlainText(
            str(
                dossier.get(
                    "diagnostic",
                    ""
                ) or ""
            )
        )

        self.intervention_edit.setPlainText(
            str(
                dossier.get(
                    "intervention",
                    ""
                ) or ""
            )
        )

        self.pieces_defectueuses_edit.setPlainText(
            str(
                dossier.get(
                    "pieces_defectueuses",
                    ""
                ) or ""
            )
        )

        self.remarques_edit.setPlainText(
            str(
                dossier.get(
                    "remarques",
                    ""
                ) or ""
            )
        )

        # ========================================================
        # STATUT
        # ========================================================

        index = self.status_combo.findText(
            str(
                dossier.get(
                    "statut",
                    ""
                )
            )
        )

        if index >= 0:
            self.status_combo.setCurrentIndex(index)

        self.set_edit_mode(True)

        # Recharger la liste des pièces disponibles
        self.load_stock()
        self.fill_piece_combo()

        # Recharger les pièces actuellement utilisées
        self.load_pieces_utilisees()

    # ========================================================
    # ANNULER MODE MODIFICATION
    # ========================================================
    def cancel_edit_mode(self):

        if not self.current_dossier:
            return

        # Recharger les données originales
        self.load_detail_data()

        # Toujours revenir à la consultation
        self.set_edit_mode(False)

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
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            self.dossiers = (
                data
                if isinstance(data, list)
                else []
            )

            self.load_stock()

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

        self.table.setRowCount(
            0
        )

        for dossier in dossiers:

            row = self.table.rowCount()

            self.table.insertRow(
                row
            )

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

            action_layout = QHBoxLayout(
                action_widget
            )

            action_layout.setContentsMargins(
                2,
                2,
                2,
                2
            )

            action_layout.setSpacing(3)

            # ------------------------------------------------
            # MODIFIER
            # ------------------------------------------------

            edit_button = QPushButton(
                "✏"
            )

            edit_button.setObjectName(
                "editIconButton"
            )

            edit_button.setToolTip(
                "Modifier le dossier"
            )

            edit_button.setFixedSize(
                24,
                24
            )

            edit_button.clicked.connect(
                lambda checked=False,
                d=dossier:
                self.open_dossier(d)
            )

            action_layout.addWidget(
                edit_button
            )

            # ------------------------------------------------
            # SUPPRIMER
            # ------------------------------------------------

            delete_button = QPushButton(
                "🗑"
            )

            delete_button.setObjectName(
                "deleteIconButton"
            )

            delete_button.setToolTip(
                "Supprimer le dossier"
            )

            delete_button.setFixedSize(
                24,
                24
            )

            delete_button.clicked.connect(
                lambda checked=False,
                d=dossier:
                self.delete_dossier(d)
            )

            action_layout.addWidget(
                delete_button
            )

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

        dossier_id = dossier.get("id")

        if not dossier_id:

            QMessageBox.warning(
                self,
                "Erreur",
                "Identifiant du dossier introuvable."
            )

            return

        # ----------------------------------------------------
        # Récupérer la version complète
        # ----------------------------------------------------

        try:

            response = requests.get(
                f"{API_URL}/reparations/{dossier_id}",
                timeout=15
            )

            response.raise_for_status()

            dossier_complet = response.json()

            if isinstance(
                dossier_complet,
                dict
            ):
                dossier = dossier_complet

        except requests.RequestException as error:

            QMessageBox.warning(
                self,
                "Erreur",
                "Impossible de récupérer les données du dossier.\n\n"
                f"{error}"
            )

            return

        # ----------------------------------------------------
        # DIALOG
        # ----------------------------------------------------

        dialog = QDialog(self)

        dialog.setWindowTitle(
            f"Modifier le dossier "
            f"{dossier.get('numero_dossier', '')}"
        )

        dialog.setMinimumSize(
            650,
            700
        )

        dialog.setStyleSheet(
            PAGE_STYLE
        )

        main_layout = QVBoxLayout(
            dialog
        )

        main_layout.setContentsMargins(
            25,
            20,
            25,
            20
        )

        main_layout.setSpacing(15)

        # ----------------------------------------------------
        # TITRE
        # ----------------------------------------------------

        title = QLabel(
            "Modifier les données du dossier"
        )

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #111827;
        """)

        main_layout.addWidget(
            title
        )

        subtitle = QLabel(
            f"Dossier : "
            f"{dossier.get('numero_dossier', '-')}"
        )

        subtitle.setStyleSheet("""
            color: #6B7280;
            font-size: 13px;
        """)

        main_layout.addWidget(
            subtitle
        )

        # ----------------------------------------------------
        # SCROLL
        # ----------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        container = QWidget()

        form_layout = QVBoxLayout(
            container
        )

        form_layout.setSpacing(15)

        # ====================================================
        # CLIENT
        # ====================================================

        client_group = QGroupBox(
            "Informations client"
        )

        client_layout = QGridLayout(
            client_group
        )

        client = dossier.get(
            "client"
        )

        if not isinstance(
            client,
            dict
        ):
            client = {}

        client_nom_edit = QLineEdit(
            str(
                client.get(
                    "nom",
                    dossier.get(
                        "client_nom",
                        ""
                    )
                ) or ""
            )
        )

        client_tel_edit = QLineEdit(
            str(
                client.get(
                    "telephone",
                    dossier.get(
                        "client_telephone",
                        ""
                    )
                ) or ""
            )
        )

        client_email_edit = QLineEdit(
            str(
                client.get(
                    "email",
                    ""
                ) or ""
            )
        )

        client_layout.addWidget(
            QLabel("Nom"),
            0,
            0
        )

        client_layout.addWidget(
            client_nom_edit,
            0,
            1
        )

        client_layout.addWidget(
            QLabel("Téléphone"),
            1,
            0
        )

        client_layout.addWidget(
            client_tel_edit,
            1,
            1
        )

        client_layout.addWidget(
            QLabel("Email"),
            2,
            0
        )

        client_layout.addWidget(
            client_email_edit,
            2,
            1
        )

        form_layout.addWidget(
            client_group
        )

        # ====================================================
        # MATÉRIEL
        # ====================================================

        machine_group = QGroupBox(
            "Informations matériel"
        )

        machine_layout = QGridLayout(
            machine_group
        )

        type_edit = QLineEdit(
            str(
                dossier.get(
                    "type_materiel",
                    ""
                ) or ""
            )
        )

        marque_edit = QLineEdit(
            str(
                dossier.get(
                    "marque",
                    ""
                ) or ""
            )
        )

        modele_edit = QLineEdit(
            str(
                dossier.get(
                    "modele",
                    ""
                ) or ""
            )
        )

        serie_edit = QLineEdit(
            str(
                dossier.get(
                    "numero_serie",
                    ""
                ) or ""
            )
        )

        machine_layout.addWidget(
            QLabel("Type de matériel"),
            0,
            0
        )

        machine_layout.addWidget(
            type_edit,
            0,
            1
        )

        machine_layout.addWidget(
            QLabel("Marque"),
            1,
            0
        )

        machine_layout.addWidget(
            marque_edit,
            1,
            1
        )

        machine_layout.addWidget(
            QLabel("Modèle"),
            2,
            0
        )

        machine_layout.addWidget(
            modele_edit,
            2,
            1
        )

        machine_layout.addWidget(
            QLabel("N° série"),
            3,
            0
        )

        machine_layout.addWidget(
            serie_edit,
            3,
            1
        )

        form_layout.addWidget(
            machine_group
        )

        # ====================================================
        # DIAGNOSTIC
        # ====================================================

        problem_group = QGroupBox(
            "Diagnostic et intervention"
        )

        problem_layout = QGridLayout(
            problem_group
        )

        probleme_edit = QTextEdit(
            str(
                dossier.get(
                    "probleme",
                    ""
                ) or ""
            )
        )

        probleme_edit.setMaximumHeight(
            80
        )

        diagnostic_edit = QTextEdit(
            str(
                dossier.get(
                    "diagnostic",
                    ""
                ) or ""
            )
        )

        diagnostic_edit.setMaximumHeight(
            80
        )

        intervention_edit = QTextEdit(
            str(
                dossier.get(
                    "intervention",
                    ""
                ) or ""
            )
        )

        intervention_edit.setMaximumHeight(
            80
        )

        pieces_edit = QTextEdit(
            str(
                dossier.get(
                    "pieces_defectueuses",
                    ""
                ) or ""
            )
        )

        pieces_edit.setMaximumHeight(
            80
        )

        remarques_edit = QTextEdit(
            str(
                dossier.get(
                    "remarques",
                    ""
                ) or ""
            )
        )

        remarques_edit.setMaximumHeight(
            80
        )

        problem_layout.addWidget(
            QLabel("Problème signalé"),
            0,
            0
        )

        problem_layout.addWidget(
            probleme_edit,
            0,
            1
        )

        problem_layout.addWidget(
            QLabel("Diagnostic"),
            1,
            0
        )

        problem_layout.addWidget(
            diagnostic_edit,
            1,
            1
        )

        problem_layout.addWidget(
            QLabel("Intervention"),
            2,
            0
        )

        problem_layout.addWidget(
            intervention_edit,
            2,
            1
        )

        problem_layout.addWidget(
            QLabel("Pièces défectueuses"),
            3,
            0
        )

        problem_layout.addWidget(
            pieces_edit,
            3,
            1
        )

        problem_layout.addWidget(
            QLabel("Remarques"),
            4,
            0
        )

        problem_layout.addWidget(
            remarques_edit,
            4,
            1
        )

        form_layout.addWidget(
            problem_group
        )

        # ====================================================
        # STATUT
        # ====================================================

        status_group = QGroupBox(
            "Statut"
        )

        status_layout = QHBoxLayout(
            status_group
        )

        status_layout.addWidget(
            QLabel("Statut :")
        )

        status_edit = QComboBox()

        status_edit.addItems([
            "En attente",
            "En diagnostic",
            "En réparation",
            "Terminé"
        ])

        current_status = str(
            dossier.get(
                "statut",
                ""
            )
        )

        index = status_edit.findText(
            current_status
        )

        if index >= 0:
            status_edit.setCurrentIndex(
                index
            )

        status_layout.addWidget(
            status_edit
        )

        status_layout.addStretch()

        form_layout.addWidget(
            status_group
        )

        form_layout.addStretch()

        scroll.setWidget(
            container
        )

        main_layout.addWidget(
            scroll,
            1
        )

        # ====================================================
        # BOUTONS
        # ====================================================

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save
            | QDialogButtonBox.Cancel
        )

        buttons.button(
            QDialogButtonBox.Save
        ).setText(
            "Enregistrer"
        )

        buttons.button(
            QDialogButtonBox.Cancel
        ).setText(
            "Annuler"
        )

        main_layout.addWidget(
            buttons
        )

        buttons.rejected.connect(
            dialog.reject
        )

        # ----------------------------------------------------
        # SAUVEGARDE
        # ----------------------------------------------------

        def save_changes():

            payload = {
                "client_nom":
                    client_nom_edit.text().strip(),

                "client_telephone":
                    client_tel_edit.text().strip(),

                "client_email":
                    client_email_edit.text().strip(),

                "type_materiel":
                    type_edit.text().strip(),

                "marque":
                    marque_edit.text().strip(),

                "modele":
                    modele_edit.text().strip(),

                "numero_serie":
                    serie_edit.text().strip(),

                "probleme":
                    probleme_edit.toPlainText().strip(),

                "diagnostic":
                    diagnostic_edit.toPlainText().strip(),

                "intervention":
                    intervention_edit.toPlainText().strip(),

                "pieces_defectueuses":
                    pieces_edit.toPlainText().strip(),

                "remarques":
                    remarques_edit.toPlainText().strip(),

                "statut":
                    status_edit.currentText()
            }

            try:

                response = requests.patch(
                    f"{API_URL}/reparations/{dossier_id}",
                    json=payload,
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
                        dialog,
                        "Erreur",
                        "Impossible d'enregistrer les modifications.\n\n"
                        f"{detail}"
                    )

                    return

                QMessageBox.information(
                    dialog,
                    "Modification réussie",
                    "Les données du dossier ont été modifiées."
                )

                dialog.accept()

                self.load_dossiers()

                # Si ce dossier est actuellement ouvert
                if (
                    self.current_dossier
                    and self.current_dossier.get("id")
                    == dossier_id
                ):
                    self.current_dossier = response.json()
                    self.load_detail_data()

            except requests.RequestException as error:

                QMessageBox.critical(
                    dialog,
                    "Erreur API",
                    "Impossible de communiquer avec le serveur.\n\n"
                    f"{error}"
                )

        buttons.accepted.connect(
            save_changes
        )

        dialog.exec()

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
        
    # ========================================================
    # CHARGER DETAIL
    # ========================================================

    def load_detail_data(self):

        dossier = self.current_dossier

        if not dossier:
            return

        numero = (
            dossier.get(
                "numero_dossier"
            )
            or f"Dossier #{dossier.get('id')}"
        )

        self.detail_numero.setText(
            numero
        )

        self.detail_date.setText(
            "Réception : "
            + format_date(
                dossier.get(
                    "date_reception"
                )
            )
        )

        self.set_status_label(
            dossier.get(
                "statut"
            )
        )

        # ========================================================
        # CLIENT
        # ========================================================

        client = dossier.get(
            "client"
        )

        if isinstance(
            client,
            dict
        ):

            client_nom = str(
                client.get(
                    "nom"
                )
                or "-"
            )

            client_tel = str(
                client.get(
                    "telephone"
                )
                or "-"
            )

            client_email = str(
                client.get(
                    "email"
                )
                or "-"
            )

        else:

            client_nom = str(
                dossier.get(
                    "client_nom"
                )
                or "-"
            )

            client_tel = str(
                dossier.get(
                    "client_telephone"
                )
                or "-"
            )

            client_email = "-"

        # Consultation

        self.client_nom.setText(
            client_nom
        )

        self.client_tel.setText(
            client_tel
        )

        self.client_email.setText(
            client_email
        )

        # Modification

        self.edit_client_nom.setText(
            client_nom if client_nom != "-" else ""
        )

        self.edit_client_tel.setText(
            client_tel if client_tel != "-" else ""
        )

        self.edit_client_email.setText(
            client_email if client_email != "-" else ""
        )

        # ========================================================
        # MACHINE
        # ========================================================

        machine_type = str(
            dossier.get(
                "type_materiel"
            )
            or "-"
        )

        machine_marque = str(
            dossier.get(
                "marque"
            )
            or "-"
        )

        machine_modele = str(
            dossier.get(
                "modele"
            )
            or "-"
        )

        machine_serie = str(
            dossier.get(
                "numero_serie"
            )
            or "-"
        )

        # Consultation

        self.machine_type.setText(
            machine_type
        )

        self.machine_marque.setText(
            machine_marque
        )

        self.machine_modele.setText(
            machine_modele
        )

        self.machine_serie.setText(
            machine_serie
        )

        # Modification

        self.edit_machine_type.setText(
            machine_type if machine_type != "-" else ""
        )

        self.edit_machine_marque.setText(
            machine_marque if machine_marque != "-" else ""
        )

        self.edit_machine_modele.setText(
            machine_modele if machine_modele != "-" else ""
        )

        self.edit_machine_serie.setText(
            machine_serie if machine_serie != "-" else ""
        )

        # ========================================================
        # INFORMATIONS DE RÉPARATION
        # ========================================================

        probleme = str(
            dossier.get(
                "probleme"
            )
            or "-"
        )

        diagnostic = str(
            dossier.get(
                "diagnostic"
            )
            or "-"
        )

        intervention = str(
            dossier.get(
                "intervention"
            )
            or "-"
        )

        pieces_defectueuses = str(
            dossier.get(
                "pieces_defectueuses"
            )
            or "-"
        )

        remarques = str(
            dossier.get(
                "remarques"
            )
            or "-"
        )

        # ========================================================
        # CONSULTATION
        # ========================================================

        self.probleme_view.setText(
            probleme
        )

        self.diagnostic_view.setText(
            diagnostic
        )

        self.intervention_view.setText(
            intervention
        )

        self.pieces_defectueuses_view.setText(
            pieces_defectueuses
        )

        self.remarques_view.setText(
            remarques
        )

        # ========================================================
        # MODIFICATION
        # ========================================================

        self.probleme_edit.setText(
            probleme if probleme != "-" else ""
        )

        self.diagnostic_edit.setText(
            diagnostic if diagnostic != "-" else ""
        )

        self.intervention_edit.setText(
            intervention if intervention != "-" else ""
        )

        self.pieces_defectueuses_edit.setText(
            pieces_defectueuses
            if pieces_defectueuses != "-"
            else ""
        )

        self.remarques_edit.setText(
            remarques if remarques != "-" else ""
        )

        # ========================================================
        # STATUT
        # ========================================================

        statut = dossier.get(
            "statut"
        )

        index = self.status_combo.findText(
            str(statut)
        )

        if index >= 0:

            self.status_combo.setCurrentIndex(
                index
            )

        # ========================================================
        # ESTIMATION
        # ========================================================

        delai = dossier.get(
            "delai_estime"
        )

        if delai is not None:

            self.delai_label.setText(
                f"{delai} jour(s)"
            )

        else:

            self.delai_label.setText(
                "-"
            )

        self.cout_estime_label.setText(
            format_money(
                dossier.get(
                    "cout_estime"
                )
            )
        )

        self.cout_reel_label.setText(
            format_money(
                dossier.get(
                    "cout_reel"
                )
            )
        )

        # ========================================================
        # STOCK
        # ========================================================

        self.load_stock()
        self.fill_piece_combo()

        # ========================================================
        # PIÈCES UTILISÉES
        # ========================================================

        self.load_pieces_utilisees()
        self.display_pieces_utilisees()

        # ========================================================
        # RESTAURER LE MODE ACTUEL
        # ========================================================
        self.set_edit_mode(False)

    # ========================================================
    # STATUT LABEL
    # ========================================================

    def set_status_label(
        self,
        statut
    ):

        statut = str(
            statut or "-"
        )

        self.detail_status_label.setText(
            statut
        )

        colors = {
            "En attente": (
                "#FEF3C7",
                "#92400E"
            ),
            "En diagnostic": (
                "#DBEAFE",
                "#1D4ED8"
            ),
            "En réparation": (
                "#E0E7FF",
                "#4338CA"
            ),
            "Terminé": (
                "#DCFCE7",
                "#15803D"
            )
        }

        background, foreground = colors.get(
            statut,
            (
                "#F3F4F6",
                "#374151"
            )
        )

        self.detail_status_label.setStyleSheet(
            f"""
            QLabel {{
                background: {background};
                color: {foreground};
                border-radius: 8px;
                padding: 9px 15px;
                font-weight: bold;
            }}
            """
        )

    # ========================================================
    # MODIFICATION DOSSIER
    # ========================================================
    def save_dossier(self):

        if not self.current_dossier:
            return

        dossier_id = self.current_dossier.get("id")

        if not dossier_id:
            return

        payload = {
            "client_nom":
                self.edit_client_nom.text().strip(),

            "client_telephone":
                self.edit_client_tel.text().strip(),

            "client_email":
                self.edit_client_email.text().strip(),

            "type_materiel":
                self.edit_machine_type.text().strip(),

            "marque":
                self.edit_machine_marque.text().strip(),

            "modele":
                self.edit_machine_modele.text().strip(),

            "numero_serie":
                self.edit_machine_serie.text().strip(),

            "probleme":
                self.probleme_edit.toPlainText().strip()
                or None,

            "diagnostic":
                self.diagnostic_edit.toPlainText().strip()
                or None,

            "intervention":
                self.intervention_edit.toPlainText().strip()
                or None,

            "pieces_defectueuses":
                self.pieces_defectueuses_edit
                .toPlainText()
                .strip()
                or None,

            "remarques":
                self.remarques_edit
                .toPlainText()
                .strip()
                or None,

            "statut":
                self.status_combo.currentText()
        }

        try:

            response = requests.patch(
                f"{API_URL}/reparations/{dossier_id}",
                json=payload,
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
                    "Erreur",
                    "Impossible d'enregistrer les modifications.\n\n"
                    f"{detail}"
                )

                return

            data = response.json()

            if isinstance(data, dict):
                self.current_dossier = data
            else:
                self.refresh_current_dossier()
                return

            self.set_edit_mode(False)

            self.load_detail_data()

            self.load_dossiers()

            self.status_changed.emit()

            QMessageBox.information(
                self,
                "Modification enregistrée",
                "Les modifications ont été enregistrées."
            )

        except requests.RequestException as error:

            QMessageBox.critical(
                self,
                "Erreur API",
                "Impossible de communiquer avec le serveur.\n\n"
                f"{error}"
            )
        
    # ========================================================
    # CHANGEMENT STATUT
    # ========================================================

    def change_status(self):

        if not self.current_dossier:
            return

        dossier_id = self.current_dossier.get(
            "id"
        )

        ancien = self.current_dossier.get(
            "statut"
        )

        nouveau = self.status_combo.currentText()

        if ancien == nouveau:

            QMessageBox.information(
                self,
                "Statut",
                "Le dossier possède déjà ce statut."
            )

            return

        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous changer le statut du dossier ?\n\n"
            f"De : {ancien}\n"
            f"Vers : {nouveau}",
            QMessageBox.Yes |
            QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        payload = {
            "nouveau_statut": nouveau,
            "utilisateur_id": DEFAULT_UTILISATEUR_ID
        }

        try:

            response = requests.patch(
                f"{API_URL}/reparations/"
                f"{dossier_id}/statut",
                json=payload,
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
                    "Erreur",
                    f"Impossible de changer le statut.\n\n"
                    f"{detail}"
                )

                return

            self.current_dossier = response.json()

            self.load_detail_data()

            self.load_dossiers()

            self.status_changed.emit()

            QMessageBox.information(
                self,
                "Statut mis à jour",
                f"Le dossier est maintenant :\n\n{nouveau}"
            )

        except requests.RequestException as error:

            QMessageBox.critical(
                self,
                "Erreur API",
                f"Impossible de communiquer avec le serveur.\n\n{error}"
            )

    # ========================================================
    # STOCK : COMBO
    # ========================================================

    def fill_piece_combo(self):

        self.piece_combo.blockSignals(
            True
        )

        self.piece_combo.clear()

        self.piece_combo.addItem(
            "Sélectionner une pièce...",
            None
        )

        for stock in self.stocks:

            quantite = safe_int(
                stock.get(
                    "quantite"
                )
            )

            if quantite <= 0:
                continue

            nom = (
                stock.get(
                    "nom_piece"
                )
                or "Pièce"
            )

            reference = (
                stock.get(
                    "reference"
                )
                or "-"
            )

            text = (
                f"{nom} | "
                f"Réf: {reference} | "
                f"Stock: {quantite}"
            )

            self.piece_combo.addItem(
                text,
                stock
            )

        self.piece_combo.blockSignals(
            False
        )

        self.filter_stock(
            self.piece_search.text()
        )

        self.on_piece_selected()

    # ========================================================
    # RECHERCHE PIECE
    # ========================================================

    def filter_stock(
        self,
        text=""
    ):

        search = (
            text
            .strip()
            .lower()
        )

        for index in range(
            self.piece_combo.count()
        ):

            stock = self.piece_combo.itemData(
                index
            )

            if not stock:

                self.piece_combo.view().setRowHidden(
                    index,
                    False
                )

                continue

            searchable = " ".join([
                str(
                    stock.get(
                        "nom_piece",
                        ""
                    )
                ),
                str(
                    stock.get(
                        "reference",
                        ""
                    )
                ),
                str(
                    stock.get(
                        "categorie",
                        ""
                    )
                )
            ]).lower()

            hidden = (
                search not in searchable
            )

            self.piece_combo.view().setRowHidden(
                index,
                hidden
            )

    # ========================================================
    # PIECE SELECTIONNEE
    # ========================================================

    def on_piece_selected(self):

        stock = self.piece_combo.currentData()

        if not stock:

            self.piece_info_label.setText(
                "Sélectionnez une pièce."
            )

            self.piece_quantity.setMaximum(
                1
            )

            return

        disponible = safe_int(
            stock.get(
                "quantite"
            )
        )

        prix = safe_float(
            stock.get(
                "prix_unitaire"
            )
        )

        self.piece_quantity.setMaximum(
            max(
                1,
                disponible
            )
        )

        self.piece_info_label.setText(
            f"Disponible : {disponible}    |    "
            f"Prix unitaire : {format_money(prix)}"
        )

    # ========================================================
    # AJOUTER PIECE
    # ========================================================

    def add_piece_to_dossier(self):

        if not self.current_dossier:
            return

        stock = self.piece_combo.currentData()

        if not stock:
            QMessageBox.warning(
                self,
                "Pièce",
                "Veuillez sélectionner une pièce."
            )
            return

        piece_id = stock.get("id")

        quantite = self.piece_quantity.value()

        disponible = safe_int(
            stock.get("quantite")
        )

        if quantite > disponible:

            QMessageBox.warning(
                self,
                "Stock insuffisant",
                f"Disponible : {disponible}\n"
                f"Demandé : {quantite}"
            )

            return

        dossier_id = self.current_dossier.get(
            "id"
        )

        payload = {
            "piece_id": piece_id,
            "quantite": quantite
        }

        try:

            response = requests.post(
                f"{API_URL}/reparations/"
                f"{dossier_id}/pieces",
                json=payload,
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
                    "Erreur",
                    "Impossible d'ajouter la pièce.\n\n"
                    f"{detail}"
                )

                return

            # Recharger le stock
            self.load_stock()

            # Recharger les pièces utilisées
            self.load_pieces_utilisees()

            # Recharger la liste de sélection
            self.fill_piece_combo()

            self.piece_quantity.setValue(1)

            QMessageBox.information(
                self,
                "Pièce ajoutée",
                "La pièce a été ajoutée à la réparation."
            )

        except requests.RequestException as error:

            QMessageBox.critical(
                self,
                "Erreur API",
                "Impossible de communiquer avec le serveur.\n\n"
                f"{error}"
            )
        
    # ========================================================
    # CHARGER PIECES UTILISEES
    # ========================================================

    def load_pieces_utilisees(self):

        if not self.current_dossier:

            return

        dossier_id = self.current_dossier.get(
            "id"
        )

        try:

            response = requests.get(
                f"{API_URL}/reparations/"
                f"{dossier_id}/pieces",
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            self.pieces_utilisees = (
                data
                if isinstance(
                    data,
                    list
                )
                else []
            )

            self.display_pieces()

        except requests.RequestException as error:

            print(
                "[DOSSIERS] Impossible de charger les pièces :",
                error
            )

            self.pieces_utilisees = []

            self.pieces_table.setRowCount(
                0
            )

            self.pieces_total_label.setText(
                "Total pièces : 0.00 DH"
            )

    # ========================================================
    # AFFICHER PIECES
    # ========================================================

    def display_pieces(self):

        self.pieces_table.setRowCount(
            0
        )

        total_general = 0.0

        for piece in self.pieces_utilisees:

            row = self.pieces_table.rowCount()

            self.pieces_table.insertRow(
                row
            )

            # ------------------------------------------------
            # NOM PIECE
            # ------------------------------------------------

            piece_info = piece.get(
                "piece"
            )

            if isinstance(
                piece_info,
                dict
            ):

                nom = (
                    piece_info.get(
                        "nom_piece"
                    )
                    or f"Pièce #{piece.get('piece_id')}"
                )

                reference = (
                    piece_info.get(
                        "reference"
                    )
                    or "-"
                )

            else:

                stock = self.find_stock(
                    piece.get(
                        "piece_id"
                    )
                )

                if stock:

                    nom = (
                        stock.get(
                            "nom_piece"
                        )
                        or f"Pièce #{piece.get('piece_id')}"
                    )

                    reference = (
                        stock.get(
                            "reference"
                        )
                        or "-"
                    )

                else:

                    nom = (
                        f"Pièce #{piece.get('piece_id')}"
                    )

                    reference = "-"

            quantite = safe_int(
                piece.get(
                    "quantite"
                )
            )

            prix = safe_float(
                piece.get(
                    "prix_utilise"
                )
            )

            total = (
                quantite
                * prix
            )

            total_general += total

            values = [
                nom,
                reference,
                str(quantite),
                format_money(prix),
                format_money(total)
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
                        if col in [2, 3, 4]
                        else Qt.AlignLeft
                    )
                )

                self.pieces_table.setItem(
                    row,
                    col,
                    item
                )

        self.pieces_total_label.setText(
            f"Total pièces : "
            f"{format_money(total_general)}"
        )

    # ========================================================
    # FIND STOCK
    # ========================================================

    def find_stock(
        self,
        piece_id
    ):

        for stock in self.stocks:

            if stock.get(
                "id"
            ) == piece_id:

                return stock

        return None

    # ========================================================
    # ACTUALISER DETAIL
    # ========================================================

    def refresh_current_dossier(self):

        if not self.current_dossier:
            return

        dossier_id = self.current_dossier.get(
            "id"
        )

        try:

            response = requests.get(
                f"{API_URL}/reparations/{dossier_id}",
                timeout=15
            )

            response.raise_for_status()

            self.current_dossier = response.json()

            self.load_detail_data()

        except requests.RequestException as error:

            QMessageBox.warning(
                self,
                "Erreur",
                f"Impossible d'actualiser le dossier.\n\n"
                f"{error}"
            )

    # ========================================================
    # RETOUR
    # ========================================================

    def back_to_list(self):

        self.stack.setCurrentWidget(
            self.list_page
        )

        self.load_dossiers()

    # ========================================================
    # PDF
    # ========================================================

    def download_pdf(self):

        if not self.current_dossier:
            return

        dossier_id = self.current_dossier.get(
            "id"
        )

        numero = (
            self.current_dossier.get(
                "numero_dossier"
            )
            or f"dossier_{dossier_id}"
        )

        try:

            response = requests.get(
                f"{API_URL}/reparations/"
                f"{dossier_id}/fiche",
                timeout=30
            )

            if not response.ok:

                QMessageBox.warning(
                    self,
                    "PDF",
                    "Impossible de générer la fiche PDF."
                )

                return

            from PySide6.QtWidgets import QFileDialog

            path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer la fiche",
                f"{numero}.pdf",
                "Fichier PDF (*.pdf)"
            )

            if not path:
                return

            with open(
                path,
                "wb"
            ) as file:

                file.write(
                    response.content
                )

            QMessageBox.information(
                self,
                "PDF généré",
                "La fiche PDF a été générée avec succès."
            )

        except (
            requests.RequestException,
            OSError
        ) as error:

            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de générer le PDF.\n\n{error}"
            )

    def remove_piece_from_edit(self, row):
        """
        Supprime une pièce de la liste locale des pièces utilisées.

        La suppression définitive côté backend sera effectuée
        lors de l'enregistrement du dossier.
        """

        if row < 0 or row >= len(self.pieces_utilisees):
            return

        piece = self.pieces_utilisees[row]

        nom = (
            piece.get("nom")
            or piece.get("designation")
            or "Cette pièce"
        )

        reply = QMessageBox.question(
            self,
            "Supprimer la pièce",
            f"Voulez-vous retirer « {nom} » du dossier ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.pieces_utilisees.pop(row)

        self.display_pieces_utilisees()

    def display_pieces_utilisees(self):

        self.pieces_table.setRowCount(0)

        total_general = 0.0

        for index, piece in enumerate(self.pieces_utilisees):

            row = self.pieces_table.rowCount()

            self.pieces_table.insertRow(row)

            nom = (
                piece.get("nom")
                or piece.get("designation")
                or piece.get("piece_nom")
                or "-"
            )

            reference = (
                piece.get("reference")
                or piece.get("piece_reference")
                or "-"
            )

            quantite = safe_int(
                piece.get("quantite")
                or piece.get("quantity")
                or 1,
                1
            )

            prix = safe_float(
                piece.get("prix_unitaire")
                or piece.get("prix")
                or 0
            )

            total = safe_float(
                piece.get("total"),
                prix * quantite
            )

            total_general += total

            values = [
                nom,
                reference,
                str(quantite),
                format_money(prix),
                format_money(total)
            ]

            for col, value in enumerate(values):

                item = QTableWidgetItem(
                    str(value)
                )

                if col >= 2:
                    item.setTextAlignment(
                        Qt.AlignCenter
                    )

                self.pieces_table.setItem(
                    row,
                    col,
                    item
                )

            # ====================================================
            # ACTION
            # ====================================================

            action_widget = QWidget()

            action_layout = QHBoxLayout(
                action_widget
            )

            action_layout.setContentsMargins(
                2,
                2,
                2,
                2
            )

            action_layout.setAlignment(
                Qt.AlignCenter
            )

            remove_button = QPushButton(
                "×"
            )

            remove_button.setObjectName(
                "deleteIconButton"
            )

            remove_button.setToolTip(
                "Retirer cette pièce"
            )

            remove_button.setFixedSize(
                22,
                22
            )

            remove_button.clicked.connect(
                lambda checked=False,
                r=row:
                self.remove_piece_from_edit(r)
            )

            action_layout.addWidget(
                remove_button
            )

            self.pieces_table.setCellWidget(
                row,
                5,
                action_widget
            )

        self.pieces_total_label.setText(
            f"Total pièces : {format_money(total_general)}"
        )

        # La colonne Action est uniquement utile en modification
        self.pieces_table.setColumnHidden(
            5,
            not self.edit_mode
        )
        