from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QComboBox,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSizePolicy,
    QMessageBox,
    QLineEdit
)

from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QDate
)

from PySide6.QtGui import QFont

from PySide6.QtCharts import (
    QChart,
    QChartView,
    QLineSeries,
    QBarSeries,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis,
    QPieSeries
)

from services.backend_api import BackendAPI


# ============================================================
# WORKER DASHBOARD
# ============================================================

class DashboardWorker(QThread):

    result_ready = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, periode="30j", parent=None):

        super().__init__(parent)

        self.periode = periode

    def run(self):

        try:

            # ==================================================
            # APPEL BACKEND
            # ==================================================

            try:

                data = BackendAPI.get_dashboard_stats(
                    periode=self.periode
                )

            except TypeError:

                # Compatibilité avec une ancienne version
                # de BackendAPI sans paramètre periode

                data = BackendAPI.get_dashboard_stats()

            # ==================================================
            # VERIFICATION
            # ==================================================

            if not isinstance(data, dict):

                raise Exception(
                    "Réponse dashboard invalide."
                )

            self.result_ready.emit(data)

        except Exception as error:

            self.error_occurred.emit(
                str(error)
            )


# ============================================================
# DASHBOARD
# ============================================================

class MenuPrincipal(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.worker = None

        self.dashboard_data = {}

        self.stat_labels = {}

        self.init_ui()

        self.load_statistics()


    # =========================================================
    # UI PRINCIPALE
    # =========================================================

    def init_ui(self):

        # =====================================================
        # SCROLL
        # =====================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()

        scroll.setWidget(
            content
        )

        main_layout = QVBoxLayout(
            content
        )

        main_layout.setContentsMargins(
            30,
            25,
            30,
            30
        )

        main_layout.setSpacing(
            20
        )

        # =====================================================
        # HEADER
        # =====================================================

        header_layout = QHBoxLayout()

        header_left = QVBoxLayout()

        titre = QLabel(
            "Tableau de bord"
        )

        titre.setStyleSheet("""
            QLabel {
                font-size: 30px;
                font-weight: 700;
                color: #111827;
            }
        """)

        header_left.addWidget(
            titre
        )

        sous_titre = QLabel(
            "Vue générale de l'activité de Repair Platform"
        )

        sous_titre.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6b7280;
            }
        """)

        header_left.addWidget(
            sous_titre
        )

        header_layout.addLayout(
            header_left
        )

        header_layout.addStretch()

        # =====================================================
        # PERIODE
        # =====================================================

        periode_label = QLabel(
            "Période :"
        )

        periode_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #374151;
                font-weight: 600;
            }
        """)

        header_layout.addWidget(
            periode_label
        )

        self.periode_combo = QComboBox()

        self.periode_combo.addItem(
            "7 derniers jours",
            "7j"
        )

        self.periode_combo.addItem(
            "30 derniers jours",
            "30j"
        )

        self.periode_combo.addItem(
            "90 derniers jours",
            "90j"
        )

        self.periode_combo.addItem(
            "Cette année",
            "1an"
        )

        self.periode_combo.setCurrentIndex(
            1
        )

        self.periode_combo.setMinimumWidth(
            160
        )

        self.periode_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                color: #111827;
                font-size: 13px;
            }

            QComboBox:hover {
                border: 1px solid #9ca3af;
            }

            QComboBox::drop-down {
                border: none;
            }
        """)

        self.periode_combo.currentIndexChanged.connect(
            self.on_period_changed
        )

        header_layout.addWidget(
            self.periode_combo
        )

        # =====================================================
        # BOUTON ACTUALISER
        # =====================================================

        refresh_button = QPushButton(
            "↻  Actualiser"
        )

        refresh_button.setCursor(
            Qt.PointingHandCursor
        )

        refresh_button.setMinimumHeight(
            38
        )

        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #111827;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1f2937;
            }

            QPushButton:pressed {
                background-color: #374151;
            }

            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)

        refresh_button.clicked.connect(
            self.refresh
        )

        self.refresh_button = refresh_button

        header_layout.addWidget(
            refresh_button
        )

        main_layout.addLayout(
            header_layout
        )

        # =====================================================
        # STATUS
        # =====================================================

        self.status_label = QLabel(
            "Chargement des statistiques..."
        )

        self.status_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 12px;
            }
        """)

        main_layout.addWidget(
            self.status_label
        )

        # =====================================================
        # CARTES KPI
        # =====================================================

        stats_layout = QGridLayout()

        stats_layout.setSpacing(
            15
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Réparations",
                "0",
                "🔧",
                "reparations"
            ),
            0,
            0
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Factures",
                "0",
                "🧾",
                "factures"
            ),
            0,
            1
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Stock",
                "0",
                "📦",
                "stock"
            ),
            0,
            2
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Dossiers ouverts",
                "0",
                "📂",
                "dossiers_ouverts"
            ),
            0,
            3
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Clients",
                "0",
                "👥",
                "clients"
            ),
            1,
            0
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "CA TTC",
                "0 DH",
                "💰",
                "ca_ttc"
            ),
            1,
            1
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Réparations terminées",
                "0",
                "✓",
                "reparations_terminees"
            ),
            1,
            2
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Stock faible",
                "0",
                "⚠",
                "stock_faible"
            ),
            1,
            3
        )

        main_layout.addLayout(
            stats_layout
        )

        # =====================================================
        # GRAPHIQUES
        # =====================================================

        charts_layout = QHBoxLayout()

        charts_layout.setSpacing(
            15
        )

        # -----------------------------------------------------
        # REPARATIONS PAR JOUR
        # -----------------------------------------------------

        self.reparations_chart = self.create_chart_frame(
            "Évolution des réparations"
        )

        self.reparations_chart_view = QChartView()

        self.reparations_chart_view.setRenderHint(
            self.reparations_chart_view.renderHints()
        )

        self.reparations_chart.layout().addWidget(
            self.reparations_chart_view
        )

        charts_layout.addWidget(
            self.reparations_chart,
            2
        )

        # -----------------------------------------------------
        # STATUTS
        # -----------------------------------------------------

        self.statuts_chart = self.create_chart_frame(
            "Répartition des statuts"
        )

        self.statuts_chart_view = QChartView()

        self.statuts_chart.layout().addWidget(
            self.statuts_chart_view
        )

        charts_layout.addWidget(
            self.statuts_chart,
            1
        )

        main_layout.addLayout(
            charts_layout
        )

        # =====================================================
        # FACTURES / CA
        # =====================================================

        factures_chart = self.create_chart_frame(
            "Factures et chiffre d'affaires"
        )

        self.factures_chart_view = QChartView()

        factures_chart.layout().addWidget(
            self.factures_chart_view
        )

        main_layout.addWidget(
            factures_chart
        )

        # =====================================================
        # TYPES DE MATERIEL
        # =====================================================

        materiel_chart = self.create_chart_frame(
            "Types de matériel les plus réparés"
        )

        self.materiel_chart_view = QChartView()

        materiel_chart.layout().addWidget(
            self.materiel_chart_view
        )

        main_layout.addWidget(
            materiel_chart
        )

        # =====================================================
        # TABLEAUX
        # =====================================================

        tables_layout = QHBoxLayout()

        tables_layout.setSpacing(
            15
        )

        # -----------------------------------------------------
        # STOCK FAIBLE
        # -----------------------------------------------------

        stock_frame = self.create_table_frame(
            "⚠ Alertes stock"
        )

        self.stock_table = QTableWidget()

        self.stock_table.setColumnCount(
            4
        )

        self.stock_table.setHorizontalHeaderLabels(
            [
                "Pièce",
                "Référence",
                "Quantité",
                "Seuil"
            ]
        )

        self.configure_table(
            self.stock_table
        )

        stock_frame.layout().addWidget(
            self.stock_table
        )

        tables_layout.addWidget(
            stock_frame
        )

        # -----------------------------------------------------
        # ARTICLES LES PLUS UTILISES
        # -----------------------------------------------------

        articles_frame = self.create_table_frame(
            "📈 Articles les plus utilisés"
        )

        self.articles_table = QTableWidget()

        self.articles_table.setColumnCount(
            4
        )

        self.articles_table.setHorizontalHeaderLabels(
            [
                "Désignation",
                "Référence",
                "Quantité",
                "Montant"
            ]
        )

        self.configure_table(
            self.articles_table
        )

        articles_frame.layout().addWidget(
            self.articles_table
        )

        tables_layout.addWidget(
            articles_frame
        )

        main_layout.addLayout(
            tables_layout
        )

        # =====================================================
        # DERNIERS DOSSIERS
        # =====================================================

        dossiers_frame = self.create_table_frame(
            "📋 Derniers dossiers de réparation"
        )

        # -----------------------------------------------------
        # BARRE DE RECHERCHE
        # -----------------------------------------------------

        dossiers_search_layout = QHBoxLayout()

        self.dossiers_search = QLineEdit()

        self.dossiers_search.setPlaceholderText(
            "Rechercher par dossier, matériel, statut, client ou date..."
        )

        self.dossiers_search.setClearButtonEnabled(
            True
        )

        self.dossiers_search.setMinimumHeight(
            38
        )

        self.dossiers_search.setStyleSheet("""
            QLineEdit {
                background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                color: #111827;
                font-size: 13px;
            }

            QLineEdit:focus {
                background-color: white;
                border: 1px solid #6b7280;
            }
        """)

        self.dossiers_search.textChanged.connect(
            self.filter_dossiers_table
        )

        dossiers_search_layout.addWidget(
            self.dossiers_search
        )

        self.dossiers_count_label = QLabel(
            "0 résultat"
        )

        self.dossiers_count_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        dossiers_search_layout.addWidget(
            self.dossiers_count_label
        )

        dossiers_frame.layout().addLayout(
            dossiers_search_layout
        )

        # -----------------------------------------------------
        # TABLE
        # -----------------------------------------------------

        self.dossiers_table = QTableWidget()

        self.dossiers_table.setColumnCount(
            5
        )

        self.dossiers_table.setHorizontalHeaderLabels(
            [
                "Dossier",
                "Matériel",
                "Statut",
                "Date réception",
                "Urgent"
            ]
        )

        self.configure_table(
            self.dossiers_table
        )

        dossiers_frame.layout().addWidget(
            self.dossiers_table
        )

        tables_layout.addWidget(
            dossiers_frame
        )

        main_layout.addWidget(
            dossiers_frame
        )


        # =====================================================
        # DERNIERS CLIENTS
        # =====================================================

        clients_frame = self.create_table_frame(
            "👥 Derniers clients"
        )

        # -----------------------------------------------------
        # BARRE DE RECHERCHE
        # -----------------------------------------------------

        clients_search_layout = QHBoxLayout()

        self.clients_search = QLineEdit()

        self.clients_search.setPlaceholderText(
            "Rechercher par nom, téléphone ou email..."
        )

        self.clients_search.setClearButtonEnabled(
            True
        )

        self.clients_search.setMinimumHeight(
            38
        )

        self.clients_search.setStyleSheet("""
            QLineEdit {
                background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                color: #111827;
                font-size: 13px;
            }

            QLineEdit:focus {
                background-color: white;
                border: 1px solid #6b7280;
            }
        """)

        self.clients_search.textChanged.connect(
            self.filter_clients_table
        )

        clients_search_layout.addWidget(
            self.clients_search
        )

        self.clients_count_label = QLabel(
            "0 résultat"
        )

        self.clients_count_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        clients_search_layout.addWidget(
            self.clients_count_label
        )

        clients_frame.layout().addLayout(
            clients_search_layout
        )

        # -----------------------------------------------------
        # TABLE
        # -----------------------------------------------------

        self.clients_table = QTableWidget()

        self.clients_table.setColumnCount(
            4
        )

        self.clients_table.setHorizontalHeaderLabels(
            [
                "Nom",
                "Téléphone",
                "Email",
                "Date création"
            ]
        )

        self.configure_table(
            self.clients_table
        )

        clients_frame.layout().addWidget(
            self.clients_table
        )

        main_layout.addWidget(
            clients_frame
        )
        
        # =====================================================
        # ESPACE FINAL
        # =====================================================

        main_layout.addSpacing(
            20
        )

        self.setLayout(
            QVBoxLayout()
        )

        self.layout().addWidget(
            scroll
        )


    # =========================================================
    # CARTE STATISTIQUE
    # =========================================================

    def create_stat_card(
        self,
        title,
        value,
        icon,
        key
    ):

        card = QFrame()

        card.setMinimumHeight(
            120
        )

        card.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }

            QFrame:hover {
                border: 1px solid #cbd5e1;
            }
        """)

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            16,
            18,
            16
        )

        layout.setSpacing(
            8
        )

        header = QHBoxLayout()

        icon_label = QLabel(
            icon
        )

        icon_label.setStyleSheet("""
            QLabel {
                font-size: 21px;
                border: none;
            }
        """)

        header.addWidget(
            icon_label
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 13px;
                font-weight: 600;
                border: none;
            }
        """)

        header.addWidget(
            title_label
        )

        header.addStretch()

        layout.addLayout(
            header
        )

        value_label = QLabel(
            value
        )

        value_label.setStyleSheet("""
            QLabel {
                font-size: 27px;
                font-weight: 700;
                color: #111827;
                border: none;
            }
        """)

        layout.addWidget(
            value_label
        )

        self.stat_labels[
            key
        ] = value_label

        return card


    # =========================================================
    # FRAME GRAPHIQUE
    # =========================================================

    def create_chart_frame(
        self,
        title
    ):

        frame = QFrame()

        frame.setMinimumHeight(
            330
        )

        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(
            frame
        )

        layout.setContentsMargins(
            18,
            15,
            18,
            15
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #111827;
                border: none;
            }
        """)

        layout.addWidget(
            title_label
        )

        return frame


    # =========================================================
    # FRAME TABLE
    # =========================================================

    def create_table_frame(
        self,
        title
    ):

        frame = QFrame()

        frame.setMinimumHeight(
            300
        )

        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(
            frame
        )

        layout.setContentsMargins(
            18,
            15,
            18,
            15
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #111827;
                border: none;
            }
        """)

        layout.addWidget(
            title_label
        )

        return frame


    # =========================================================
    # CONFIGURATION TABLE
    # =========================================================

    def configure_table(
        self,
        table
    ):

        table.setAlternatingRowColors(
            True
        )

        table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        table.setShowGrid(
            False
        )

        table.verticalHeader().setVisible(
            False
        )

        table.horizontalHeader().setStretchLastSection(
            True
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: #f3f4f6;
                font-size: 12px;
                color: #374151;
            }

            QTableWidget::item {
                padding: 7px;
                border-bottom: 1px solid #f3f4f6;
            }

            QTableWidget::item:selected {
                background-color: #f3f4f6;
                color: #111827;
            }

            QHeaderView::section {
                background-color: #f9fafb;
                color: #6b7280;
                font-size: 12px;
                font-weight: 700;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e5e7eb;
            }
        """)


    # =========================================================
    # CHARGEMENT
    # =========================================================

    def load_statistics(
        self,
        periode=None
    ):

        if periode is None:

            periode = self.periode_combo.currentData()

        self.status_label.setText(
            "Actualisation des données..."
        )

        self.refresh_button.setEnabled(
            False
        )

        self.periode_combo.setEnabled(
            False
        )

        # =====================================================
        # EVITER PLUSIEURS WORKERS
        # =====================================================

        if self.worker is not None:

            if self.worker.isRunning():

                self.refresh_button.setEnabled(
                    True
                )

                self.periode_combo.setEnabled(
                    True
                )

                return

        self.worker = DashboardWorker(
            periode=periode
        )

        self.worker.result_ready.connect(
            self.update_dashboard
        )

        self.worker.error_occurred.connect(
            self.statistics_error
        )

        self.worker.finished.connect(
            self.dashboard_finished
        )

        self.worker.start()


    # =========================================================
    # CHANGEMENT PERIODE
    # =========================================================

    def on_period_changed(
        self
    ):

        periode = self.periode_combo.currentData()

        self.load_statistics(
            periode
        )


    # =========================================================
    # FIN WORKER
    # =========================================================

    def dashboard_finished(
        self
    ):

        self.refresh_button.setEnabled(
            True
        )

        self.periode_combo.setEnabled(
            True
        )


    # =========================================================
    # UPDATE DASHBOARD
    # =========================================================

    def update_dashboard(
        self,
        data
    ):

        self.dashboard_data = data

        print(
            "[DASHBOARD] Données reçues :",
            data
        )

        # =====================================================
        # CARTES
        # =====================================================

        self.update_cards(
            data
        )

        # =====================================================
        # GRAPHIQUES
        # =====================================================

        self.update_reparations_chart(
            data
        )

        self.update_statuts_chart(
            data
        )

        self.update_factures_chart(
            data
        )

        self.update_materiel_chart(
            data
        )

        # =====================================================
        # TABLEAUX
        # =====================================================

        self.update_stock_table(
            data
        )

        self.update_articles_table(
            data
        )

        self.update_dossiers_table(
            data
        )

        self.update_clients_table(
            data
        )

        # =====================================================
        # STATUS
        # =====================================================

        self.status_label.setText(
            "Données actualisées."
        )

    # =========================================================
    # CARTES
    # =========================================================

    def update_cards(
        self,
        data
    ):

        # =====================================================
        # LES KPI SONT DANS data["kpis"]
        # =====================================================

        kpis = data.get(
            "kpis",
            {}
        )

        if not isinstance(kpis, dict):
            kpis = {}

        # =====================================================
        # VALEURS
        # =====================================================

        reparations = kpis.get(
            "reparations",
            0
        )

        factures = kpis.get(
            "factures",
            0
        )

        # Quantité totale en stock
        stock = kpis.get(
            "quantite_stock",
            kpis.get(
                "stock",
                0
            )
        )

        dossiers_ouverts = kpis.get(
            "dossiers_ouverts",
            0
        )

        clients = kpis.get(
            "clients",
            0
        )

        ca_ttc = kpis.get(
            "montant_factures_ttc",
            kpis.get(
                "ca_ttc",
                0
            )
        )

        reparations_terminees = kpis.get(
            "reparations_terminees",
            0
        )

        stock_faible = kpis.get(
            "stock_faible",
            0
        )

        # =====================================================
        # AFFICHAGE
        # =====================================================

        self.stat_labels[
            "reparations"
        ].setText(
            self.format_number(
                reparations
            )
        )

        self.stat_labels[
            "factures"
        ].setText(
            self.format_number(
                factures
            )
        )

        self.stat_labels[
            "stock"
        ].setText(
            self.format_number(
                stock
            )
        )

        self.stat_labels[
            "dossiers_ouverts"
        ].setText(
            self.format_number(
                dossiers_ouverts
            )
        )

        self.stat_labels[
            "clients"
        ].setText(
            self.format_number(
                clients
            )
        )

        self.stat_labels[
            "ca_ttc"
        ].setText(
            f"{self.format_money(ca_ttc)} DH"
        )

        self.stat_labels[
            "reparations_terminees"
        ].setText(
            self.format_number(
                reparations_terminees
            )
        )

        self.stat_labels[
            "stock_faible"
        ].setText(
            self.format_number(
                stock_faible
            )
        )

    # =========================================================
    # GRAPHIQUE REPARATIONS
    # =========================================================

    def update_reparations_chart(
        self,
        data
    ):

        series = QLineSeries()

        series.setName(
            "Réparations"
        )

        # =====================================================
        # RECUPERATION
        # =====================================================

        reparations_data = data.get(
            "reparations",
            {}
        )

        if not isinstance(
            reparations_data,
            dict
        ):
            reparations_data = {}

        evolution = reparations_data.get(
            "par_jour",
            []
        )

        categories = []

        max_value = 0

        # =====================================================
        # DONNEES
        # =====================================================

        for index, item in enumerate(
            evolution
        ):

            if not isinstance(
                item,
                dict
            ):
                continue

            date = item.get(
                "date",
                ""
            )

            nombre = item.get(
                "nombre",
                item.get(
                    "count",
                    0
                )
            )

            try:

                value = float(
                    nombre or 0
                )

            except (
                TypeError,
                ValueError
            ):

                value = 0

            series.append(
                index,
                value
            )

            max_value = max(
                max_value,
                value
            )

            categories.append(
                self.short_date(
                    date
                )
            )

        # =====================================================
        # CHART
        # =====================================================

        chart = QChart()

        chart.addSeries(
            series
        )

        chart.setTitle(
            ""
        )

        chart.legend().setVisible(
            True
        )

        chart.setAnimationOptions(
            QChart.SeriesAnimations
        )

        # =====================================================
        # AXE X
        # =====================================================

        axis_x = QBarCategoryAxis()

        if categories:

            axis_x.append(
                categories
            )

        # =====================================================
        # AXE Y
        # =====================================================

        axis_y = QValueAxis()

        axis_y.setMin(
            0
        )

        axis_y.setMax(
            max(
                5,
                max_value + 2
            )
        )

        # =====================================================
        # ATTACHEMENT
        # =====================================================

        chart.addAxis(
            axis_x,
            Qt.AlignBottom
        )

        chart.addAxis(
            axis_y,
            Qt.AlignLeft
        )

        series.attachAxis(
            axis_x
        )

        series.attachAxis(
            axis_y
        )

        self.reparations_chart_view.setChart(
            chart
        )
    

    # =========================================================
    # GRAPHIQUE STATUTS
    # =========================================================

    # =========================================================
    # GRAPHIQUE STATUTS
    # =========================================================

    def update_statuts_chart(
        self,
        data
    ):

        series = QPieSeries()

        # =====================================================
        # RECUPERATION
        # =====================================================

        reparations_data = data.get(
            "reparations",
            {}
        )

        if not isinstance(
            reparations_data,
            dict
        ):
            reparations_data = {}

        statuts = reparations_data.get(
            "par_statut",
            []
        )

        # =====================================================
        # SECURITE
        # =====================================================

        if isinstance(
            statuts,
            dict
        ):

            statuts = [
                {
                    "statut": key,
                    "nombre": value
                }

                for key, value in statuts.items()
            ]

        # =====================================================
        # DONNEES
        # =====================================================

        for item in statuts:

            if not isinstance(
                item,
                dict
            ):
                continue

            statut = str(
                item.get(
                    "statut",
                    "Inconnu"
                )
            )

            nombre = item.get(
                "nombre",
                item.get(
                    "count",
                    0
                )
            )

            try:

                nombre = float(
                    nombre or 0
                )

            except (
                TypeError,
                ValueError
            ):

                nombre = 0

            if nombre > 0:

                series.append(
                    statut,
                    nombre
                )

        # =====================================================
        # CHART
        # =====================================================

        chart = QChart()

        chart.addSeries(
            series
        )

        chart.setTitle(
            ""
        )

        chart.legend().setVisible(
            True
        )

        chart.legend().setAlignment(
            Qt.AlignRight
        )

        chart.setAnimationOptions(
            QChart.SeriesAnimations
        )

        self.statuts_chart_view.setChart(
            chart
        )

    # =========================================================
    # GRAPHIQUE FACTURES
    # =========================================================

    # =========================================================
    # GRAPHIQUE FACTURES
    # =========================================================

    def update_factures_chart(
        self,
        data
    ):

        bar_series = QBarSeries()

        bar_set = QBarSet(
            "Chiffre d'affaires TTC"
        )

        # =====================================================
        # RECUPERATION
        # =====================================================

        factures_data = data.get(
            "factures",
            {}
        )

        if not isinstance(
            factures_data,
            dict
        ):
            factures_data = {}

        factures = factures_data.get(
            "par_jour",
            []
        )

        categories = []

        # =====================================================
        # MAX
        # =====================================================

        max_value = 0

        # =====================================================
        # DONNEES
        # =====================================================

        for item in factures:

            if not isinstance(
                item,
                dict
            ):
                continue

            date = item.get(
                "date",
                ""
            )

            montant = item.get(
                "montant",
                item.get(
                    "total_ttc",
                    item.get(
                        "ca",
                        0
                    )
                )
            )

            try:

                montant = float(
                    montant or 0
                )

            except (
                TypeError,
                ValueError
            ):

                montant = 0

            # Ajouter la valeur
            bar_set.append(
                montant
            )

            # Calculer le maximum directement
            max_value = max(
                max_value,
                montant
            )

            categories.append(
                self.short_date(
                    date
                )
            )

        # =====================================================
        # AJOUT SERIES
        # =====================================================

        bar_series.append(
            bar_set
        )

        # =====================================================
        # CHART
        # =====================================================

        chart = QChart()

        chart.addSeries(
            bar_series
        )

        chart.legend().setVisible(
            True
        )

        chart.setAnimationOptions(
            QChart.SeriesAnimations
        )

        # =====================================================
        # AXE X
        # =====================================================

        axis_x = QBarCategoryAxis()

        if categories:

            axis_x.append(
                categories
            )

        # =====================================================
        # AXE Y
        # =====================================================

        axis_y = QValueAxis()

        axis_y.setMin(
            0
        )

        axis_y.setMax(
            max(
                100,
                max_value * 1.2
            )
        )

        # =====================================================
        # ATTACH AXES
        # =====================================================

        chart.addAxis(
            axis_x,
            Qt.AlignBottom
        )

        chart.addAxis(
            axis_y,
            Qt.AlignLeft
        )

        bar_series.attachAxis(
            axis_x
        )

        bar_series.attachAxis(
            axis_y
        )

        self.factures_chart_view.setChart(
            chart
        )

    # =========================================================
    # GRAPHIQUE TYPES MATERIEL
    # =========================================================

    def update_materiel_chart(
        self,
        data
    ):

        bar_series = QBarSeries()

        bar_set = QBarSet(
            "Nombre de réparations"
        )

        categories = []

        # =====================================================
        # RECUPERATION
        # =====================================================

        reparations_data = data.get(
            "reparations",
            {}
        )

        if not isinstance(
            reparations_data,
            dict
        ):
            reparations_data = {}

        materiels = reparations_data.get(
            "par_materiel",
            []
        )

        # =====================================================
        # SECURITE
        # =====================================================

        if isinstance(
            materiels,
            dict
        ):

            materiels = [
                {
                    "type_materiel": key,
                    "nombre": value
                }

                for key, value in materiels.items()
            ]

        max_value = 0

        # =====================================================
        # DONNEES
        # =====================================================

        for item in materiels:

            if not isinstance(
                item,
                dict
            ):
                continue

            label = item.get(
                "type_materiel",
                item.get(
                    "type",
                    item.get(
                        "label",
                        "Autre"
                    )
                )
            )

            nombre = item.get(
                "nombre",
                item.get(
                    "count",
                    0
                )
            )

            try:

                nombre = float(
                    nombre or 0
                )

            except (
                TypeError,
                ValueError
            ):

                nombre = 0

            categories.append(
                str(label)
            )

            bar_set.append(
                nombre
            )

            max_value = max(
                max_value,
                nombre
            )

        # =====================================================
        # SERIES
        # =====================================================

        bar_series.append(
            bar_set
        )

        # =====================================================
        # CHART
        # =====================================================

        chart = QChart()

        chart.addSeries(
            bar_series
        )

        chart.legend().setVisible(
            False
        )

        chart.setAnimationOptions(
            QChart.SeriesAnimations
        )

        # =====================================================
        # AXE X
        # =====================================================

        axis_x = QBarCategoryAxis()

        if categories:

            axis_x.append(
                categories
            )

        # =====================================================
        # AXE Y
        # =====================================================

        axis_y = QValueAxis()

        axis_y.setMin(
            0
        )

        axis_y.setMax(
            max(
                5,
                max_value + 1
            )
        )

        # =====================================================
        # ATTACH AXES
        # =====================================================

        chart.addAxis(
            axis_x,
            Qt.AlignBottom
        )

        chart.addAxis(
            axis_y,
            Qt.AlignLeft
        )

        bar_series.attachAxis(
            axis_x
        )

        bar_series.attachAxis(
            axis_y
        )

        self.materiel_chart_view.setChart(
            chart
        )

    # =========================================================
    # TABLE STOCK
    # =========================================================

    def update_stock_table(
        self,
        data
    ):

        stock_data = data.get(
            "stock",
            {}
        )

        if not isinstance(
            stock_data,
            dict
        ):
            stock_data = {}

        items = stock_data.get(
            "alertes",
            []
        )

        self.stock_table.setRowCount(
            0
        )

        for item in items:

            if not isinstance(
                item,
                dict
            ):
                continue

            row = self.stock_table.rowCount()

            self.stock_table.insertRow(
                row
            )

            nom = item.get(
                "nom",
                item.get(
                    "designation",
                    ""
                )
            )

            reference = item.get(
                "reference",
                ""
            )

            quantite = item.get(
                "quantite",
                0
            )

            seuil = item.get(
                "seuil_min",
                0
            )

            values = [
                nom,
                reference,
                quantite,
                seuil
            ]

            for col, value in enumerate(
                values
            ):

                table_item = QTableWidgetItem(
                    str(value)
                )

                if col in [2, 3]:

                    table_item.setTextAlignment(
                        Qt.AlignCenter
                    )

                self.stock_table.setItem(
                    row,
                    col,
                    table_item
                )

    # =========================================================
    # TABLE ARTICLES
    # =========================================================

    def update_articles_table(
        self,
        data
    ):

        stock_data = data.get(
            "stock",
            {}
        )

        if not isinstance(
            stock_data,
            dict
        ):
            stock_data = {}

        items = stock_data.get(
            "top_produits_achats",
            []
        )

        self.articles_table.setRowCount(
            0
        )

        for item in items:

            if not isinstance(
                item,
                dict
            ):
                continue

            row = self.articles_table.rowCount()

            self.articles_table.insertRow(
                row
            )

            designation = item.get(
                "designation",
                ""
            )

            reference = item.get(
                "reference",
                ""
            )

            quantite = item.get(
                "quantite",
                0
            )

            montant = item.get(
                "montant",
                0
            )

            try:

                montant_text = (
                    f"{float(montant):,.2f}"
                    .replace(",", " ")
                    + " DH"
                )

            except (
                TypeError,
                ValueError
            ):

                montant_text = (
                    f"{montant} DH"
                )

            values = [
                designation,
                reference,
                quantite,
                montant_text
            ]

            for col, value in enumerate(
                values
            ):

                table_item = QTableWidgetItem(
                    str(value)
                )

                if col == 2:

                    table_item.setTextAlignment(
                        Qt.AlignCenter
                    )

                self.articles_table.setItem(
                    row,
                    col,
                    table_item
                )

    # =========================================================
    # TABLE DOSSIERS
    # =========================================================

    def update_dossiers_table(
        self,
        data
    ):

        # =====================================================
        # DONNEES BACKEND
        # =====================================================

        reparations = data.get(
            "reparations",
            {}
        )

        if not isinstance(
            reparations,
            dict
        ):
            reparations = {}

        items = reparations.get(
            "recentes",
            []
        )

        if not isinstance(
            items,
            list
        ):
            items = []

        # =====================================================
        # VIDER LA TABLE
        # =====================================================

        self.dossiers_table.setRowCount(
            0
        )

        # =====================================================
        # REMPLIR LA TABLE
        # =====================================================

        for item in items:

            if not isinstance(
                item,
                dict
            ):
                continue

            row = self.dossiers_table.rowCount()

            self.dossiers_table.insertRow(
                row
            )

            # -------------------------------------------------
            # DOSSIER
            # -------------------------------------------------

            numero = item.get(
                "numero_dossier"
            )

            if not numero:
                numero = f"REP-{item.get('id', '')}"

            # -------------------------------------------------
            # MATERIEL
            # -------------------------------------------------

            materiel = item.get(
                "type_materiel",
                ""
            )

            # -------------------------------------------------
            # STATUT
            # -------------------------------------------------

            statut = item.get(
                "statut",
                ""
            )

            # -------------------------------------------------
            # DATE RECEPTION
            # -------------------------------------------------

            date_reception = item.get(
                "date_reception",
                ""
            )

            # -------------------------------------------------
            # URGENT
            # -------------------------------------------------

            urgent = item.get(
                "urgent",
                False
            )

            if isinstance(
                urgent,
                str
            ):

                urgent = urgent.lower() in [
                    "true",
                    "1",
                    "oui",
                    "yes"
                ]

            urgent_text = (
                "Oui"
                if urgent
                else "Non"
            )

            # =================================================
            # VALEURS
            # =================================================

            values = [
                str(numero),
                str(materiel),
                str(statut),
                self.format_datetime(
                    date_reception
                ),
                urgent_text
            ]

            # =================================================
            # INSERTION
            # =================================================

            for col, value in enumerate(
                values
            ):

                table_item = QTableWidgetItem(
                    value
                )

                # Centrer Urgent
                if col == 4:

                    table_item.setTextAlignment(
                        Qt.AlignCenter
                    )

                self.dossiers_table.setItem(
                    row,
                    col,
                    table_item
                )

        # =====================================================
        # RECHERCHE
        # =====================================================

        if hasattr(
            self,
            "dossiers_search"
        ):

            self.filter_dossiers_table(
                self.dossiers_search.text()
            )

        else:

            for row in range(
                self.dossiers_table.rowCount()
            ):

                self.dossiers_table.setRowHidden(
                    row,
                    False
                )

        # =====================================================
        # COMPTEUR
        # =====================================================

        if hasattr(
            self,
            "dossiers_count_label"
        ):

            visible_count = 0

            for row in range(
                self.dossiers_table.rowCount()
            ):

                if not self.dossiers_table.isRowHidden(
                    row
                ):
                    visible_count += 1

            self.update_dossiers_count(
                visible_count
            )

    # =========================================================
    # TABLE CLIENTS
    # =========================================================

    def update_clients_table(
        self,
        data
    ):

        clients_data = data.get(
            "clients",
            {}
        )

        if not isinstance(
            clients_data,
            dict
        ):
            clients_data = {}

        items = clients_data.get(
            "recents",
            []
        )

        self.clients_table.setRowCount(
            0
        )

        for item in items:

            if not isinstance(
                item,
                dict
            ):
                continue

            row = self.clients_table.rowCount()

            self.clients_table.insertRow(
                row
            )

            nom = item.get(
                "nom",
                ""
            )

            telephone = item.get(
                "telephone",
                ""
            )

            email = item.get(
                "email",
                ""
            )

            date = item.get(
                "date_creation",
                ""
            )

            values = [
                nom,
                telephone,
                email,
                self.format_datetime(
                    date
                )
            ]

            for col, value in enumerate(
                values
            ):

                self.clients_table.setItem(
                    row,
                    col,
                    QTableWidgetItem(
                        str(value)
                    )
                )
            # Réafficher toutes les lignes après actualisation
            for row in range(
                self.clients_table.rowCount()
            ):

                self.clients_table.setRowHidden(
                    row,
                    False
                )

            self.filter_clients_table(
                self.clients_search.text()
            )

    # =========================================================
    # ERREUR
    # =========================================================

    def statistics_error(
        self,
        message
    ):

        print(
            "[DASHBOARD] Erreur :",
            message
        )

        self.status_label.setText(
            "Impossible de charger les statistiques."
        )

        self.refresh_button.setEnabled(
            True
        )

        self.periode_combo.setEnabled(
            True
        )

    # =========================================================
    # ACTUALISER
    # =========================================================

    def refresh(
        self
    ):

        periode = self.periode_combo.currentData()

        self.load_statistics(
            periode
        )


    # =========================================================
    # FORMAT NOMBRE
    # =========================================================

    @staticmethod
    def format_number(
        value
    ):

        try:

            return f"{int(value):,}".replace(
                ",",
                " "
            )

        except:

            return str(
                value
            )


    # =========================================================
    # FORMAT MONNAIE
    # =========================================================

    @staticmethod
    def format_money(
        value
    ):

        try:

            return f"{float(value):,.2f}".replace(
                ",",
                " "
            )

        except:

            return str(
                value
            )


    # =========================================================
    # DATE COURTE
    # =========================================================

    @staticmethod
    def short_date(
        value
    ):

        if not value:

            return ""

        text = str(
            value
        )

        # YYYY-MM-DD
        if len(text) >= 10:

            return text[8:10] + "/" + text[5:7]

        return text


    # =========================================================
    # DATETIME
    # =========================================================

    @staticmethod
    def format_datetime(
        value
    ):

        if not value:

            return ""

        text = str(
            value
        )

        if len(text) >= 16:

            return (
                text[8:10]
                + "/"
                + text[5:7]
                + "/"
                + text[0:4]
                + " "
                + text[11:16]
            )

        return text

    # =========================================================
    # RECHERCHE DOSSIERS
    # =========================================================

    def filter_dossiers_table(
        self,
        text
    ):

        search_text = (
            text
            .strip()
            .lower()
        )

        visible_count = 0

        for row in range(
            self.dossiers_table.rowCount()
        ):

            row_match = False

            for column in range(
                self.dossiers_table.columnCount()
            ):

                item = self.dossiers_table.item(
                    row,
                    column
                )

                if item is None:
                    continue

                cell_text = (
                    item.text()
                    .strip()
                    .lower()
                )

                if search_text in cell_text:

                    row_match = True

                    break

            self.dossiers_table.setRowHidden(
                row,
                not row_match
            )

            if row_match:
                visible_count += 1

        self.update_dossiers_count(
            visible_count
        )

    # =========================================================
    # COMPTEUR DOSSIERS
    # =========================================================

    def update_dossiers_count(
        self,
        count
    ):

        if count <= 1:

            self.dossiers_count_label.setText(
                f"{count} résultat"
            )

        else:

            self.dossiers_count_label.setText(
                f"{count} résultats"
            )

    # =========================================================
    # RECHERCHE CLIENTS
    # =========================================================

    def filter_clients_table(
        self,
        text
    ):

        search_text = (
            text
            .strip()
            .lower()
        )

        visible_count = 0

        for row in range(
            self.clients_table.rowCount()
        ):

            row_match = False

            for column in range(
                self.clients_table.columnCount()
            ):

                item = self.clients_table.item(
                    row,
                    column
                )

                if item is None:
                    continue

                cell_text = (
                    item.text()
                    .strip()
                    .lower()
                )

                if search_text in cell_text:

                    row_match = True

                    break

            self.clients_table.setRowHidden(
                row,
                not row_match
            )

            if row_match:
                visible_count += 1

        self.update_clients_count(
            visible_count
        )

    # =========================================================
    # COMPTEUR CLIENTS
    # =========================================================

    def update_clients_count(
        self,
        count
    ):

        if count <= 1:

            self.clients_count_label.setText(
                f"{count} résultat"
            )

        else:

            self.clients_count_label.setText(
                f"{count} résultats"
            )


