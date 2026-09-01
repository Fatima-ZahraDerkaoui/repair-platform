from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QComboBox,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSizePolicy,
    QLineEdit
)

from PySide6.QtCore import (
    Qt,
    QThread,
    Signal
)

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

from datetime import datetime
from collections import defaultdict

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
            try:
                data = BackendAPI.get_dashboard_stats(periode=self.periode)
            except TypeError:
                data = BackendAPI.get_dashboard_stats()

            if not isinstance(data, dict):
                raise Exception("Réponse dashboard invalide.")

            self.result_ready.emit(data)

        except Exception as error:
            self.error_occurred.emit(str(error))


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
        self.setStyleSheet("background-color: #FFFFFF;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: #FFFFFF; }")

        content = QWidget()
        content.setStyleSheet("background-color: #FFFFFF;")
        scroll.setWidget(content)

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(32, 28, 32, 32)
        main_layout.setSpacing(24)

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------
        header_layout = QHBoxLayout()
        header_left = QVBoxLayout()

        titre = QLabel("Tableau de bord")
        titre.setStyleSheet("font-size: 26px; font-weight: 800; color: #0F172A;")
        header_left.addWidget(titre)

        sous_titre = QLabel("Aperçu de l'activité globale de l'atelier")
        sous_titre.setStyleSheet("font-size: 13px; color: #64748B;")
        header_left.addWidget(sous_titre)

        header_layout.addLayout(header_left)
        header_layout.addStretch()

        periode_label = QLabel("Période :")
        periode_label.setStyleSheet("font-size: 13px; color: #334155; font-weight: 600;")
        header_layout.addWidget(periode_label)

        self.periode_combo = QComboBox()
        self.periode_combo.addItem("7 derniers jours", "7j")
        self.periode_combo.addItem("30 derniers jours", "30j")
        self.periode_combo.addItem("90 derniers jours", "90j")
        self.periode_combo.addItem("Cette année", "1an")
        self.periode_combo.setCurrentIndex(1)
        self.periode_combo.setMinimumWidth(160)
        self.periode_combo.setStyleSheet("""
            QComboBox {
                background: #FFFFFF; border: 1px solid #CBD5E1;
                border-radius: 6px; padding: 6px 12px; color: #0F172A; font-size: 13px;
            }
            QComboBox:focus { border-color: #2563EB; }
        """)
        self.periode_combo.currentIndexChanged.connect(self.on_period_changed)
        header_layout.addWidget(self.periode_combo)

        main_layout.addLayout(header_layout)

        self.status_label = QLabel("Mise à jour...")
        self.status_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        main_layout.addWidget(self.status_label)

        # -----------------------------------------------------
        # CARTES KPI (SANS EMOJIS)
        # -----------------------------------------------------
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)

        stats_layout.addWidget(self.create_stat_card("Réparations totales", "0", "reparations"), 0, 0)
        stats_layout.addWidget(self.create_stat_card("Factures émises", "0", "factures"), 0, 1)
        stats_layout.addWidget(self.create_stat_card("Articles en Stock", "0", "stock"), 0, 2)
        stats_layout.addWidget(self.create_stat_card("Dossiers ouverts", "0", "dossiers_ouverts"), 0, 3)
        stats_layout.addWidget(self.create_stat_card("Clients enregistrés", "0", "clients"), 1, 0)
        stats_layout.addWidget(self.create_stat_card("Chiffre d'Affaires", "0 DH", "ca_ttc"), 1, 1)
        stats_layout.addWidget(self.create_stat_card("Réparations terminées", "0", "reparations_terminees"), 1, 2)
        stats_layout.addWidget(self.create_stat_card("Alerte stock critique", "0", "stock_faible"), 1, 3)

        main_layout.addLayout(stats_layout)

        # -----------------------------------------------------
        # GRAPHIQUES SUPERIEURS
        # -----------------------------------------------------
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)

        self.reparations_chart = self.create_chart_frame("Évolution du volume de réparations")
        self.reparations_chart_view = QChartView()
        self.reparations_chart_view.setRenderHint(self.reparations_chart_view.renderHints())
        self.reparations_chart.layout().addWidget(self.reparations_chart_view)
        charts_layout.addWidget(self.reparations_chart, 2)

        self.statuts_chart = self.create_chart_frame("Répartition par statut")
        self.statuts_chart_view = QChartView()
        self.statuts_chart.layout().addWidget(self.statuts_chart_view)
        charts_layout.addWidget(self.statuts_chart, 1)

        main_layout.addLayout(charts_layout)

        # -----------------------------------------------------
        # GRAPHIQUE CA RÉPARATIONS
        # -----------------------------------------------------
        ca_chart_frame = self.create_chart_frame("Revenus & Chiffre d'Affaires")
        
        ca_header_layout = QHBoxLayout()
        ca_header_layout.addStretch()
        
        ca_group_label = QLabel("Regroupement :")
        ca_group_label.setStyleSheet("font-size: 12px; color: #475569; font-weight: 600;")
        ca_header_layout.addWidget(ca_group_label)

        self.ca_group_combo = QComboBox()
        self.ca_group_combo.addItem("Par Jour", "jour")
        self.ca_group_combo.addItem("Par Semaine", "semaine")
        self.ca_group_combo.addItem("Par Mois", "mois")
        self.ca_group_combo.setStyleSheet("""
            QComboBox {
                background: #F8FAFC; border: 1px solid #CBD5E1;
                border-radius: 6px; padding: 4px 8px; font-size: 12px; color: #0F172A;
            }
        """)
        self.ca_group_combo.currentIndexChanged.connect(self.on_ca_group_changed)
        ca_header_layout.addWidget(self.ca_group_combo)
        
        ca_chart_frame.layout().addLayout(ca_header_layout)

        self.factures_chart_view = QChartView()
        ca_chart_frame.layout().addWidget(self.factures_chart_view)
        main_layout.addWidget(ca_chart_frame)

        # -----------------------------------------------------
        # TYPES DE MATERIEL
        # -----------------------------------------------------
        materiel_chart = self.create_chart_frame("Types de matériels pris en charge")
        self.materiel_chart_view = QChartView()
        materiel_chart.layout().addWidget(self.materiel_chart_view)
        main_layout.addWidget(materiel_chart)

        # -----------------------------------------------------
        # TABLEAUX DE BORD (STOCK ET TOP PIÈCES)
        # -----------------------------------------------------
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(16)

        stock_frame = self.create_table_frame("Alertes de stock")
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(4)
        self.stock_table.setHorizontalHeaderLabels(["Désignation", "Référence", "Quantité", "Seuil min"])
        self.configure_table(self.stock_table)
        stock_frame.layout().addWidget(self.stock_table)
        tables_layout.addWidget(stock_frame)

        articles_frame = self.create_table_frame("Pièces les plus consommées")
        self.articles_table = QTableWidget()
        self.articles_table.setColumnCount(4)
        self.articles_table.setHorizontalHeaderLabels(["Désignation", "Référence", "Quantité", "Montant Total"])
        self.configure_table(self.articles_table)
        articles_frame.layout().addWidget(self.articles_table)
        tables_layout.addWidget(articles_frame)

        main_layout.addLayout(tables_layout)

        # -----------------------------------------------------
        # TABLEAU : DOSSIERS RÉCENTS
        # -----------------------------------------------------
        dossiers_frame = self.create_table_frame("Derniers dossiers de réparation")
        dossiers_search_layout = QHBoxLayout()
        self.dossiers_search = QLineEdit()
        self.dossiers_search.setPlaceholderText("Filtrer par dossier, matériel, statut, client...")
        self.dossiers_search.setClearButtonEnabled(True)
        self.dossiers_search.setMinimumHeight(36)
        self.dossiers_search.textChanged.connect(self.filter_dossiers_table)
        dossiers_search_layout.addWidget(self.dossiers_search)
        
        self.dossiers_count_label = QLabel("0 résultat")
        self.dossiers_count_label.setStyleSheet("color: #64748B; font-size: 12px;")
        dossiers_search_layout.addWidget(self.dossiers_count_label)
        dossiers_frame.layout().addLayout(dossiers_search_layout)

        self.dossiers_table = QTableWidget()
        self.dossiers_table.setColumnCount(5)
        self.dossiers_table.setHorizontalHeaderLabels(["N° Dossier", "Matériel", "Statut", "Date Réception", "Urgent"])
        self.configure_table(self.dossiers_table)
        dossiers_frame.layout().addWidget(self.dossiers_table)
        main_layout.addWidget(dossiers_frame)

        # -----------------------------------------------------
        # TABLEAU : CLIENTS RÉCENTS
        # -----------------------------------------------------
        clients_frame = self.create_table_frame("Nouveaux clients enregistrés")
        clients_search_layout = QHBoxLayout()
        self.clients_search = QLineEdit()
        self.clients_search.setPlaceholderText("Filtrer par nom, téléphone ou email...")
        self.clients_search.setClearButtonEnabled(True)
        self.clients_search.setMinimumHeight(36)
        self.clients_search.textChanged.connect(self.filter_clients_table)
        clients_search_layout.addWidget(self.clients_search)

        self.clients_count_label = QLabel("0 résultat")
        self.clients_count_label.setStyleSheet("color: #64748B; font-size: 12px;")
        clients_search_layout.addWidget(self.clients_count_label)
        clients_frame.layout().addLayout(clients_search_layout)

        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(4)
        self.clients_table.setHorizontalHeaderLabels(["Nom complet", "Téléphone", "Email", "Date d'ajout"])
        self.configure_table(self.clients_table)
        clients_frame.layout().addWidget(self.clients_table)
        main_layout.addWidget(clients_frame)

        main_layout.addSpacing(20)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)

    # =========================================================
    # MÉTHODES DE CONSTRUCTION
    # =========================================================

    def create_stat_card(self, title, value, key):
        card = QFrame()
        card.setMinimumHeight(100)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setStyleSheet("""
            QFrame { 
                background-color: #FFFFFF; 
                border: 1px solid #E2E8F0; 
                border-radius: 8px; 
            }
            QFrame:hover { 
                border-color: #CBD5E1; 
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        title_label = QLabel(title.upper())
        title_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 700; border: none; letter-spacing: 0.5px;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #0F172A; border: none;")
        layout.addWidget(value_label)

        self.stat_labels[key] = value_label
        return card

    def create_chart_frame(self, title):
        frame = QFrame()
        frame.setMinimumHeight(320)
        frame.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; }")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #0F172A; border: none;")
        layout.addWidget(title_label)
        return frame

    def create_table_frame(self, title):
        frame = QFrame()
        frame.setMinimumHeight(280)
        frame.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; }")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #0F172A; border: none;")
        layout.addWidget(title_label)
        return frame

    def configure_table(self, table):
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setShowGrid(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("""
            QTableWidget { 
                background-color: #FFFFFF; 
                border: none; 
                font-size: 12px; 
                color: #1E293B; 
            }
            QTableWidget::item { 
                padding: 8px; 
                border-bottom: 1px solid #F1F5F9; 
            }
            QHeaderView::section { 
                background-color: #F8FAFC; 
                color: #64748B; 
                font-size: 11px; 
                font-weight: 700; 
                border: none; 
                padding: 6px;
            }
        """)

    # =========================================================
    # CHARGEMENT ET DÉCLENCHEURS
    # =========================================================

    def load_statistics(self, periode=None):
        if periode is None:
            periode = self.periode_combo.currentData()

        self.status_label.setText("Actualisation des données...")
        self.periode_combo.setEnabled(False)

        if self.worker is not None and self.worker.isRunning():
            self.periode_combo.setEnabled(True)
            return

        self.worker = DashboardWorker(periode=periode)
        self.worker.result_ready.connect(self.update_dashboard)
        self.worker.error_occurred.connect(self.statistics_error)
        self.worker.finished.connect(self.dashboard_finished)
        self.worker.start()

    def on_period_changed(self):
        self.load_statistics(self.periode_combo.currentData())

    def on_ca_group_changed(self):
        if self.dashboard_data:
            self.update_factures_chart(self.dashboard_data)

    def dashboard_finished(self):
        self.periode_combo.setEnabled(True)

    def load_data(self):
        self.load_statistics()

    # =========================================================
    # MISE À JOUR DU DASHBOARD
    # =========================================================

    def update_dashboard(self, data):
        self.dashboard_data = data
        self.update_cards(data)
        self.update_reparations_chart(data)
        self.update_statuts_chart(data)
        self.update_factures_chart(data)
        self.update_materiel_chart(data)
        self.update_stock_table(data)
        self.update_articles_table(data)
        self.update_dossiers_table(data)
        self.update_clients_table(data)
        self.status_label.setText("Données synchronisées.")

    def update_cards(self, data):
        kpis = data.get("kpis", {})
        if not isinstance(kpis, dict):
            kpis = {}

        self.stat_labels["reparations"].setText(self.format_number(kpis.get("reparations", 0)))
        self.stat_labels["factures"].setText(self.format_number(kpis.get("factures", 0)))
        self.stat_labels["stock"].setText(self.format_number(kpis.get("quantite_stock", kpis.get("stock", 0))))
        self.stat_labels["dossiers_ouverts"].setText(self.format_number(kpis.get("dossiers_ouverts", 0)))
        self.stat_labels["clients"].setText(self.format_number(kpis.get("clients", 0)))
        
        ca = kpis.get("ca_reparations", kpis.get("ca_ttc", kpis.get("montant_factures_ttc", 0.0)))
        self.stat_labels["ca_ttc"].setText(f"{self.format_money(ca)} DH")
        self.stat_labels["reparations_terminees"].setText(self.format_number(kpis.get("reparations_terminees", 0)))
        self.stat_labels["stock_faible"].setText(self.format_number(kpis.get("stock_faible", 0)))

    def update_factures_chart(self, data):
        bar_series = QBarSeries()
        bar_set = QBarSet("Montant (DH)")

        reparations_data = data.get("reparations", {})
        if not isinstance(reparations_data, dict):
            reparations_data = {}

        items = reparations_data.get("par_jour", [])
        group_mode = self.ca_group_combo.currentData()

        aggregated = defaultdict(float)

        for item in items:
            if not isinstance(item, dict):
                continue

            date_str = item.get("date", "")
            if not date_str:
                continue

            montant = item.get("cout_reel", item.get("cout_estime", item.get("montant", 0)))
            try:
                montant_val = float(montant or 0)
            except (TypeError, ValueError):
                montant_val = 0.0

            try:
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                if group_mode == "semaine":
                    key = dt.strftime("%Y-W%U")
                elif group_mode == "mois":
                    key = dt.strftime("%m/%Y")
                else:
                    key = dt.strftime("%d/%m")
            except Exception:
                key = self.short_date(date_str)

            aggregated[key] += montant_val

        categories = []
        max_value = 0.0

        for cat_key, total_montant in aggregated.items():
            bar_set.append(total_montant)
            categories.append(cat_key)
            max_value = max(max_value, total_montant)

        bar_series.append(bar_set)

        chart = QChart()
        chart.addSeries(bar_series)
        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        if categories:
            axis_x.append(categories)

        axis_y = QValueAxis()
        axis_y.setMin(0)
        axis_y.setMax(max(100.0, max_value * 1.2))

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)

        bar_series.attachAxis(axis_x)
        bar_series.attachAxis(axis_y)

        self.factures_chart_view.setChart(chart)

    def update_reparations_chart(self, data):
        series = QLineSeries()
        series.setName("Réparations")
        reparations_data = data.get("reparations", {})
        evolution = reparations_data.get("par_jour", [])

        categories = []
        max_value = 0

        for index, item in enumerate(evolution):
            if not isinstance(item, dict):
                continue
            date = item.get("date", "")
            nombre = item.get("nombre", item.get("count", 0))
            value = float(nombre or 0)
            series.append(index, value)
            max_value = max(max_value, value)
            categories.append(self.short_date(date))

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        if categories:
            axis_x.append(categories)

        axis_y = QValueAxis()
        axis_y.setMin(0)
        axis_y.setMax(max(5, int(max_value) + 1))

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        self.reparations_chart_view.setChart(chart)

    def update_statuts_chart(self, data):
        series = QPieSeries()
        reparations_data = data.get("reparations", {})
        statuts = reparations_data.get("par_statut", [])

        if isinstance(statuts, dict):
            statuts = [{"statut": k, "nombre": v} for k, v in statuts.items()]

        for item in statuts:
            if not isinstance(item, dict):
                continue
            statut = str(item.get("statut", "Inconnu"))
            nombre = float(item.get("nombre", 0))
            if nombre > 0:
                series.append(statut, nombre)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        self.statuts_chart_view.setChart(chart)

    def update_materiel_chart(self, data):
        bar_series = QBarSeries()
        bar_set = QBarSet("Nombre")
        categories = []

        reparations_data = data.get("reparations", {})
        materiels = reparations_data.get("par_materiel", [])

        if isinstance(materiels, dict):
            materiels = [{"type_materiel": k, "nombre": v} for k, v in materiels.items()]

        max_value = 0
        for item in materiels:
            if not isinstance(item, dict):
                continue
            label = str(item.get("type_materiel", "Autre"))
            nombre = float(item.get("nombre", 0))
            categories.append(label)
            bar_set.append(nombre)
            max_value = max(max_value, nombre)

        bar_series.append(bar_set)
        chart = QChart()
        chart.addSeries(bar_series)
        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        if categories:
            axis_x.append(categories)

        axis_y = QValueAxis()
        axis_y.setMin(0)
        axis_y.setMax(max(5, max_value + 1))

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_x)
        bar_series.attachAxis(axis_y)

        self.materiel_chart_view.setChart(chart)

    def update_stock_table(self, data):
        stock_data = data.get("stock", {})
        items = stock_data.get("alertes", [])
        self.stock_table.setRowCount(0)

        for item in items:
            if not isinstance(item, dict):
                continue
            row = self.stock_table.rowCount()
            self.stock_table.insertRow(row)
            values = [item.get("nom", ""), item.get("reference", ""), item.get("quantite", 0), item.get("seuil_min", 0)]
            for col, value in enumerate(values):
                t_item = QTableWidgetItem(str(value))
                if col in [2, 3]:
                    t_item.setTextAlignment(Qt.AlignCenter)
                self.stock_table.setItem(row, col, t_item)

    def update_articles_table(self, data):
        stock_data = data.get("stock", {})
        items = stock_data.get("top_produits_achats", [])
        self.articles_table.setRowCount(0)

        for item in items:
            if not isinstance(item, dict):
                continue
            row = self.articles_table.rowCount()
            self.articles_table.insertRow(row)
            montant = item.get("montant", 0)
            montant_text = f"{float(montant):,.2f}".replace(",", " ") + " DH"
            values = [item.get("designation", ""), item.get("reference", ""), item.get("quantite", 0), montant_text]
            for col, value in enumerate(values):
                t_item = QTableWidgetItem(str(value))
                if col == 2:
                    t_item.setTextAlignment(Qt.AlignCenter)
                self.articles_table.setItem(row, col, t_item)

    def update_dossiers_table(self, data):
        reparations = data.get("reparations", {})
        items = reparations.get("recentes", [])
        self.dossiers_table.setRowCount(0)

        for item in items:
            if not isinstance(item, dict):
                continue
            row = self.dossiers_table.rowCount()
            self.dossiers_table.insertRow(row)
            numero = item.get("numero_dossier") or f"REP-{item.get('id', '')}"
            urgent_text = "Oui" if item.get("urgent") else "Non"
            values = [str(numero), str(item.get("type_materiel", "")), str(item.get("statut", "")), self.format_datetime(item.get("date_reception")), urgent_text]
            for col, value in enumerate(values):
                t_item = QTableWidgetItem(value)
                if col == 4:
                    t_item.setTextAlignment(Qt.AlignCenter)
                self.dossiers_table.setItem(row, col, t_item)

        if hasattr(self, "dossiers_search"):
            self.filter_dossiers_table(self.dossiers_search.text())

    def update_clients_table(self, data):
        clients_data = data.get("clients", {})
        items = clients_data.get("recents", [])
        self.clients_table.setRowCount(0)

        for item in items:
            if not isinstance(item, dict):
                continue
            row = self.clients_table.rowCount()
            self.clients_table.insertRow(row)
            values = [item.get("nom", ""), item.get("telephone", ""), item.get("email", ""), self.format_datetime(item.get("date_creation"))]
            for col, value in enumerate(values):
                self.clients_table.setItem(row, col, QTableWidgetItem(str(value)))

        if hasattr(self, "clients_search"):
            self.filter_clients_table(self.clients_search.text())

    # =========================================================
    # RECHERCHES ET UTILITAIRES
    # =========================================================

    def filter_dossiers_table(self, text):
        search_text = text.strip().lower()
        visible_count = 0
        for row in range(self.dossiers_table.rowCount()):
            match = any(search_text in (self.dossiers_table.item(row, col).text().lower() if self.dossiers_table.item(row, col) else "") for col in range(self.dossiers_table.columnCount()))
            self.dossiers_table.setRowHidden(row, not match)
            if match:
                visible_count += 1
        self.update_dossiers_count(visible_count)

    def filter_clients_table(self, text):
        search_text = text.strip().lower()
        visible_count = 0
        for row in range(self.clients_table.rowCount()):
            match = any(search_text in (self.clients_table.item(row, col).text().lower() if self.clients_table.item(row, col) else "") for col in range(self.clients_table.columnCount()))
            self.clients_table.setRowHidden(row, not match)
            if match:
                visible_count += 1
        self.update_clients_count(visible_count)

    def update_dossiers_count(self, count):
        self.dossiers_count_label.setText(f"{count} résultat" if count <= 1 else f"{count} résultats")

    def update_clients_count(self, count):
        self.clients_count_label.setText(f"{count} résultat" if count <= 1 else f"{count} résultats")

    def statistics_error(self, message):
        self.status_label.setText("Erreur de chargement des données.")
        self.periode_combo.setEnabled(True)

    @staticmethod
    def format_number(value):
        try:
            return f"{int(value):,}".replace(",", " ")
        except Exception:
            return str(value)

    @staticmethod
    def format_money(value):
        try:
            return f"{float(value):,.2f}".replace(",", " ")
        except Exception:
            return str(value)

    @staticmethod
    def short_date(value):
        text = str(value) if value else ""
        return text[8:10] + "/" + text[5:7] if len(text) >= 10 else text

    @staticmethod
    def format_datetime(value):
        text = str(value) if value else ""
        return text[8:10] + "/" + text[5:7] + "/" + text[0:4] + " " + text[11:16] if len(text) >= 16 else text
    