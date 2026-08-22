from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox
)

from views.widgets.sidebar import Sidebar


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Repair Platform"
        )

        self.resize(
            1400,
            850
        )

        self.init_ui()

    # =========================================================
    # UI
    # =========================================================

    def init_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        layout = QHBoxLayout(
            central
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(0)

        # -----------------------------------------------------
        # SIDEBAR
        # -----------------------------------------------------

        self.sidebar = Sidebar()

        self.sidebar.page_changed.connect(
            self.show_page
        )

        self.sidebar.quit_requested.connect(
            self.close
        )

        layout.addWidget(
            self.sidebar
        )

        # -----------------------------------------------------
        # STACKED CONTENT
        # -----------------------------------------------------

        self.pages = QStackedWidget()

        layout.addWidget(
            self.pages
        )

        # -----------------------------------------------------
        # PAGES
        # -----------------------------------------------------

        self.create_pages()

        self.show_page(
            "dashboard"
        )

    # =========================================================
    # CREATE PAGES
    # =========================================================

    def create_pages(self):

        from views.pages.menu_principal import (
            MenuPrincipal
        )

        from views.pages.nouvelle_reparation import (
            NouvelleReparation
        )

        from views.pages.factures_page import (
            FacturesPage
        )

        from views.pages.stock_page import (
            StockPage
        )

        from views.pages.dossiers_page import (
            DossiersPage
        )

        # -----------------------------------------------------
        # DASHBOARD
        # -----------------------------------------------------

        self.dashboard_page = MenuPrincipal(
            self
        )

        self.pages.addWidget(
            self.dashboard_page
        )

        # -----------------------------------------------------
        # REPARATION
        # -----------------------------------------------------

        self.reparation_page = NouvelleReparation(
            self
        )

        self.pages.addWidget(
            self.reparation_page
        )

        # -----------------------------------------------------
        # FACTURES
        # -----------------------------------------------------

        self.factures_page = FacturesPage(
            self
        )

        self.factures_page.facture_validated.connect(
            self.on_facture_validated
        )

        self.pages.addWidget(
            self.factures_page
        )

        # -----------------------------------------------------
        # STOCK
        # -----------------------------------------------------

        self.stock_page = StockPage(
            self
        )

        self.pages.addWidget(
            self.stock_page
        )

        # -----------------------------------------------------
        # DOSSIERS
        # -----------------------------------------------------

        self.dossiers_page = DossiersPage(
            self
        )

        self.pages.addWidget(
            self.dossiers_page
        )

    # =========================================================
    # NAVIGATION
    # =========================================================

    def show_page(self, page_name):

        mapping = {

            "dashboard": self.dashboard_page,

            "nouvelle_reparation":
                self.reparation_page,

            "factures":
                self.factures_page,

            "stock":
                self.stock_page,

            "dossiers":
                self.dossiers_page
        }

        page = mapping.get(
            page_name
        )

        if page is not None:

            self.pages.setCurrentWidget(
                page
            )

            # Rafraîchir les données lorsqu'on ouvre
            # les pages concernées.

            if page_name == "dashboard":

                if hasattr(
                    self.dashboard_page,
                    "load_data"
                ):
                    self.dashboard_page.load_data()

            elif page_name == "dossiers":

                if hasattr(
                    self.dossiers_page,
                    "load_dossiers"
                ):
                    self.dossiers_page.load_dossiers()

    # =========================================================
    # FACTURE VALIDEE
    # =========================================================

    def on_facture_validated(
        self,
        facture
    ):

        QMessageBox.information(
            self,
            "Facture validée",
            "La facture a été validée avec succès."
        )