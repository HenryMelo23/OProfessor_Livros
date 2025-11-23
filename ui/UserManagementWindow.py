import json
import secrets
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, 
    QLineEdit, QLabel, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
# Importa a janela de login para obter o PATH dos arquivos
from ui.login_window import LoginWindow 
# Importa a nova janela de criação (import relativo)
from .NewUserCreationWindow import NewUserCreationWindow 
from core.encryption_utils import decrypt_token_from_file, save_encrypted_token

class UserManagementWindow(QWidget):
    CARGOS_VALIDOS = ["ADM", "Gestor", "Funcionario"]

    def __init__(self, app_ref):
        super().__init__()
        self.app_ref = app_ref
        self.all_profiles = {}
        self.setup_ui()
        self.load_profiles()

    def setup_ui(self):
        self.setWindowTitle("Gerenciamento de Perfis (ADM)")
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # --- Painel Esquerdo: Tabela de Usuários ---
        left_panel = QVBoxLayout()
        self.table_users = QTableWidget()
        self.table_users.setColumnCount(5)
        self.table_users.setHorizontalHeaderLabels(["CÓDIGO", "NOME", "EMAIL", "CARGO", "SENHA"])
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_users.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_users.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_users.itemSelectionChanged.connect(self.load_selected_user_data)
        
        left_panel.addWidget(QLabel("Lista de Usuários:"))
        left_panel.addWidget(self.table_users)

        btn_voltar = QPushButton("Voltar à Home")
        btn_voltar.clicked.connect(self.app_ref.show_home)
        left_panel.addWidget(btn_voltar)

        # --- Painel Direito: Formulário de CRUD ---
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Detalhes do Perfil:"))
        
        form_layout = QFormLayout()
        
        self.lbl_id = QLabel("NOVO (ID gerado auto)")
        self.input_nome = QLineEdit()
        self.input_email = QLineEdit()
        self.input_senha = QLineEdit()
        self.input_senha.setEchoMode(QLineEdit.Password)
        
        self.input_cargo = QComboBox() 
        self.input_cargo.addItems(self.CARGOS_VALIDOS)

        form_layout.addRow("Código (ID):", self.lbl_id)
        form_layout.addRow("Nome:", self.input_nome)
        form_layout.addRow("E-mail:", self.input_email)
        form_layout.addRow("Senha:", self.input_senha)
        form_layout.addRow("Cargo:", self.input_cargo)
        
        right_panel.addLayout(form_layout)

        # Botões de Ação
        crud_layout = QHBoxLayout()
        self.btn_new = QPushButton("Novo Usuário")
        self.btn_save = QPushButton("Salvar Alterações")
        self.btn_delete = QPushButton("Excluir Usuário")

        # Conexões AJUSTADAS: Novo abre o modal, Salvar só edita
        self.btn_new.clicked.connect(self.open_new_user_dialog) 
        self.btn_save.clicked.connect(self.save_user)
        self.btn_delete.clicked.connect(self.delete_user)
        
        self.btn_new.setStyleSheet("background-color: #3498db; color: white;")
        self.btn_save.setStyleSheet("background-color: #2ecc71; color: white;")
        self.btn_delete.setStyleSheet("background-color: #e74c3c; color: white;")

        crud_layout.addWidget(self.btn_new)
        crud_layout.addWidget(self.btn_save)
        crud_layout.addWidget(self.btn_delete)

        right_panel.addLayout(crud_layout)
        right_panel.addStretch(1)

        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)

    def generate_unique_id(self):
        """Método mantido, mas a lógica de geração primária está no modal."""
        while True:
            new_id = str(secrets.randbelow(900) + 100)
            if new_id not in self.all_profiles:
                return new_id

    def load_profiles(self):
        """Carrega e descriptografa o dicionário de perfis e atualiza a tabela."""
        try:
            perfis_json_str = decrypt_token_from_file(LoginWindow.PERFIS_CRIPTOGRAFADOS_PATH)
            self.all_profiles = json.loads(perfis_json_str) 
            self.populate_table()
            self.clear_form()
            print("✅ Gerenciamento de Usuários: Perfis carregados com sucesso.")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro de Carregamento", 
                                 f"❌ Falha ao carregar perfis: {e}")
            self.all_profiles = {}

    def populate_table(self):
        """Preenche a QTableWidget com os dados dos perfis."""
        self.table_users.setRowCount(0)
        row = 0
        for code, profile in self.all_profiles.items():
            self.table_users.insertRow(row)
            
            self.table_users.setItem(row, 0, QTableWidgetItem(code))
            self.table_users.setItem(row, 1, QTableWidgetItem(profile.get("nome", "")))
            self.table_users.setItem(row, 2, QTableWidgetItem(profile.get("email", "")))
            self.table_users.setItem(row, 3, QTableWidgetItem(profile.get("cargo", "Funcionario")))
            self.table_users.setItem(row, 4, QTableWidgetItem("*******")) 
            row += 1

    def clear_form(self):
        """Limpa o formulário para a criação de um novo usuário."""
        self.lbl_id.setText("NOVO (ID gerado auto)")
        self.input_nome.clear()
        self.input_email.clear()
        self.input_senha.clear()
        self.input_cargo.setCurrentIndex(0)
        self.table_users.clearSelection()

    def load_selected_user_data(self):
        """Carrega os dados do usuário selecionado para o formulário de edição."""
        selected_items = self.table_users.selectedItems()
        if not selected_items:
            self.clear_form()
            return

        row = selected_items[0].row()
        user_code = self.table_users.item(row, 0).text()
        
        profile = self.all_profiles.get(user_code)
        if profile:
            self.lbl_id.setText(user_code)
            self.input_nome.setText(profile.get("nome", ""))
            self.input_email.setText(profile.get("email", ""))
            
            cargo = profile.get("cargo", "Funcionario")
            index = self.input_cargo.findText(cargo)
            if index >= 0:
                self.input_cargo.setCurrentIndex(index)
                
            self.input_senha.clear() 

    # --- NOVOS MÉTODOS PARA CRIAÇÃO MODULAR ---
    def open_new_user_dialog(self):
        """Abre o modal para criação de um novo usuário."""
        dialog = NewUserCreationWindow(self.all_profiles, self)
        dialog.profile_created.connect(self.handle_new_profile_creation) 
        dialog.exec_()
        
    def handle_new_profile_creation(self, new_profile_data):
        """Recebe o novo perfil e salva no dicionário principal."""
        user_code = new_profile_data.pop("id")
        
        self.all_profiles[user_code] = new_profile_data
        
        if self._save_all_profiles():
            self.load_profiles()
    # --- FIM DOS NOVOS MÉTODOS ---

    def save_user(self):
        """AJUSTADO: Edita um usuário EXISTENTE. A criação é delegada ao modal."""
        current_id = self.lbl_id.text()
        
        if current_id == "NOVO (ID gerado auto)":
            QMessageBox.warning(self, "Ação Não Permitida", 
                                "Use o botão dedicado **Novo Usuário** para criar cadastros.")
            return
            
        # Lógica de Edição: 
        novo_nome = self.input_nome.text().strip()
        novo_email = self.input_email.text().strip()
        nova_senha = self.input_senha.text().strip()
        novo_cargo = self.input_cargo.currentText() 
        
        if not all([novo_nome, novo_email, novo_cargo]):
            QMessageBox.warning(self, "Erro", "Nome, E-mail e Cargo são obrigatórios.")
            return

        user_code = current_id
        profile = self.all_profiles.get(user_code)
        
        if not profile:
            QMessageBox.critical(self, "Erro", "Perfil de usuário não encontrado para edição.")
            return

        profile["nome"] = novo_nome
        profile["email"] = novo_email
        profile["cargo"] = novo_cargo
        
        if nova_senha:
            profile["senha"] = nova_senha 
            
        action_message = f"Usuário ({user_code}) editado."

        if self._save_all_profiles():
            QMessageBox.information(self, "Sucesso", action_message + " e salvo.")
            self.load_profiles()
        else:
            print("❌ DEBUG: Salvamento na edição falhou.")

    def delete_user(self):
        """Exclui o usuário selecionado."""
        current_id = self.lbl_id.text()
        
        if current_id == "NOVO (ID gerado auto)":
            QMessageBox.warning(self, "Aviso", "Nenhum usuário selecionado para exclusão.")
            return

        if hasattr(self.app_ref, 'logged_user_code') and current_id == self.app_ref.logged_user_code:
            QMessageBox.critical(self, "Restrição", "Você não pode excluir seu próprio perfil ativo.")
            return
            
        user_name = self.all_profiles.get(current_id, {}).get('nome', 'Desconhecido')

        reply = QMessageBox.question(self, 'Confirmar Exclusão',
            f"Tem certeza que deseja EXCLUIR o usuário {current_id} - {user_name}?", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if current_id in self.all_profiles:
                del self.all_profiles[current_id]
                if self._save_all_profiles():
                    self.load_profiles()
                    QMessageBox.information(self, "Sucesso", f"Usuário {current_id} excluído e salvo.")
            else:
                 QMessageBox.warning(self, "Aviso", "Usuário não encontrado na lista para exclusão.")

    def _save_all_profiles(self):
        """Salva o dicionário de perfis de volta no arquivo users.bin criptografado."""
        try:
            perfis_json_atualizado = json.dumps(self.all_profiles)
            save_encrypted_token(perfis_json_atualizado, LoginWindow.PERFIS_CRIPTOGRAFADOS_PATH)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Erro de Segurança", f"Falha CRÍTICA ao salvar o arquivo de perfis: {e}")
            return False