from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox
)

from views.widgets.sidebar import Sidebar
from views.pages.login_page import LoginPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Repair Platform")
        self.resize(1400, 850)
        self.showMaximized()

        self.current_user = None
        self.init_ui()

    def init_ui(self):
        # Stack global pour basculer entre Login et App Principale
        self.root_stack = QStackedWidget()
        self.setCentralWidget(self.root_stack)

        # 1. ÉCRAN DE LOGIN
        self.login_page = LoginPage()
        self.login_page.login_successful.connect(self.on_login_success)
        self.root_stack.addWidget(self.login_page)

        # 2. CONTENEUR PRINCIPAL DE L'APPLICATION
        self.main_app_widget = QWidget()
        app_layout = QHBoxLayout(self.main_app_widget)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.show_page)
        self.sidebar.quit_requested.connect(self.logout)
        app_layout.addWidget(self.sidebar)

        # Vues empilées
        self.pages = QStackedWidget()
        app_layout.addWidget(self.pages)

        # Initialisation des vues
        self.create_pages()
        self.root_stack.addWidget(self.main_app_widget)

        # Démarrage obligatoire sur la page de connexion
        self.root_stack.setCurrentWidget(self.login_page)

    def on_login_success(self, user_info):
        self.current_user = user_info
        self.root_stack.setCurrentWidget(self.main_app_widget)
        self.show_page("dashboard")

    def logout(self):
        self.current_user = None
        self.root_stack.setCurrentWidget(self.login_page)

    def create_pages(self):
        from views.pages.menu_principal import MenuPrincipal
        from views.pages.nouvelle_reparation import NouvelleReparation
        from views.pages.factures_page import FacturesPage
        from views.pages.stock_page import StockPage
        from views.pages.dossiers_page import DossiersPage
        from views.pages.administration_page import AdministrationPage

        self.dashboard_page = MenuPrincipal(self)
        self.pages.addWidget(self.dashboard_page)

        self.reparation_page = NouvelleReparation(self)
        self.pages.addWidget(self.reparation_page)

        self.factures_page = FacturesPage(self)
        self.factures_page.facture_validated.connect(self.on_facture_validated)
        self.pages.addWidget(self.factures_page)

        self.stock_page = StockPage(self)
        self.pages.addWidget(self.stock_page)

        self.dossiers_page = DossiersPage(self)
        self.pages.addWidget(self.dossiers_page)

        self.administration_page = AdministrationPage(self)
        self.pages.addWidget(self.administration_page)

    def show_page(self, page_name):
        mapping = {
            "dashboard": self.dashboard_page,
            "nouvelle_reparation": self.reparation_page,
            "factures": self.factures_page,
            "stock": self.stock_page,
            "dossiers": self.dossiers_page,
            "administration": self.administration_page
        }

        page = mapping.get(page_name)
        if page is not None:
            self.pages.setCurrentWidget(page)

            if page_name == "dashboard" and hasattr(self.dashboard_page, "load_data"):
                self.dashboard_page.load_data()

            elif page_name == "dossiers" and hasattr(self.dossiers_page, "load_dossiers"):
                self.dossiers_page.load_dossiers()

            elif page_name == "administration" and hasattr(self.administration_page, "load_users"):
                self.administration_page.load_users()

    def on_facture_validated(self, facture):
        QMessageBox.information(
            self,
            "Facture validée",
            "La facture a été validée avec succès."
        )

    