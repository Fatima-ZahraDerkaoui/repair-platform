import requests
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
    QWidget,
    QFileDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from views.pages.dossiers_utils import (
    API_URL,
    DEFAULT_UTILISATEUR_ID,
    safe_int,
    safe_float,
    format_date,
    format_money,
)


class DossierDetailMixin:

    def setup_detail_page(self):
        layout = QVBoxLayout(self.detail_page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Barre supérieure
        header = QHBoxLayout()
        self.back_button = QPushButton("← Retour aux dossiers")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self.back_to_list)

        header.addWidget(self.back_button)
        header.addStretch()

        self.pdf_button = QPushButton("📄 Fiche PDF")
        self.pdf_button.setCursor(Qt.PointingHandCursor)
        self.pdf_button.clicked.connect(self.download_pdf)
        header.addWidget(self.pdf_button)

        layout.addLayout(header)

        # Zone Scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        content = QVBoxLayout(container)
        content.setContentsMargins(4, 4, 8, 20)
        content.setSpacing(16)

        # Card En-tête Dossier
        header_card = QFrame()
        header_card.setObjectName("detailHeaderCard")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(20, 16, 20, 16)

        left = QVBoxLayout()
        d_title = QLabel("DOSSIER DE RÉPARATION")
        d_title.setObjectName("detailOverline")
        left.addWidget(d_title)

        self.detail_numero = QLabel()
        self.detail_numero.setObjectName("detailNumero")
        left.addWidget(self.detail_numero)

        self.detail_date = QLabel()
        self.detail_date.setObjectName("detailDate")
        left.addWidget(self.detail_date)
        header_layout.addLayout(left)
        header_layout.addStretch()

        status_container = QVBoxLayout()
        st_title = QLabel("STATUT ACTUEL")
        st_title.setObjectName("detailStatusTitle")
        st_title.setAlignment(Qt.AlignCenter)
        status_container.addWidget(st_title)

        self.detail_status_label = QLabel()
        self.detail_status_label.setObjectName("detailStatus")
        self.detail_status_label.setAlignment(Qt.AlignCenter)
        self.detail_status_label.setMinimumWidth(160)
        status_container.addWidget(self.detail_status_label)
        header_layout.addLayout(status_container)

        content.addWidget(header_card)

        # 01. Client
        client_group = QGroupBox("01. Informations Client")
        client_layout = QGridLayout(client_group)
        client_layout.setContentsMargins(16, 20, 16, 16)
        client_layout.setHorizontalSpacing(16)

        self.client_nom = self.create_info_label()
        self.client_tel = self.create_info_label()
        self.client_email = self.create_info_label()

        self.edit_client_nom = QLineEdit()
        self.edit_client_tel = QLineEdit()
        self.edit_client_email = QLineEdit()

        fields_c = [
            ("Nom complet", self.client_nom, self.edit_client_nom),
            ("Téléphone", self.client_tel, self.edit_client_tel),
            ("Email", self.client_email, self.edit_client_email),
        ]
        for row, (lbl, view, edit) in enumerate(fields_c):
            f_lbl = QLabel(lbl)
            f_lbl.setObjectName("fieldLabel")
            client_layout.addWidget(f_lbl, row, 0)
            client_layout.addWidget(view, row, 1)
            client_layout.addWidget(edit, row, 1)

        content.addWidget(client_group)

        # 02. Matériel
        machine_group = QGroupBox("02. Matériel & Spécifications")
        machine_layout = QGridLayout(machine_group)
        machine_layout.setContentsMargins(16, 20, 16, 16)
        machine_layout.setHorizontalSpacing(16)

        self.machine_type = self.create_info_label()
        self.machine_marque = self.create_info_label()
        self.machine_modele = self.create_info_label()
        self.machine_serie = self.create_info_label()

        self.edit_machine_type = QLineEdit()
        self.edit_machine_marque = QLineEdit()
        self.edit_machine_modele = QLineEdit()
        self.edit_machine_serie = QLineEdit()

        fields_m = [
            ("Type matériel", self.machine_type, self.edit_machine_type),
            ("Marque", self.machine_marque, self.edit_machine_marque),
            ("Modèle", self.machine_modele, self.edit_machine_modele),
            ("N° de Série", self.machine_serie, self.edit_machine_serie),
        ]
        for row, (lbl, view, edit) in enumerate(fields_m):
            f_lbl = QLabel(lbl)
            f_lbl.setObjectName("fieldLabel")
            machine_layout.addWidget(f_lbl, row, 0)
            machine_layout.addWidget(view, row, 1)
            machine_layout.addWidget(edit, row, 1)

        content.addWidget(machine_group)

        # 03. Diagnostic & Intervention
        problem_group = QGroupBox("03. Diagnostic & Rapport Technique")
        problem_layout = QGridLayout(problem_group)
        problem_layout.setContentsMargins(16, 20, 16, 16)
        problem_layout.setHorizontalSpacing(16)

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

        for t in [self.probleme_edit, self.diagnostic_edit, self.intervention_edit, self.pieces_defectueuses_edit, self.remarques_edit]:
            t.setMinimumHeight(65)
            t.setMaximumHeight(100)

        fields_p = [
            ("Problème signalé", self.probleme_view, self.probleme_edit),
            ("Diagnostic technique", self.diagnostic_view, self.diagnostic_edit),
            ("Intervention effectuée", self.intervention_view, self.intervention_edit),
            ("Pièces défectueuses", self.pieces_defectueuses_view, self.pieces_defectueuses_edit),
            ("Remarques", self.remarques_view, self.remarques_edit),
        ]
        for row, (lbl, view, edit) in enumerate(fields_p):
            f_lbl = QLabel(lbl)
            f_lbl.setObjectName("fieldLabel")
            f_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            problem_layout.addWidget(f_lbl, row, 0)
            problem_layout.addWidget(view, row, 1)
            problem_layout.addWidget(edit, row, 1)

        content.addWidget(problem_group)

        # 04. Statut
        status_group = QGroupBox("04. Statut du Dossier")
        status_layout = QHBoxLayout(status_group)
        status_layout.setContentsMargins(16, 16, 16, 16)

        st_lbl = QLabel("Changer le statut :")
        st_lbl.setObjectName("fieldLabel")
        status_layout.addWidget(st_lbl)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["En attente", "En diagnostic", "En réparation", "Terminé"])
        self.status_combo.setMinimumWidth(220)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()

        content.addWidget(status_group)

        # 05. Pièces utilisées
        pieces_group = QGroupBox("05. Gestion des Pièces et Composants")
        pieces_layout = QVBoxLayout(pieces_group)
        pieces_layout.setContentsMargins(16, 20, 16, 16)

        self.pieces_edit_controls = QWidget()
        edit_p_layout = QVBoxLayout(self.pieces_edit_controls)
        edit_p_layout.setContentsMargins(0, 0, 0, 8)

        s_layout = QHBoxLayout()
        s_lbl = QLabel("Rechercher pièce :")
        s_lbl.setObjectName("fieldLabel")
        s_layout.addWidget(s_lbl)

        self.piece_search = QLineEdit()
        self.piece_search.setPlaceholderText("Nom, référence, catégorie...")
        self.piece_search.textChanged.connect(self.filter_stock)
        s_layout.addWidget(self.piece_search, 1)
        edit_p_layout.addLayout(s_layout)

        sel_layout = QHBoxLayout()
        p_lbl = QLabel("Pièce :")
        p_lbl.setObjectName("fieldLabel")
        sel_layout.addWidget(p_lbl)

        self.piece_combo = QComboBox()
        self.piece_combo.currentIndexChanged.connect(self.on_piece_selected)
        sel_layout.addWidget(self.piece_combo, 1)

        q_lbl = QLabel("Qté :")
        q_lbl.setObjectName("fieldLabel")
        sel_layout.addWidget(q_lbl)

        self.piece_quantity = QSpinBox()
        self.piece_quantity.setRange(1, 100)
        self.piece_quantity.setValue(1)
        sel_layout.addWidget(self.piece_quantity)

        self.add_piece_button = QPushButton("+ Ajouter")
        self.add_piece_button.setObjectName("successButton")
        self.add_piece_button.setCursor(Qt.PointingHandCursor)
        self.add_piece_button.clicked.connect(self.add_piece)
        sel_layout.addWidget(self.add_piece_button)

        edit_p_layout.addLayout(sel_layout)

        self.piece_info_label = QLabel("Sélectionnez une pièce pour voir son stock.")
        self.piece_info_label.setObjectName("pieceInfo")
        edit_p_layout.addWidget(self.piece_info_label)

        pieces_layout.addWidget(self.pieces_edit_controls)

        # Tableau des pièces
        self.pieces_table = QTableWidget()
        self.pieces_table.setColumnCount(6)
        self.pieces_table.setHorizontalHeaderLabels(["Pièce", "Référence", "Qté", "Prix unit.", "Total", "Action"])
        self.pieces_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pieces_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pieces_table.setAlternatingRowColors(True)
        self.pieces_table.verticalHeader().setVisible(False)
        self.pieces_table.setMinimumHeight(160)

        p_hdr = self.pieces_table.horizontalHeader()
        p_hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        p_hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        for c in [2, 3, 4, 5]:
            p_hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)

        pieces_layout.addWidget(self.pieces_table)

        total_card = QFrame()
        total_card.setObjectName("piecesTotalCard")
        tot_l = QHBoxLayout(total_card)
        tot_l.setContentsMargins(14, 8, 14, 8)
        tot_l.addStretch()

        self.pieces_total_label = QLabel("Total pièces : 0.00 DH")
        self.pieces_total_label.setObjectName("piecesTotalLabel")
        tot_l.addWidget(self.pieces_total_label)

        pieces_layout.addWidget(total_card)
        content.addWidget(pieces_group)

        # =========================================================
        # 06. REDESIGN : IA & ESTIMATION FINANCIÈRE
        # =========================================================
        est_group = QGroupBox("06. Estimation Financière & Intelligence Artificielle")
        est_group.setObjectName("aiGroupBox")
        est_main_layout = QVBoxLayout(est_group)
        est_main_layout.setContentsMargins(20, 20, 20, 20)
        est_main_layout.setSpacing(16)

        # Bouton d'estimation IA Premium
        self.btn_predict_cost = QPushButton("✨ Lancer l'Estimation Automatique (IA Machine Learning)")
        self.btn_predict_cost.setObjectName("aiButton")
        self.btn_predict_cost.setCursor(Qt.PointingHandCursor)
        self.btn_predict_cost.clicked.connect(self.predict_and_apply_cost)
        est_main_layout.addWidget(self.btn_predict_cost)

        # Grille de cartes d'affichage des prédictions
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        # 1. Carte Coût Estimé
        cost_card = QFrame()
        cost_card.setObjectName("metricCard")
        cc_layout = QVBoxLayout(cost_card)
        cc_layout.setContentsMargins(16, 14, 16, 14)

        lbl_c_title = QLabel("COÛT ESTIMÉ (IA)")
        lbl_c_title.setObjectName("metricTitle")
        cc_layout.addWidget(lbl_c_title)

        self.cout_estime_label = QLabel("0.00 DH")
        self.cout_estime_label.setObjectName("metricValueBlue")
        cc_layout.addWidget(self.cout_estime_label)

        self.edit_cout_estime = QLineEdit()
        self.edit_cout_estime.setPlaceholderText("Ex: 150.00")
        cc_layout.addWidget(self.edit_cout_estime)

        cards_layout.addWidget(cost_card)

        # 2. Carte Délai Estimé
        delay_card = QFrame()
        delay_card.setObjectName("metricCard")
        dc_layout = QVBoxLayout(delay_card)
        dc_layout.setContentsMargins(16, 14, 16, 14)

        lbl_d_title = QLabel("DÉLAI ESTIMÉ (IA)")
        lbl_d_title.setObjectName("metricTitle")
        dc_layout.addWidget(lbl_d_title)

        self.delai_label = QLabel("- Jour(s)")
        self.delai_label.setObjectName("metricValuePurple")
        dc_layout.addWidget(self.delai_label)

        cards_layout.addWidget(delay_card)

        # 3. Carte Coût Réel (Facturé)
        real_card = QFrame()
        real_card.setObjectName("metricCard")
        rc_layout = QVBoxLayout(real_card)
        rc_layout.setContentsMargins(16, 14, 16, 14)

        lbl_r_title = QLabel("COÛT RÉEL (FACTURÉ)")
        lbl_r_title.setObjectName("metricTitle")
        rc_layout.addWidget(lbl_r_title)

        self.cout_reel_label = QLabel("0.00 DH")
        self.cout_reel_label.setObjectName("metricValueGreen")
        rc_layout.addWidget(self.cout_reel_label)

        self.edit_cout_reel = QLineEdit()
        self.edit_cout_reel.setPlaceholderText("Ex: 200.00")
        rc_layout.addWidget(self.edit_cout_reel)

        cards_layout.addWidget(real_card)

        est_main_layout.addLayout(cards_layout)
        content.addWidget(est_group)

        # Actions de validation
        actions_card = QFrame()
        actions_card.setObjectName("actionsCard")
        actions_layout = QHBoxLayout(actions_card)
        actions_layout.setContentsMargins(14, 10, 14, 10)
        actions_layout.addStretch()

        self.edit_detail_button = QPushButton("✎ Modifier le dossier")
        self.edit_detail_button.setObjectName("primaryButton")
        self.edit_detail_button.setCursor(Qt.PointingHandCursor)
        self.edit_detail_button.clicked.connect(self.enter_edit_mode)
        actions_layout.addWidget(self.edit_detail_button)

        self.cancel_edit_button = QPushButton("Annuler")
        self.cancel_edit_button.setCursor(Qt.PointingHandCursor)
        self.cancel_edit_button.clicked.connect(self.cancel_edit_mode)
        actions_layout.addWidget(self.cancel_edit_button)

        self.save_detail_button = QPushButton("✓ Enregistrer")
        self.save_detail_button.setObjectName("primaryButton")
        self.save_detail_button.setCursor(Qt.PointingHandCursor)
        self.save_detail_button.clicked.connect(self.save_dossier)
        actions_layout.addWidget(self.save_detail_button)

        content.addWidget(actions_card)

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        self._apply_detail_styles()
        self.set_edit_mode(False)

    def _apply_detail_styles(self):
        self.detail_page.setStyleSheet("""
            #detailHeaderCard, #actionsCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
            #detailOverline { color: #64748B; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; }
            #detailNumero { color: #0F172A; font-size: 24px; font-weight: 800; }
            #detailDate { color: #64748B; font-size: 12px; }
            #detailStatusTitle { color: #64748B; font-size: 10px; font-weight: 700; }
            #detailStatus { font-weight: 700; font-size: 12px; }
            #fieldLabel { color: #475569; font-size: 12px; font-weight: 600; }
            #pieceInfo { color: #475569; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 10px; }
            #piecesTotalCard { background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 8px; }
            #piecesTotalLabel { color: #1E40AF; font-size: 15px; font-weight: 800; }
            
            /* BOUTON IA MODERNE GRADIENT */
            QPushButton#aiButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #2563EB);
                color: #FFFFFF;
                font-weight: 700;
                font-size: 13px;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }
            QPushButton#aiButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338CA, stop:1 #1D4ED8);
            }

            /* CARTES DE DÉTAIL FINANCIER */
            QFrame#metricCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
            QLabel#metricTitle {
                color: #64748B;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QLabel#metricValueBlue {
                color: #2563EB;
                font-size: 20px;
                font-weight: 800;
            }
            QLabel#metricValuePurple {
                color: #7C3AED;
                font-size: 20px;
                font-weight: 800;
            }
            QLabel#metricValueGreen {
                color: #16A34A;
                font-size: 20px;
                font-weight: 800;
            }

            /* Bouton Supprimer Pièce */
            #deletePieceButton {
                background-color: #FEF2F2;
                color: #DC2626;
                border: 1px solid #FECACA;
                border-radius: 6px;
                font-weight: 700;
                font-size: 11px;
                padding: 4px 10px;
            }
            #deletePieceButton:hover {
                background-color: #FEE2E2;
                color: #B91C1C;
            }
        """)

    def set_edit_mode(self, enabled):
        self.edit_mode = enabled

        for view, edit in [
            (self.client_nom, self.edit_client_nom), (self.client_tel, self.edit_client_tel), (self.client_email, self.edit_client_email),
            (self.machine_type, self.edit_machine_type), (self.machine_marque, self.edit_machine_marque),
            (self.machine_modele, self.edit_machine_modele), (self.machine_serie, self.edit_machine_serie),
            (self.probleme_view, self.probleme_edit), (self.diagnostic_view, self.diagnostic_edit),
            (self.intervention_view, self.intervention_edit), (self.pieces_defectueuses_view, self.pieces_defectueuses_edit),
            (self.remarques_view, self.remarques_edit), (self.cout_estime_label, self.edit_cout_estime),
            (self.cout_reel_label, self.edit_cout_reel)
        ]:
            view.setVisible(not enabled)
            edit.setVisible(enabled)

        self.status_combo.setVisible(enabled)
        self.pieces_edit_controls.setVisible(enabled)
        self.pieces_table.setColumnHidden(5, not enabled)

        self.edit_detail_button.setVisible(not enabled)
        self.cancel_edit_button.setVisible(enabled)
        self.save_detail_button.setVisible(enabled)

        if hasattr(self, "pieces_utilisees"):
            self.display_pieces()

    def enter_edit_mode(self):
        if not self.current_dossier:
            return
        d = self.current_dossier
        c = d.get("client") if isinstance(d.get("client"), dict) else {}

        self.edit_client_nom.setText(str(c.get("nom", d.get("client_nom", "")) or ""))
        self.edit_client_tel.setText(str(c.get("telephone", d.get("client_telephone", "")) or ""))
        self.edit_client_email.setText(str(c.get("email", "") or ""))

        self.edit_machine_type.setText(str(d.get("type_materiel", "") or ""))
        self.edit_machine_marque.setText(str(d.get("marque", "") or ""))
        self.edit_machine_modele.setText(str(d.get("modele", "") or ""))
        self.edit_machine_serie.setText(str(d.get("numero_serie", "") or ""))

        self.probleme_edit.setPlainText(str(d.get("probleme", "") or ""))
        self.diagnostic_edit.setPlainText(str(d.get("diagnostic", "") or ""))
        self.intervention_edit.setPlainText(str(d.get("intervention", "") or ""))
        self.pieces_defectueuses_edit.setPlainText(str(d.get("pieces_defectueuses", "") or ""))
        self.remarques_edit.setPlainText(str(d.get("remarques", "") or ""))

        ce = d.get("cout_estime")
        cr = d.get("cout_reel")
        self.edit_cout_estime.setText(str(ce) if ce is not None else "")
        self.edit_cout_reel.setText(str(cr) if cr is not None else "")

        idx = self.status_combo.findText(str(d.get("statut", "")))
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

        self.set_edit_mode(True)
        self.load_stock()
        self.fill_piece_combo()
        self.load_pieces_utilisees()

    def cancel_edit_mode(self):
        self.set_edit_mode(False)
        self.load_detail_data()

    def load_detail_data(self):
        d = self.current_dossier
        if not d:
            return

        self.detail_numero.setText(d.get("numero_dossier") or f"Dossier #{d.get('id')}")
        self.detail_date.setText("Réception : " + format_date(d.get("date_reception")))
        self.set_status_label(d.get("statut"))

        c = d.get("client") if isinstance(d.get("client"), dict) else {}
        nom = str(c.get("nom") or d.get("client_nom") or "-")
        tel = str(c.get("telephone") or d.get("client_telephone") or "-")
        email = str(c.get("email") or "-")

        self.client_nom.setText(nom)
        self.client_tel.setText(tel)
        self.client_email.setText(email)

        self.machine_type.setText(str(d.get("type_materiel") or "-"))
        self.machine_marque.setText(str(d.get("marque") or "-"))
        self.machine_modele.setText(str(d.get("modele") or "-"))
        self.machine_serie.setText(str(d.get("numero_serie") or "-"))

        self.probleme_view.setText(str(d.get("probleme") or "-"))
        self.diagnostic_view.setText(str(d.get("diagnostic") or "-"))
        self.intervention_view.setText(str(d.get("intervention") or "-"))
        self.pieces_defectueuses_view.setText(str(d.get("pieces_defectueuses") or "-"))
        self.remarques_view.setText(str(d.get("remarques") or "-"))

        delai = d.get("delai_estime")
        self.delai_label.setText(f"{delai} jour(s)" if delai is not None else "-")

        ce = d.get("cout_estime")
        cr = d.get("cout_reel")
        self.cout_estime_label.setText(format_money(ce))
        self.cout_reel_label.setText(format_money(cr))

        self.load_pieces_utilisees()
        self.load_stock()
        self.fill_piece_combo()
        self.set_edit_mode(self.edit_mode)

    def refresh_current_dossier(self):
        if not self.current_dossier:
            return
        d_id = self.current_dossier.get("id")
        try:
            response = requests.get(f"{API_URL}/reparations/{d_id}", timeout=15)
            response.raise_for_status()
            self.current_dossier = response.json()
            self.load_detail_data()
        except requests.RequestException as error:
            QMessageBox.warning(self, "Erreur", f"Impossible d'actualiser le dossier :\n{error}")

    def back_to_list(self):
        self.stack.setCurrentWidget(self.list_page)
        self.load_dossiers()

    def save_dossier(self):
        if not self.current_dossier:
            return
        d_id = self.current_dossier.get("id")

        ce_str = self.edit_cout_estime.text().replace("DH", "").strip()
        cr_str = self.edit_cout_reel.text().replace("DH", "").strip()
        ce_val = safe_float(ce_str, None) if ce_str else None
        cr_val = safe_float(cr_str, None) if cr_str else None

        payload = {
            "client_nom": self.edit_client_nom.text().strip(),
            "client_telephone": self.edit_client_tel.text().strip(),
            "client_email": self.edit_client_email.text().strip(),
            "type_materiel": self.edit_machine_type.text().strip(),
            "marque": self.edit_machine_marque.text().strip(),
            "modele": self.edit_machine_modele.text().strip(),
            "numero_serie": self.edit_machine_serie.text().strip(),
            "probleme": self.probleme_edit.toPlainText().strip() or None,
            "diagnostic": self.diagnostic_edit.toPlainText().strip() or None,
            "intervention": self.intervention_edit.toPlainText().strip() or None,
            "pieces_defectueuses": self.pieces_defectueuses_edit.toPlainText().strip() or None,
            "remarques": self.remarques_edit.toPlainText().strip() or None,
            "statut": self.status_combo.currentText(),
            "cout_estime": ce_val,
            "cout_reel": cr_val
        }

        try:
            response = requests.patch(f"{API_URL}/reparations/{d_id}", json=payload, timeout=15)
            if not response.ok:
                detail = response.json().get("detail", response.text) if response.headers.get("content-type") == "application/json" else response.text
                QMessageBox.warning(self, "Erreur", f"Échec de sauvegarde :\n{detail}")
                return

            self.current_dossier = response.json() if isinstance(response.json(), dict) else self.current_dossier
            self.set_edit_mode(False)
            self.load_detail_data()
            self.load_dossiers()
            self.status_changed.emit()
            QMessageBox.information(self, "Succès", "Dossier mis à jour avec succès.")
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur API", f"Impossible de contacter le serveur :\n{error}")

    def download_pdf(self):
        if not self.current_dossier:
            return
        d_id = self.current_dossier.get("id")
        num = self.current_dossier.get("numero_dossier") or f"dossier_{d_id}"

        try:
            response = requests.get(f"{API_URL}/reparations/{d_id}/fiche", timeout=30)
            if not response.ok:
                QMessageBox.warning(self, "Erreur PDF", "Génération du PDF impossible.")
                return

            path, _ = QFileDialog.getSaveFileName(self, "Enregistrer la fiche PDF", f"{num}.pdf", "Fichier PDF (*.pdf)")
            if not path:
                return

            with open(path, "wb") as f:
                f.write(response.content)

            QMessageBox.information(self, "PDF Généré", f"Fiche PDF enregistrée dans :\n{path}")
        except Exception as error:
            QMessageBox.critical(self, "Erreur", f"Échec de l'export PDF :\n{error}")

    def set_status_label(self, statut):
        statut = str(statut or "-")
        self.detail_status_label.setText(statut)
        colors = {
            "En attente": ("#FEF3C7", "#92400E"),
            "En diagnostic": ("#E0F2FE", "#0369A1"),
            "En réparation": ("#F3E8FF", "#6B21A8"),
            "Terminé": ("#DCFCE7", "#15803D")
        }
        bg, fg = colors.get(statut, ("#F1F5F9", "#475569"))
        self.detail_status_label.setStyleSheet(f"background: {bg}; color: {fg}; border-radius: 20px; padding: 6px 14px; font-weight: 700;")

    def fill_piece_combo(self):
        self.piece_combo.blockSignals(True)
        self.piece_combo.clear()
        self.piece_combo.addItem("Sélectionner une pièce...", None)

        for stock in self.stocks:
            q = safe_int(stock.get("quantite"))
            nom = stock.get("nom_piece") or "Pièce"
            ref = stock.get("reference") or "-"
            self.piece_combo.addItem(f"{nom} | Réf: {ref} | Stock: {q}", stock)

        self.piece_combo.blockSignals(False)
        self.piece_quantity.setEnabled(False)
        self.add_piece_button.setEnabled(False)
        self.piece_info_label.setText("Sélectionnez une pièce.")
        self.filter_stock(self.piece_search.text())

    def filter_stock(self, text=""):
        search = text.strip().lower()
        for idx in range(self.piece_combo.count()):
            stock = self.piece_combo.itemData(idx)
            if not stock:
                self.piece_combo.view().setRowHidden(idx, False)
                continue
            searchable = f"{stock.get('nom_piece', '')} {stock.get('reference', '')} {stock.get('categorie', '')}".lower()
            self.piece_combo.view().setRowHidden(idx, search not in searchable)

    def on_piece_selected(self):
        stock = self.piece_combo.currentData()
        if not isinstance(stock, dict):
            self.piece_info_label.setText("Sélectionnez une pièce.")
            self.piece_quantity.setEnabled(False)
            self.add_piece_button.setEnabled(False)
            return

        q = safe_int(stock.get("quantite"))
        p = safe_float(stock.get("prix_unitaire"))

        self.piece_quantity.setEnabled(True)
        self.add_piece_button.setEnabled(True)
        self.piece_info_label.setText(f"Stock disponible : {q} | Prix unitaire : {format_money(p)}")

    def add_piece(self):
        if not self.current_dossier:
            return
        stock = self.piece_combo.currentData()
        if not isinstance(stock, dict):
            return

        p_id = stock.get("id")
        q_val = self.piece_quantity.value()
        d_id = self.current_dossier.get("id")

        try:
            response = requests.post(
                f"{API_URL}/reparations/{d_id}/pieces",
                json={"piece_id": p_id, "quantite": q_val},
                timeout=15
            )
            if not response.ok:
                detail = response.json().get("detail", response.text) if response.headers.get("content-type") == "application/json" else response.text
                QMessageBox.warning(self, "Erreur Stock", f"Impossible d'ajouter la pièce :\n{detail}")
                return

            self.load_stock()
            self.load_pieces_utilisees()
            self.fill_piece_combo()
            QMessageBox.information(self, "Succès", "Pièce ajoutée au dossier avec succès.")
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur API", f"Impossible de contacter le serveur :\n{error}")

    def load_pieces_utilisees(self):
        if not self.current_dossier:
            return
        d_id = self.current_dossier.get("id")
        try:
            response = requests.get(f"{API_URL}/reparations/{d_id}/pieces", timeout=15)
            response.raise_for_status()
            self.pieces_utilisees = response.json() if isinstance(response.json(), list) else []
            self.display_pieces()
        except requests.RequestException as error:
            print("[DOSSIERS] Erreur pièces utilisées :", error)
            self.pieces_utilisees = []
            self.display_pieces()

    def display_pieces(self):
        self.pieces_table.setRowCount(0)
        total_gen = 0.0

        for pu in self.pieces_utilisees:
            pu_id = pu.get("id")
            if not pu_id:
                continue
            p_info = pu.get("piece") or {}
            nom = p_info.get("nom_piece", "Pièce")
            ref = p_info.get("reference", "-")
            q = safe_float(pu.get("quantite"))
            px = safe_float(pu.get("prix_utilise"))
            tot = q * px
            total_gen += tot

            row = self.pieces_table.rowCount()
            self.pieces_table.insertRow(row)

            self.pieces_table.setItem(row, 0, QTableWidgetItem(str(nom)))
            self.pieces_table.setItem(row, 1, QTableWidgetItem(str(ref)))
            self.pieces_table.setItem(row, 2, QTableWidgetItem(str(int(q) if q.is_integer() else q)))
            self.pieces_table.setItem(row, 3, QTableWidgetItem(f"{px:.2f} DH"))
            self.pieces_table.setItem(row, 4, QTableWidgetItem(f"{tot:.2f} DH"))

            del_btn = QPushButton("✕ Supprimer")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setVisible(self.edit_mode)
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FEF2F2;
                    color: #DC2626;
                    border: 1px solid #FECACA;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 8px;
                    padding: 0px 8px;
                    min-height: 12px;
                }
                QPushButton:hover {
                    background-color: #FEE2E2;
                    color: #B91C1C;
                }
            """)
            del_btn.clicked.connect(lambda checked=False, pid=pu_id: self.remove_piece_from_edit(pid))
            self.pieces_table.setCellWidget(row, 5, del_btn)

        self.pieces_total_label.setText(f"Total pièces : {total_gen:.2f} DH")

    def remove_piece_from_edit(self, pu_id):
        if not self.current_dossier:
            return
        d_id = self.current_dossier.get("id")

        reply = QMessageBox.question(
            self,
            "Retrait de la pièce",
            "Voulez-vous retirer cette pièce du dossier ? La quantité sera réintégrée en stock.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            response = requests.delete(f"{API_URL}/reparations/{d_id}/pieces/{pu_id}", timeout=15)
            if not response.ok:
                detail = response.json().get("detail", response.text) if response.headers.get("content-type") == "application/json" else response.text
                QMessageBox.warning(self, "Erreur", f"Échec de la suppression :\n{detail}")
                return

            self.load_pieces_utilisees()
            self.load_stock()
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur réseau", f"Impossible de contacter le serveur :\n{error}")

    def predict_and_apply_cost(self):
        if getattr(self, "edit_mode", False):
            mat = self.edit_machine_type.text().strip()
            prob = self.probleme_edit.toPlainText().strip()
        else:
            d = self.current_dossier or {}
            mat = str(d.get("type_materiel") or "").strip()
            prob = str(d.get("probleme") or "").strip()

        if not mat or not prob:
            QMessageBox.warning(
                self, 
                "Informations requises", 
                "Le matériel et le problème doivent être renseignés pour faire une prédiction."
            )
            return

        # Appel au service ML
        result = self.predict_cost(mat, prob)
        if not result or not isinstance(result, dict):
            QMessageBox.warning(
                self, 
                "Échec IA", 
                "Le service d'estimation n'a pas renvoyé de réponse valide."
            )
            return

        cost = result.get("cout_estime")
        delay = result.get("delai_estime")

        if cost is None:
            QMessageBox.warning(self, "Format invalide", f"Réponse IA incomprise :\n{result}")
            return

        # Mise à jour des cartes
        self.cout_estime_label.setText(format_money(cost))
        self.edit_cout_estime.setText(str(cost))

        if delay is not None:
            self.delai_label.setText(f"{delay} jour(s)")

        # Persistance en BD
        if self.current_dossier:
            self.current_dossier["cout_estime"] = cost
            if delay is not None:
                self.current_dossier["delai_estime"] = delay

            d_id = self.current_dossier.get("id")
            if d_id:
                try:
                    requests.patch(
                        f"{API_URL}/reparations/{d_id}",
                        json={"cout_estime": cost, "delai_estime": delay},
                        timeout=10
                    )
                except requests.RequestException as err:
                    print("[DOSSIER] Avertissement: échec d'enregistrement auto:", err)

        msg = f"Coût estimé (IA) : {format_money(cost)}"
        if delay is not None:
            msg += f"\nDélai estimé (IA) : {delay} jour(s)"
            
        QMessageBox.information(self, "Estimation IA Réussie", msg)
        