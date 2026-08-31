import requests
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QGroupBox,
    QFrame,
    QScrollArea,
    QMessageBox,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox
)
from PySide6.QtCore import Qt

API_URL = "http://127.0.0.1:8000"


# =========================================================
# BOÎTE DE DIALOGUE : MODIFICATION UTILISATEUR
# =========================================================
class EditUserDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier l'utilisateur")
        self.setFixedWidth(420)
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel { font-weight: 600; color: #334155; font-size: 13px; }
            QLineEdit, QComboBox { 
                background-color: #FFFFFF; border: 1px solid #CBD5E1; 
                border-radius: 6px; padding: 8px; font-size: 13px; color: #0F172A; 
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #4F46E5; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        grid = QGridLayout()
        grid.setSpacing(10)

        self.input_nom = QLineEdit(str(user_data.get("nom", "")))
        self.input_email = QLineEdit(str(user_data.get("email", "")))
        self.input_tel = QLineEdit(str(user_data.get("telephone") or ""))
        
        # Nouveau mot de passe (laisser vide pour ne pas changer)
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Laisser vide si inchangé")
        self.input_password.setEchoMode(QLineEdit.Password)

        self.combo_role = QComboBox()
        self.combo_role.addItems(["Technicien", "Administrateur", "Réceptionniste"])
        
        idx = self.combo_role.findText(user_data.get("role", "Technicien"))
        if idx >= 0:
            self.combo_role.setCurrentIndex(idx)

        grid.addWidget(QLabel("Nom complet :"), 0, 0)
        grid.addWidget(self.input_nom, 0, 1)
        grid.addWidget(QLabel("Email :"), 1, 0)
        grid.addWidget(self.input_email, 1, 1)
        grid.addWidget(QLabel("Téléphone :"), 2, 0)
        grid.addWidget(self.input_tel, 2, 1)
        grid.addWidget(QLabel("Nouveau MDP :"), 3, 0)
        grid.addWidget(self.input_password, 3, 1)
        grid.addWidget(QLabel("Rôle :"), 4, 0)
        grid.addWidget(self.combo_role, 4, 1)

        layout.addLayout(grid)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        data = {
            "nom": self.input_nom.text().strip(),
            "email": self.input_email.text().strip(),
            "telephone": self.input_tel.text().strip() or None,
            "role": self.combo_role.currentText()
        }
        # Inclure le mot de passe seulement s'il a été saisi
        pwd = self.input_password.text().strip()
        if pwd:
            data["password"] = pwd
        return data


# =========================================================
# BOÎTE DE DIALOGUE : MODIFICATION CLIENT
# =========================================================
class EditClientDialog(QDialog):
    def __init__(self, client_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier le client")
        self.setFixedWidth(400)
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel { font-weight: 600; color: #334155; font-size: 13px; }
            QLineEdit { 
                background-color: #FFFFFF; border: 1px solid #CBD5E1; 
                border-radius: 6px; padding: 8px; font-size: 13px; color: #0F172A; 
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        grid = QGridLayout()
        grid.setSpacing(10)

        self.input_nom = QLineEdit(str(client_data.get("nom", "")))
        self.input_tel = QLineEdit(str(client_data.get("telephone", "")))
        self.input_email = QLineEdit(str(client_data.get("email") or ""))
        self.input_adresse = QLineEdit(str(client_data.get("adresse") or ""))

        grid.addWidget(QLabel("Nom complet :"), 0, 0)
        grid.addWidget(self.input_nom, 0, 1)
        grid.addWidget(QLabel("Téléphone :"), 1, 0)
        grid.addWidget(self.input_tel, 1, 1)
        grid.addWidget(QLabel("Email :"), 2, 0)
        grid.addWidget(self.input_email, 2, 1)
        grid.addWidget(QLabel("Adresse :"), 3, 0)
        grid.addWidget(self.input_adresse, 3, 1)

        layout.addLayout(grid)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "nom": self.input_nom.text().strip(),
            "telephone": self.input_tel.text().strip(),
            "email": self.input_email.text().strip() or None,
            "adresse": self.input_adresse.text().strip() or None
        }


# =========================================================
# PAGE ADMINISTRATION PRINCIPALE
# =========================================================
class AdministrationPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.users = []
        self.clients = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        container.setStyleSheet("background-color: #FFFFFF;")
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(30, 25, 30, 30)
        content_layout.setSpacing(24)

        # En-tête
        header_layout = QVBoxLayout()
        titre = QLabel("Administration")
        titre.setStyleSheet("font-size: 26px; font-weight: 800; color: #0F172A;")
        sous_titre = QLabel("Gestion des utilisateurs et des clients de l'atelier.")
        sous_titre.setStyleSheet("font-size: 13px; color: #64748B;")
        header_layout.addWidget(titre)
        header_layout.addWidget(sous_titre)
        content_layout.addLayout(header_layout)

        # =========================================================
        # SECTION 1 : UTILISATEURS / TECHNICIENS
        # =========================================================
        users_group = QGroupBox("01. Gestion des Utilisateurs")
        users_layout = QVBoxLayout(users_group)
        users_layout.setContentsMargins(16, 20, 16, 16)
        users_layout.setSpacing(14)

        form_u_frame = QFrame()
        form_u_frame.setObjectName("subCardFrame")
        form_u_layout = QGridLayout(form_u_frame)
        form_u_layout.setContentsMargins(12, 12, 12, 12)

        self.u_nom = QLineEdit()
        self.u_nom.setPlaceholderText("Nom complet...")

        self.u_email = QLineEdit()
        self.u_email.setPlaceholderText("Email...")

        self.u_tel = QLineEdit()
        self.u_tel.setPlaceholderText("Téléphone...")

        self.u_password = QLineEdit()
        self.u_password.setPlaceholderText("Mot de passe...")
        self.u_password.setEchoMode(QLineEdit.Password)

        self.u_role = QComboBox()
        self.u_role.addItems(["Technicien", "Administrateur", "Réceptionniste"])

        self.btn_add_user = QPushButton("+ Ajouter")
        self.btn_add_user.setObjectName("btnPrimary")
        self.btn_add_user.setCursor(Qt.PointingHandCursor)
        self.btn_add_user.clicked.connect(self.create_user_api)

        # Formulaire utilisateurs sur 2 lignes pour intégrer tous les champs
        form_u_layout.addWidget(QLabel("Nom :"), 0, 0)
        form_u_layout.addWidget(self.u_nom, 0, 1)
        form_u_layout.addWidget(QLabel("Email :"), 0, 2)
        form_u_layout.addWidget(self.u_email, 0, 3)
        form_u_layout.addWidget(QLabel("Tél :"), 1, 0)
        form_u_layout.addWidget(self.u_tel, 1, 1)
        form_u_layout.addWidget(QLabel("Mot de passe :"), 1, 2)
        form_u_layout.addWidget(self.u_password, 1, 3)
        form_u_layout.addWidget(QLabel("Rôle :"), 0, 4)
        form_u_layout.addWidget(self.u_role, 0, 5)
        form_u_layout.addWidget(self.btn_add_user, 1, 4, 1, 2)

        users_layout.addWidget(form_u_frame)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Nom", "Email", "Téléphone", "Rôle", "Actions"])
        self.configure_table(self.users_table)

        hdr_u = self.users_table.horizontalHeader()
        hdr_u.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr_u.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr_u.setSectionResizeMode(2, QHeaderView.Stretch)
        hdr_u.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr_u.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr_u.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        users_layout.addWidget(self.users_table)
        content_layout.addWidget(users_group)

        # =========================================================
        # SECTION 2 : CLIENTS
        # =========================================================
        clients_group = QGroupBox("02. Répertoire Clients")
        clients_layout = QVBoxLayout(clients_group)
        clients_layout.setContentsMargins(16, 20, 16, 16)
        clients_layout.setSpacing(14)

        form_c_frame = QFrame()
        form_c_frame.setObjectName("subCardFrame")
        form_c_layout = QGridLayout(form_c_frame)
        form_c_layout.setContentsMargins(12, 12, 12, 12)

        self.c_nom = QLineEdit()
        self.c_nom.setPlaceholderText("Nom complet...")

        self.c_tel = QLineEdit()
        self.c_tel.setPlaceholderText("Téléphone...")

        self.c_email = QLineEdit()
        self.c_email.setPlaceholderText("Email...")

        self.c_adresse = QLineEdit()
        self.c_adresse.setPlaceholderText("Adresse...")

        self.btn_add_client = QPushButton("+ Ajouter")
        self.btn_add_client.setObjectName("btnSuccess")
        self.btn_add_client.setCursor(Qt.PointingHandCursor)
        self.btn_add_client.clicked.connect(self.create_client_api)

        form_c_layout.addWidget(QLabel("Nom :"), 0, 0)
        form_c_layout.addWidget(self.c_nom, 0, 1)
        form_c_layout.addWidget(QLabel("Tél :"), 0, 2)
        form_c_layout.addWidget(self.c_tel, 0, 3)
        form_c_layout.addWidget(QLabel("Email :"), 1, 0)
        form_c_layout.addWidget(self.c_email, 1, 1)
        form_c_layout.addWidget(QLabel("Adresse :"), 1, 2)
        form_c_layout.addWidget(self.c_adresse, 1, 3)
        form_c_layout.addWidget(self.btn_add_client, 1, 4)

        clients_layout.addWidget(form_c_frame)

        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(6)
        self.clients_table.setHorizontalHeaderLabels(["ID", "Nom", "Téléphone", "Email", "Adresse", "Actions"])
        self.configure_table(self.clients_table)

        hdr_c = self.clients_table.horizontalHeader()
        hdr_c.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr_c.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr_c.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr_c.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr_c.setSectionResizeMode(4, QHeaderView.Stretch)
        hdr_c.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        clients_layout.addWidget(self.clients_table)
        content_layout.addWidget(clients_group)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self._apply_styles()
        self.load_all_data()

    def configure_table(self, table):
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setMinimumHeight(200)

    def _apply_styles(self):
        self.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #0F172A;
                border: 1px solid #E2E8F0; border-radius: 10px;
                background-color: #FFFFFF; margin-top: 10px; padding-top: 12px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; background-color: #FFFFFF; }
            QFrame#subCardFrame { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; }
            
            QLineEdit, QComboBox { 
                background-color: #FFFFFF; border: 1px solid #CBD5E1; 
                border-radius: 6px; padding: 6px 10px; font-size: 13px; color: #0F172A;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #2563EB; }
            
            QComboBox QAbstractItemView {
                background-color: #FFFFFF; color: #0F172A;
                selection-background-color: #2563EB; selection-color: #FFFFFF;
            }

            /* BOUTON D'AJOUT BLEU */
            QPushButton#btnPrimary { 
                background-color: #2563EB; 
                color: #000b00; 
                font-size: 13px;
                font-weight: 700; 
                border: 1px solid black; 
                border-radius: 6px; 
                padding: 8px 16px; 
            }
            QPushButton#btnPrimary:hover { 
                background-color: #0000FF; 
            }
            
            /* BOUTON D'AJOUT VERT */
            QPushButton#btnSuccess { 
                background-color: #16A34A; 
                color: #000b00; 
                font-size: 13px;
                font-weight: 700; 
                border: 1px solid black; 
                border-radius: 6px; 
                padding: 8px 16px; 
            }
            QPushButton#btnSuccess:hover { 
                background-color: #0000FF; 
            }
        """)

    def load_all_data(self):
        self.load_users()
        self.load_clients()

    # =========================================================
    # LOGIQUE UTILISATEURS
    # =========================================================
    def load_users(self):
        try:
            res = requests.get(f"{API_URL}/utilisateurs/", timeout=10)
            if res.ok:
                self.users = res.json()
                self.display_users()
        except Exception as err:
            print("[ADMIN] Erreur utilisateurs:", err)

    def display_users(self):
        self.users_table.setRowCount(0)
        for u in self.users:
            row = self.users_table.rowCount()
            self.users_table.insertRow(row)

            u_id = u.get("id")
            self.users_table.setItem(row, 0, QTableWidgetItem(str(u_id)))
            self.users_table.setItem(row, 1, QTableWidgetItem(str(u.get("nom", "-"))))
            self.users_table.setItem(row, 2, QTableWidgetItem(str(u.get("email", "-"))))
            self.users_table.setItem(row, 3, QTableWidgetItem(str(u.get("telephone") or "-")))
            self.users_table.setItem(row, 4, QTableWidgetItem(str(u.get("role", "-"))))

            # Boutons Icônes (Modifier / Supprimer)
            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(4)

            btn_edit = QPushButton("✎")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.setStyleSheet("background: #E0F2FE; color: #0284C7; border: 1px solid #BAE6FD; border-radius: 4px; font-weight: bold; padding: 4px 8px;")
            btn_edit.clicked.connect(lambda checked=False, user=u: self.edit_user_api(user))

            btn_del = QPushButton("🗑")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setStyleSheet("background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; border-radius: 4px; font-weight: bold; padding: 4px 8px;")
            btn_del.clicked.connect(lambda checked=False, uid=u_id: self.delete_user_api(uid))

            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_del)
            self.users_table.setCellWidget(row, 5, action_widget)

    def create_user_api(self):
        nom = self.u_nom.text().strip()
        email = self.u_email.text().strip()
        tel = self.u_tel.text().strip() or None
        pwd = self.u_password.text().strip()
        role = self.u_role.currentText()

        if not nom or not email or not pwd:
            QMessageBox.warning(self, "Champs requis", "Le nom, l'email et le mot de passe sont obligatoires.")
            return

        payload = {
            "nom": nom,
            "email": email,
            "telephone": tel,
            "password": pwd,
            "role": role
        }
        try:
            res = requests.post(f"{API_URL}/utilisateurs/", json=payload, timeout=10)
            if res.ok:
                self.u_nom.clear()
                self.u_email.clear()
                self.u_tel.clear()
                self.u_password.clear()
                self.load_users()
                QMessageBox.information(self, "Succès", "Utilisateur créé.")
            else:
                QMessageBox.warning(self, "Erreur", res.text)
        except Exception as err:
            QMessageBox.critical(self, "Erreur Réseau", str(err))

    def edit_user_api(self, user):
        dialog = EditUserDialog(user, self)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_data()
            u_id = user.get("id")
            try:
                res = requests.put(f"{API_URL}/utilisateurs/{u_id}", json=updated_data, timeout=10)
                if res.ok:
                    self.load_users()
                    QMessageBox.information(self, "Succès", "Utilisateur mis à jour.")
                else:
                    QMessageBox.warning(self, "Erreur", res.text)
            except Exception as err:
                QMessageBox.critical(self, "Erreur Réseau", str(err))

    def delete_user_api(self, user_id):
        if QMessageBox.question(self, "Confirmation", "Supprimer cet utilisateur ?", QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        try:
            res = requests.delete(f"{API_URL}/utilisateurs/{user_id}", timeout=10)
            if res.ok:
                self.load_users()
        except Exception as err:
            QMessageBox.critical(self, "Erreur Réseau", str(err))

    # =========================================================
    # LOGIQUE CLIENTS
    # =========================================================
    def load_clients(self):
        try:
            res = requests.get(f"{API_URL}/clients/", timeout=10)
            if res.ok:
                self.clients = res.json()
                self.display_clients()
        except Exception as err:
            print("[ADMIN] Erreur clients:", err)

    def display_clients(self):
        self.clients_table.setRowCount(0)
        for c in self.clients:
            row = self.clients_table.rowCount()
            self.clients_table.insertRow(row)

            c_id = c.get("id")
            self.clients_table.setItem(row, 0, QTableWidgetItem(str(c_id)))
            self.clients_table.setItem(row, 1, QTableWidgetItem(str(c.get("nom", "-"))))
            self.clients_table.setItem(row, 2, QTableWidgetItem(str(c.get("telephone", "-"))))
            self.clients_table.setItem(row, 3, QTableWidgetItem(str(c.get("email") or "-")))
            self.clients_table.setItem(row, 4, QTableWidgetItem(str(c.get("adresse") or "-")))

            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(4)

            btn_edit = QPushButton("✎")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.setStyleSheet("background: #E0F2FE; color: #0284C7; border: 1px solid #BAE6FD; border-radius: 4px; font-weight: bold; padding: 4px 8px;")
            btn_edit.clicked.connect(lambda checked=False, client=c: self.edit_client_api(client))

            btn_del = QPushButton("🗑")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setStyleSheet("background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; border-radius: 4px; font-weight: bold; padding: 4px 8px;")
            btn_del.clicked.connect(lambda checked=False, cid=c_id: self.delete_client_api(cid))

            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_del)
            self.clients_table.setCellWidget(row, 5, action_widget)

    def create_client_api(self):
        nom = self.c_nom.text().strip()
        tel = self.c_tel.text().strip()
        email = self.c_email.text().strip() or None
        adresse = self.c_adresse.text().strip() or None

        if not nom or not tel:
            QMessageBox.warning(self, "Champs requis", "Le nom et le téléphone sont obligatoires.")
            return

        payload = {"nom": nom, "telephone": tel, "email": email, "adresse": adresse}
        try:
            res = requests.post(f"{API_URL}/clients/", json=payload, timeout=10)
            if res.ok:
                self.c_nom.clear()
                self.c_tel.clear()
                self.c_email.clear()
                self.c_adresse.clear()
                self.load_clients()
                QMessageBox.information(self, "Succès", "Client créé.")
            else:
                QMessageBox.warning(self, "Erreur", res.text)
        except Exception as err:
            QMessageBox.critical(self, "Erreur Réseau", str(err))

    def edit_client_api(self, client):
        dialog = EditClientDialog(client, self)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_data()
            c_id = client.get("id")
            try:
                res = requests.put(f"{API_URL}/clients/{c_id}", json=updated_data, timeout=10)
                if res.ok:
                    self.load_clients()
                    QMessageBox.information(self, "Succès", "Client mis à jour.")
                else:
                    QMessageBox.warning(self, "Erreur", res.text)
            except Exception as err:
                QMessageBox.critical(self, "Erreur Réseau", str(err))

    def delete_client_api(self, client_id):
        if QMessageBox.question(self, "Confirmation", "Supprimer ce client ?", QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        try:
            res = requests.delete(f"{API_URL}/clients/{client_id}", timeout=10)
            if res.ok:
                self.load_clients()
        except Exception as err:
            QMessageBox.critical(self, "Erreur Réseau", str(err))