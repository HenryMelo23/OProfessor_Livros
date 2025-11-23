import re
import secrets
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, 
    QVBoxLayout, QMessageBox, QComboBox, QLabel
)
from PyQt5.QtCore import pyqtSignal

class NewUserCreationWindow(QDialog):
    # Sinal emitido ao criar um novo perfil
    profile_created = pyqtSignal(dict) 
    CARGOS_VALIDOS = ["ADM", "Gestor", "Funcionario"]

    def __init__(self, existing_profiles, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Criar Novo Usuário")
        # Referência aos perfis existentes para checagem de ID
        self.existing_profiles = existing_profiles 
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.input_nome = QLineEdit()
        self.input_email = QLineEdit()
        self.input_senha = QLineEdit()
        self.input_senha.setEchoMode(QLineEdit.Password)
        
        self.input_cargo = QComboBox() 
        self.input_cargo.addItems(self.CARGOS_VALIDOS)

        form_layout.addRow("Nome:", self.input_nome)
        form_layout.addRow("E-mail:", self.input_email)
        form_layout.addRow("Senha Inicial:", self.input_senha)
        form_layout.addRow("Cargo:", self.input_cargo)
        
        main_layout.addLayout(form_layout)

        btn_create = QPushButton("Criar e Salvar")
        btn_create.setStyleSheet("background-color: #2ecc71; color: white;")
        btn_create.clicked.connect(self.create_user)
        
        main_layout.addWidget(btn_create)

    def generate_unique_id(self):
        """Gera um ID único de 3 dígitos."""
        while True:
            new_id = str(secrets.randbelow(900) + 100)
            if new_id not in self.existing_profiles:
                return new_id

    def validate_email(self, email):
        """Validação básica de formato de e-mail."""
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def create_user(self):
        nome = self.input_nome.text().strip()
        email = self.input_email.text().strip()
        senha = self.input_senha.text().strip()
        cargo = self.input_cargo.currentText()

        # Validação
        if not all([nome, email, senha]):
            QMessageBox.warning(self, "Erro", "Todos os campos são obrigatórios.")
            return
        if not self.validate_email(email):
            QMessageBox.warning(self, "Erro", "Formato de e-mail inválido.")
            return

        new_id = self.generate_unique_id()
        new_profile = {
            "nome": nome,
            "email": email,
            "senha": senha,
            "cargo": cargo,
            "id": new_id
        }

        self.profile_created.emit(new_profile) 
        QMessageBox.information(self, "Sucesso", f"Novo usuário **{new_id}** criado e enviado para salvamento.")
        self.accept()