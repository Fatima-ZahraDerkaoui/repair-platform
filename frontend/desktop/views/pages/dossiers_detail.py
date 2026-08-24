from PySide6.QtWidgets import (
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
    QTextEdit,
    QWidget
)

from PySide6.QtCore import Qt

import requests

from views.pages.dossiers_utils import (
    safe_int,
    safe_float,
    format_date,
    format_money,
)

API_URL = "http://127.0.0.1:8000"

DEFAULT_UTILISATEUR_ID = 1


class DossierDetailMixin:

    def setup_detail_page(self):

        layout = QVBoxLayout(self.detail_page)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # ============================================================
        # BARRE SUPÉRIEURE
        # ============================================================

        header = QHBoxLayout()
        header.setSpacing(8)

        self.back_button = QPushButton("←  Retour aux dossiers")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.back_to_list)

        header.addWidget(self.back_button)
        header.addStretch()

        self.detail_refresh_button = QPushButton("↻  Actualiser")
        self.detail_refresh_button.setObjectName("secondaryButton")
        self.detail_refresh_button.clicked.connect(
            self.refresh_current_dossier
        )

        header.addWidget(self.detail_refresh_button)

        self.pdf_button = QPushButton("▣  PDF")
        self.pdf_button.setObjectName("secondaryButton")
        self.pdf_button.clicked.connect(self.download_pdf)

        header.addWidget(self.pdf_button)

        layout.addLayout(header)

        # ============================================================
        # SCROLL
        # ============================================================

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        container = QWidget()

        content = QVBoxLayout(container)
        content.setContentsMargins(4, 4, 8, 25)
        content.setSpacing(14)

        # ============================================================
        # CARTE IDENTIFICATION
        # ============================================================

        header_card = QFrame()
        header_card.setObjectName("detailHeaderCard")

        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(22, 18, 22, 18)

        left = QVBoxLayout()
        left.setSpacing(4)

        dossier_title = QLabel("DOSSIER DE RÉPARATION")
        dossier_title.setObjectName("detailOverline")

        left.addWidget(dossier_title)

        self.detail_numero = QLabel()
        self.detail_numero.setObjectName("detailNumero")

        left.addWidget(self.detail_numero)

        self.detail_date = QLabel()
        self.detail_date.setObjectName("detailDate")

        left.addWidget(self.detail_date)

        header_layout.addLayout(left)
        header_layout.addStretch()

        status_container = QVBoxLayout()
        status_container.setSpacing(5)

        status_title = QLabel("STATUT")
        status_title.setObjectName("detailStatusTitle")
        status_title.setAlignment(Qt.AlignCenter)

        status_container.addWidget(status_title)

        self.detail_status_label = QLabel()
        self.detail_status_label.setObjectName("detailStatus")
        self.detail_status_label.setAlignment(Qt.AlignCenter)
        self.detail_status_label.setMinimumWidth(160)

        status_container.addWidget(self.detail_status_label)

        header_layout.addLayout(status_container)

        content.addWidget(header_card)

        # ============================================================
        # CLIENT
        # ============================================================

        client_group = QGroupBox("01  •  Client")
        client_layout = QGridLayout(client_group)

        client_layout.setContentsMargins(18, 22, 18, 18)
        client_layout.setHorizontalSpacing(18)
        client_layout.setVerticalSpacing(10)

        client_layout.setColumnMinimumWidth(0, 120)

        self.client_nom = self.create_info_label()
        self.client_tel = self.create_info_label()
        self.client_email = self.create_info_label()

        self.edit_client_nom = QLineEdit()
        self.edit_client_tel = QLineEdit()
        self.edit_client_email = QLineEdit()

        self.edit_client_nom.setPlaceholderText("Nom du client")
        self.edit_client_tel.setPlaceholderText("Numéro de téléphone")
        self.edit_client_email.setPlaceholderText("Adresse e-mail")

        client_fields = [
            ("Nom complet", self.client_nom, self.edit_client_nom),
            ("Téléphone", self.client_tel, self.edit_client_tel),
            ("Email", self.client_email, self.edit_client_email),
        ]

        for row, (label, view, edit) in enumerate(client_fields):

            field_label = QLabel(label)
            field_label.setObjectName("fieldLabel")

            client_layout.addWidget(
                field_label,
                row,
                0
            )

            client_layout.addWidget(
                view,
                row,
                1
            )

            client_layout.addWidget(
                edit,
                row,
                1
            )

        content.addWidget(client_group)

        # ============================================================
        # MATÉRIEL
        # ============================================================

        machine_group = QGroupBox("02  •  Matériel")
        machine_layout = QGridLayout(machine_group)

        machine_layout.setContentsMargins(18, 22, 18, 18)
        machine_layout.setHorizontalSpacing(18)
        machine_layout.setVerticalSpacing(10)

        machine_layout.setColumnMinimumWidth(0, 120)

        self.machine_type = self.create_info_label()
        self.machine_marque = self.create_info_label()
        self.machine_modele = self.create_info_label()
        self.machine_serie = self.create_info_label()

        self.edit_machine_type = QLineEdit()
        self.edit_machine_marque = QLineEdit()
        self.edit_machine_modele = QLineEdit()
        self.edit_machine_serie = QLineEdit()

        self.edit_machine_type.setPlaceholderText("Type de matériel")
        self.edit_machine_marque.setPlaceholderText("Marque")
        self.edit_machine_modele.setPlaceholderText("Modèle")
        self.edit_machine_serie.setPlaceholderText("Numéro de série")

        machine_fields = [
            ("Type", self.machine_type, self.edit_machine_type),
            ("Marque", self.machine_marque, self.edit_machine_marque),
            ("Modèle", self.machine_modele, self.edit_machine_modele),
            ("N° de série", self.machine_serie, self.edit_machine_serie),
        ]

        for row, (label, view, edit) in enumerate(machine_fields):

            field_label = QLabel(label)
            field_label.setObjectName("fieldLabel")

            machine_layout.addWidget(
                field_label,
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

        # ============================================================
        # DIAGNOSTIC / INTERVENTION
        # ============================================================

        problem_group = QGroupBox(
            "03  •  Diagnostic et intervention"
        )

        problem_layout = QGridLayout(problem_group)

        problem_layout.setContentsMargins(18, 22, 18, 18)
        problem_layout.setHorizontalSpacing(18)
        problem_layout.setVerticalSpacing(12)

        problem_layout.setColumnMinimumWidth(0, 150)

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

        text_edits = [
            self.probleme_edit,
            self.diagnostic_edit,
            self.intervention_edit,
            self.pieces_defectueuses_edit,
            self.remarques_edit
        ]

        for edit in text_edits:
            edit.setMinimumHeight(70)
            edit.setMaximumHeight(110)

        self.probleme_edit.setPlaceholderText(
            "Décrire le problème signalé..."
        )

        self.diagnostic_edit.setPlaceholderText(
            "Saisir le diagnostic technique..."
        )

        self.intervention_edit.setPlaceholderText(
            "Décrire les interventions réalisées..."
        )

        self.pieces_defectueuses_edit.setPlaceholderText(
            "Indiquer les pièces défectueuses..."
        )

        self.remarques_edit.setPlaceholderText(
            "Ajouter des remarques..."
        )

        edit_fields = [
            (
                "Problème signalé",
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

            field_label = QLabel(label)
            field_label.setObjectName("fieldLabel")
            field_label.setAlignment(
                Qt.AlignTop | Qt.AlignLeft
            )

            problem_layout.addWidget(
                field_label,
                row,
                0
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

        # ============================================================
        # STATUT
        # ============================================================

        status_group = QGroupBox(
            "04  •  Statut du dossier"
        )

        status_layout = QHBoxLayout(status_group)
        status_layout.setContentsMargins(18, 20, 18, 20)
        status_layout.setSpacing(12)

        status_label = QLabel("Nouveau statut")
        status_label.setObjectName("fieldLabel")

        status_layout.addWidget(status_label)

        self.status_combo = QComboBox()

        self.status_combo.addItems([
            "En attente",
            "En diagnostic",
            "En réparation",
            "Terminé"
        ])

        self.status_combo.setMinimumWidth(220)

        status_layout.addWidget(
            self.status_combo
        )

        status_layout.addStretch()

        content.addWidget(status_group)

        # ============================================================
        # PIÈCES UTILISÉES
        # ============================================================

        pieces_group = QGroupBox(
            "05  •  Pièces utilisées"
        )

        pieces_layout = QVBoxLayout(pieces_group)
        pieces_layout.setContentsMargins(18, 22, 18, 18)
        pieces_layout.setSpacing(12)

        # ------------------------------------------------------------
        # ZONE AJOUT PIÈCE
        # ------------------------------------------------------------

        self.pieces_edit_controls = QWidget()

        edit_piece_layout = QVBoxLayout(
            self.pieces_edit_controls
        )

        edit_piece_layout.setContentsMargins(
            0, 0, 0, 4
        )
        edit_piece_layout.setSpacing(10)

        # Recherche

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        search_label = QLabel("Rechercher une pièce")
        search_label.setObjectName("fieldLabel")

        search_layout.addWidget(search_label)

        self.piece_search = QLineEdit()

        self.piece_search.setPlaceholderText(
            "Nom, référence ou catégorie..."
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
        selection_layout.setSpacing(10)

        piece_label = QLabel("Pièce")
        piece_label.setObjectName("fieldLabel")

        selection_layout.addWidget(
            piece_label
        )

        self.piece_combo = QComboBox()

        self.piece_combo.setMinimumHeight(38)

        self.piece_combo.currentIndexChanged.connect(
            self.on_piece_selected
        )

        selection_layout.addWidget(
            self.piece_combo,
            1
        )

        quantity_label = QLabel("Quantité")
        quantity_label.setObjectName("fieldLabel")

        selection_layout.addWidget(
            quantity_label
        )

        self.piece_quantity = QSpinBox()

        self.piece_quantity.setRange(
            1,
            100
        )

        self.piece_quantity.setValue(1)
        self.piece_quantity.setMinimumWidth(80)

        selection_layout.addWidget(
            self.piece_quantity
        )

        self.add_piece_button = QPushButton(
            "+  Ajouter"
        )

        self.add_piece_button.setObjectName(
            "successButton"
        )

        self.add_piece_button.clicked.connect(
            self.add_piece
        )

        selection_layout.addWidget(
            self.add_piece_button
        )

        edit_piece_layout.addLayout(
            selection_layout
        )

        # Informations stock

        self.piece_info_label = QLabel(
            "Sélectionnez une pièce."
        )

        self.piece_info_label.setObjectName(
            "pieceInfo"
        )

        edit_piece_layout.addWidget(
            self.piece_info_label
        )

        pieces_layout.addWidget(
            self.pieces_edit_controls
        )

        # ------------------------------------------------------------
        # TABLEAU
        # ------------------------------------------------------------

        self.pieces_table = QTableWidget()
        self.pieces_table.setColumnCount(6)

        self.pieces_table.setHorizontalHeaderLabels([
            "Pièce",
            "Référence",
            "Qté",
            "Prix unitaire",
            "Total",
            "Action"
        ])

        self.pieces_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.pieces_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.pieces_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.pieces_table.verticalHeader().setVisible(
            False
        )

        self.pieces_table.setAlternatingRowColors(
            True
        )

        self.pieces_table.setMinimumHeight(
            180
        )

        pieces_header = (
            self.pieces_table.horizontalHeader()
        )

        pieces_header.setStretchLastSection(
            False
        )

        pieces_header.setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        pieces_header.setSectionResizeMode(
            1,
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

        # ------------------------------------------------------------
        # TOTAL
        # ------------------------------------------------------------

        total_container = QFrame()
        total_container.setObjectName(
            "piecesTotalCard"
        )

        total_layout = QHBoxLayout(
            total_container
        )

        total_layout.setContentsMargins(
            15, 10, 15, 10
        )

        total_layout.addStretch()

        self.pieces_total_label = QLabel(
            "Total pièces : 0.00 DH"
        )

        self.pieces_total_label.setObjectName(
            "piecesTotalLabel"
        )

        total_layout.addWidget(
            self.pieces_total_label
        )

        pieces_layout.addWidget(
            total_container
        )

        content.addWidget(
            pieces_group
        )

        # ============================================================
        # ESTIMATION
        # ============================================================

        estimation_group = QGroupBox(
            "06  •  Estimation financière et délai"
        )

        estimation_layout = QGridLayout(
            estimation_group
        )

        estimation_layout.setContentsMargins(
            18, 22, 18, 18
        )

        estimation_layout.setHorizontalSpacing(
            18
        )

        estimation_layout.setVerticalSpacing(
            10
        )

        estimation_layout.setColumnMinimumWidth(
            0,
            150
        )

        self.delai_label = self.create_info_label()
        self.cout_estime_label = self.create_info_label()
        self.cout_reel_label = self.create_info_label()

        estimation_fields = [
            (
                "Délai estimé",
                self.delai_label
            ),
            (
                "Coût estimé",
                self.cout_estime_label
            ),
            (
                "Coût réel",
                self.cout_reel_label
            )
        ]

        for row, (label, widget) in enumerate(
            estimation_fields
        ):

            field_label = QLabel(label)
            field_label.setObjectName(
                "fieldLabel"
            )

            estimation_layout.addWidget(
                field_label,
                row,
                0
            )

            estimation_layout.addWidget(
                widget,
                row,
                1
            )

        content.addWidget(
            estimation_group
        )

        # ============================================================
        # ACTIONS
        # ============================================================

        actions_frame = QFrame()
        actions_frame.setObjectName(
            "actionsCard"
        )

        self.detail_actions = QHBoxLayout(
            actions_frame
        )

        self.detail_actions.setContentsMargins(
            15, 12, 15, 12
        )

        self.detail_actions.addStretch()

        self.edit_detail_button = QPushButton(
            "✎  Modifier le dossier"
        )

        self.edit_detail_button.setObjectName(
            "primaryButton"
        )

        self.edit_detail_button.clicked.connect(
            self.enter_edit_mode
        )

        self.detail_actions.addWidget(
            self.edit_detail_button
        )

        self.cancel_edit_button = QPushButton(
            "Annuler"
        )

        self.cancel_edit_button.setObjectName(
            "secondaryButton"
        )

        self.cancel_edit_button.clicked.connect(
            self.cancel_edit_mode
        )

        self.detail_actions.addWidget(
            self.cancel_edit_button
        )

        self.save_detail_button = QPushButton(
            "✓  Enregistrer"
        )

        self.save_detail_button.setObjectName(
            "primaryButton"
        )

        self.save_detail_button.clicked.connect(
            self.save_dossier
        )

        self.detail_actions.addWidget(
            self.save_detail_button
        )

        content.addWidget(
            actions_frame
        )

        # ============================================================
        # FIN
        # ============================================================

        scroll.setWidget(container)

        layout.addWidget(
            scroll,
            1
        )

        # Style général de cette page
        self._apply_detail_styles()

        # Mode consultation au démarrage
        self.set_edit_mode(False)

    def _apply_detail_styles(self):

        self.detail_page.setStyleSheet("""
            /* =====================================================
            PAGE
            ===================================================== */

            QScrollArea {
                background: transparent;
                border: none;
            }

            QWidget {
                font-family: "Segoe UI";
                font-size: 13px;
                color: #1F2937;
            }

            /* =====================================================
            GROUPES / CARTES
            ===================================================== */

            QGroupBox {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                font-size: 14px;
                font-weight: 700;
                color: #111827;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 7px;
                background: #FFFFFF;
                color: #111827;
            }

            #detailHeaderCard {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }

            #actionsCard {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
            }

            /* =====================================================
            TITRE DOSSIER
            ===================================================== */

            #detailOverline {
                color: #6B7280;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }

            #detailNumero {
                color: #111827;
                font-size: 25px;
                font-weight: 700;
            }

            #detailDate {
                color: #6B7280;
                font-size: 12px;
            }

            #detailStatusTitle {
                color: #6B7280;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
            }

            #detailStatus {
                min-height: 32px;
                padding: 7px 18px;
                border-radius: 16px;
                font-size: 12px;
                font-weight: 700;
            }

            /* =====================================================
            LABELS
            ===================================================== */

            #fieldLabel {
                color: #6B7280;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel {
                background: transparent;
            }

            /* =====================================================
            CHAMPS DE CONSULTATION
            ===================================================== */

            QGroupBox QLabel:not(#fieldLabel) {
                background: transparent;
            }

            /* =====================================================
            CHAMPS DE MODIFICATION
            ===================================================== */

            QLineEdit,
            QTextEdit,
            QComboBox,
            QSpinBox {
                background: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: 7px;
                padding: 8px 10px;
                min-height: 20px;
                color: #111827;
            }

            QLineEdit:focus,
            QTextEdit:focus,
            QComboBox:focus,
            QSpinBox:focus {
                border: 1px solid #2563EB;
                background: #FFFFFF;
            }

            QTextEdit {
                padding: 8px;
            }

            QComboBox {
                padding-right: 25px;
            }

            QComboBox QAbstractItemView {
                background: #FFFFFF;
                border: 1px solid #D1D5DB;
                selection-background-color: #EFF6FF;
                selection-color: #1D4ED8;
            }

            QSpinBox {
                padding-right: 5px;
            }

            /* =====================================================
            BOUTONS
            ===================================================== */

            QPushButton {
                min-height: 34px;
                padding: 7px 14px;
                border-radius: 7px;
                font-weight: 600;
                border: 1px solid #D1D5DB;
                background: #FFFFFF;
                color: #374151;
            }

            QPushButton:hover {
                background: #F9FAFB;
            }

            QPushButton:pressed {
                background: #F3F4F6;
            }

            #primaryButton {
                background: #2563EB;
                color: white;
                border: 1px solid #2563EB;
            }

            #primaryButton:hover {
                background: #1D4ED8;
                border-color: #1D4ED8;
            }

            #successButton {
                background: #16A34A;
                color: white;
                border: 1px solid #16A34A;
            }

            #successButton:hover {
                background: #15803D;
                border-color: #15803D;
            }

            #secondaryButton {
                background: #FFFFFF;
                color: #374151;
                border: 1px solid #D1D5DB;
            }

            #secondaryButton:hover {
                background: #F9FAFB;
                border-color: #9CA3AF;
            }

            #backButton {
                background: transparent;
                border: none;
                color: #4B5563;
                font-weight: 600;
            }

            #backButton:hover {
                background: #F3F4F6;
                color: #111827;
            }

            /* =====================================================
            INFORMATIONS PIÈCES
            ===================================================== */

            #pieceInfo {
                color: #6B7280;
                background: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                padding: 7px 10px;
            }

            #piecesTotalCard {
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 7px;
            }

            #piecesTotalLabel {
                color: #1D4ED8;
                font-size: 15px;
                font-weight: 700;
            }

            /* =====================================================
            TABLEAU
            ===================================================== */

            QTableWidget {
                background: #FFFFFF;
                alternate-background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 7px;
                gridline-color: #E5E7EB;
                selection-background-color: #EFF6FF;
                selection-color: #1D4ED8;
            }

            QTableWidget::item {
                padding: 8px;
                border: none;
            }

            QTableWidget::item:selected {
                background: #EFF6FF;
                color: #1D4ED8;
            }

            QHeaderView::section {
                background: #F8FAFC;
                color: #475569;
                border: none;
                border-bottom: 1px solid #E2E8F0;
                padding: 9px 8px;
                font-size: 11px;
                font-weight: 700;
            }

            /* =====================================================
            SCROLLBAR
            ===================================================== */

            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 3px;
            }

            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 4px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                height: 8px;
                background: transparent;
            }

            QScrollBar::handle:horizontal {
                background: #CBD5E1;
                border-radius: 4px;
            }
        """)

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

    def cancel_edit_mode(self):

        if not self.current_dossier:
            return

        # Recharger les valeurs originales du dossier
        self.load_detail_data()

        # Revenir au mode consultation
        self.set_edit_mode(False)

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
        # PIÈCES UTILISÉES
        # ========================================================

        self.load_pieces_utilisees()

        # ========================================================
        # STOCK POUR SÉLECTION
        # ========================================================

        self.load_stock()

        self.fill_piece_combo()

        # ========================================================
        # RESTAURER LE MODE ACTUEL
        # ========================================================

        self.set_edit_mode(
            self.edit_mode
        )

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
   
    def back_to_list(self):

        self.stack.setCurrentWidget(
            self.list_page
        )

        self.load_dossiers()

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

    def set_status_label(self, statut ):
    
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
  
    def fill_piece_combo(self):

        self.piece_combo.blockSignals(True)

        self.piece_combo.clear()

        self.piece_combo.addItem(
            "Sélectionner une pièce...",
            None
        )

        for stock in self.stocks:

            quantite = safe_int(
                stock.get("quantite")
            )

            # Ne jamais afficher une pièce épuisée
            #if quantite <= 0:
            #    continue

            nom = (
                stock.get("nom_piece")
                or "Pièce"
            )

            reference = (
                stock.get("reference")
                or "-"
            )

            text = (
                f"{nom} | "
                f"Réf: {reference} | "
                f"Stock actuel : {quantite}"
            )

            self.piece_combo.addItem(
                text,
                stock
            )

        self.piece_combo.blockSignals(False)

        # Réinitialisation de la quantité
        self.piece_quantity.setEnabled(False)
        self.piece_quantity.setMinimum(1)
        self.piece_quantity.setMaximum(100)
        self.piece_quantity.setValue(1)

        self.add_piece_button.setEnabled(False)

        self.piece_info_label.setText(
            "Sélectionnez une pièce."
        )

        self.piece_info_label.setStyleSheet("""
            color: #6B7280;
            padding: 3px;
        """)

        self.filter_stock(
            self.piece_search.text()
        )

        self.on_piece_selected()
   
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
    
    def on_piece_selected(self):

        stock = self.piece_combo.currentData()

        # ========================================================
        # AUCUNE PIÈCE SÉLECTIONNÉE
        # ========================================================

        if not isinstance(stock, dict):

            self.piece_info_label.setText(
                "Sélectionnez une pièce."
            )

            self.piece_info_label.setStyleSheet("""
                color: #6B7280;
                padding: 3px;
            """)

            self.piece_quantity.setEnabled(False)
            self.piece_quantity.setMinimum(1)
            self.piece_quantity.setMaximum(999999)
            self.piece_quantity.setValue(1)

            # IMPORTANT
            self.add_piece_button.setEnabled(False)

            return

        # ========================================================
        # PIÈCE VALIDE
        # ========================================================

        disponible = safe_int(
            stock.get("quantite")
        )

        prix = safe_float(
            stock.get("prix_unitaire")
        )

        # La quantité utilisée n'est pas limitée
        # par le stock disponible.
        self.piece_quantity.setEnabled(True)

        self.piece_quantity.setMinimum(1)
        self.piece_quantity.setMaximum(999999)

        if self.piece_quantity.value() < 1:
            self.piece_quantity.setValue(1)

        # IMPORTANT :
        # activer le bouton Ajouter
        self.add_piece_button.setEnabled(True)

        self.piece_info_label.setText(
            f"Stock actuel : {disponible}    |    "
            f"Prix unitaire : {format_money(prix)}"
        )

        self.piece_info_label.setStyleSheet("""
            color: #6B7280;
            padding: 3px;
        """)

    def add_piece(self):

        if not self.current_dossier:
            return

        # ========================================================
        # VÉRIFIER LA PIÈCE SÉLECTIONNÉE
        # ========================================================

        stock = self.piece_combo.currentData()

        if not isinstance(stock, dict):

            QMessageBox.warning(
                self,
                "Pièce",
                "Veuillez sélectionner une pièce."
            )

            return

        piece_id = stock.get("id")

        if not piece_id:

            QMessageBox.warning(
                self,
                "Pièce",
                "La pièce sélectionnée est invalide."
            )

            return

        # ========================================================
        # QUANTITÉ DEMANDÉE
        # ========================================================

        quantite = self.piece_quantity.value()

        if quantite < 1:

            QMessageBox.warning(
                self,
                "Quantité invalide",
                "La quantité doit être supérieure ou égale à 1."
            )

            return

        # ========================================================
        # RÉCUPÉRER LE STOCK ACTUEL
        # ========================================================

        try:

            response_stock = requests.get(
                f"{API_URL}/stock/",
                timeout=15
            )

            if not response_stock.ok:

                QMessageBox.warning(
                    self,
                    "Stock",
                    "Impossible de vérifier la pièce."
                )

                return

            stocks_actualises = response_stock.json()

            if not isinstance(
                stocks_actualises,
                list
            ):

                QMessageBox.warning(
                    self,
                    "Stock",
                    "Les données du stock reçues sont invalides."
                )

                return

            stock_actuel = None

            for item in stocks_actualises:

                if item.get("id") == piece_id:

                    stock_actuel = item
                    break

            # ====================================================
            # PIÈCE INTROUVABLE
            # ====================================================

            if not stock_actuel:

                QMessageBox.warning(
                    self,
                    "Pièce introuvable",
                    "Cette pièce n'existe plus dans le stock."
                )

                self.load_stock()
                self.fill_piece_combo()

                return

            # ====================================================
            # INFORMATIONS STOCK
            # ====================================================

            disponible = safe_int(
                stock_actuel.get("quantite")
            )

            prix = safe_float(
                stock_actuel.get("prix_unitaire")
            )

            # Mettre à jour les données locales
            stock.update(stock_actuel)

            # ====================================================
            # IMPORTANT :
            # ON NE BLOQUE PAS LA QUANTITÉ SELON LE STOCK
            # ====================================================
            #
            # Exemple :
            #
            # Stock actuel = 3
            # Quantité utilisée = 4
            #
            # => AUTORISÉ
            #
            # La quantité de la réparation représente la quantité
            # réellement utilisée dans cette réparation.
            # Elle n'est pas limitée par le stock actuel.
            #
            # ====================================================

            dossier_id = self.current_dossier.get(
                "id"
            )

            payload = {
                "piece_id": piece_id,
                "quantite": quantite
            }

            response = requests.post(
                f"{API_URL}/reparations/"
                f"{dossier_id}/pieces",
                json=payload,
                timeout=15
            )

            # ====================================================
            # ERREUR BACKEND
            # ====================================================

            if not response.ok:

                try:

                    error_data = response.json()

                    detail = error_data.get(
                        "detail"
                    )

                    if isinstance(detail, list):

                        messages = []

                        for error in detail:

                            if isinstance(error, dict):

                                msg = error.get(
                                    "msg",
                                    "Erreur de validation"
                                )

                                messages.append(
                                    str(msg)
                                )

                            else:

                                messages.append(
                                    str(error)
                                )

                        detail = "\n".join(
                            messages
                        )

                    elif isinstance(detail, dict):

                        detail = detail.get(
                            "message",
                            str(detail)
                        )

                    if not detail:
                        detail = response.text

                except Exception:

                    detail = response.text

                QMessageBox.warning(
                    self,
                    "Impossible d'ajouter la pièce",
                    f"{detail}"
                )

                self.load_stock()
                self.fill_piece_combo()

                return

            # ====================================================
            # SUCCÈS
            # ====================================================

            self.load_stock()
            self.load_pieces_utilisees()
            self.fill_piece_combo()

            QMessageBox.information(
                self,
                "Pièce ajoutée",
                f"La pièce a été ajoutée à la réparation.\n\n"
                f"Quantité utilisée : {quantite}\n"
                f"Stock actuel avant utilisation : {disponible}"
            )

        except requests.RequestException as error:

            QMessageBox.critical(
                self,
                "Erreur API",
                "Impossible de communiquer avec le serveur.\n\n"
                f"{error}"
            )

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
    
            self.display_pieces()
    