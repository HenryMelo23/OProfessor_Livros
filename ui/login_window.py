from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
    QPushButton, QLabel, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from pathlib import Path
import json
from core.sync_utils import sync_critical_files

# Importa a função de utilidade para descriptografia
from core.encryption_utils import decrypt_token_from_file

PERFIS_CRIPTOGRAFADOS_PATH = "users.bin" 
AUTH_TOKEN_PATH = "auth_token.bin"

class LoginWindow(QWidget):
    PERFIS_CRIPTOGRAFADOS_PATH = "users.bin"
    AUTH_TOKEN_PATH = "auth_token.bin"
    
    # Mapeamento estático dos códigos para os nomes completos (para o commit)
    # 🚨 ESTE MAPA DEVE SER MANTIDO SINCRONIZADO COM OS PERFIS CRIPTOGRAFADOS
    NOME_PARA_COMMIT = {
        "101": "Isabela Silva", 
        "202": "Luis Ferreira"
        # Adicione outros perfis base aqui
    }

    def __init__(self, app_ref):
        super().__init__()
        self.app_ref = app_ref
        self.perfis_cadastrados = None # Dicionário {código: senha}
        self.load_profiles()
        self._check_and_sync_files()
        self.setup_ui()

    def load_profiles(self):
        """Carrega e descriptografa o dicionário de perfis do arquivo users.bin."""
        try:
            # 1. Descriptografa a string JSON do arquivo
            perfis_json_str = decrypt_token_from_file(self.PERFIS_CRIPTOGRAFADOS_PATH)
            
            # 2. Converte para dicionário Python
            self.perfis_cadastrados = json.loads(perfis_json_str) 
            print("✅ Perfis de usuário descriptografados com sucesso.")
            
        except FileNotFoundError:
            QMessageBox.critical(self, "Erro Crítico", 
                                 "❌ Arquivo de perfis (users.bin) não encontrado. Execute o script de geração.")
        except Exception as e:
            QMessageBox.critical(self, "Erro de Segurança", 
                                 f"❌ Falha ao carregar ou descriptografar perfis. Verifique a CHAVE de criptografia. Erro: {e}")
    def _check_and_sync_files(self):
        """Método para chamar o sync na inicialização."""
        files_to_check = [
            LoginWindow.PERFIS_CRIPTOGRAFADOS_PATH,
            LoginWindow.AUTH_TOKEN_PATH
        ]
        sync_critical_files(files_to_check)

    def setup_ui(self):
        self.setWindowTitle("Login - Controle de Catálogo")
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Acesso do Funcionário")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        form = QFormLayout()
        
        # Campo para o Código Único de Login
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Código Único Ex: 101") 
        self.input_codigo.setMaxLength(3) 
        
        # Campo para a Senha do Perfil
        self.input_senha = QLineEdit()
        self.input_senha.setEchoMode(QLineEdit.Password)
        
        form.addRow("Código de Login:", self.input_codigo)
        form.addRow("Senha do Perfil:", self.input_senha)
        
        layout.addLayout(form)

        # Botão de Login
        self.btn_login = QPushButton("Acessar Sistema")
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)

    def handle_login(self):
        codigo = self.input_codigo.text().strip()
        senha_digitada = self.input_senha.text().strip() 

        if not self.perfis_cadastrados: 
            return
        if codigo not in self.perfis_cadastrados:
            QMessageBox.critical(self, "Falha", "Código de login ou senha incorreta.")
            return

        perfil_selecionado = self.perfis_cadastrados[codigo]
        
        # Garante que a senha correta é uma string limpa e sem espaços
        senha_correta = str(perfil_selecionado.get("senha", "")).strip() 
        
        # 2. Verifica a senha
        if senha_digitada == senha_correta:
            # Autenticação bem-sucedida!
            
            # 🚨 REMOÇÃO DA LÓGICA MANUAL DE ATRIBUIÇÃO DE ESTADO
            # O código anterior estava tentando definir:
            # self.app_ref.logged_user_profile = perfil_selecionado
            # self.app_ref.logged_user_code = codigo
            # self.app_ref.current_user = nome_completo
            # ISSO FOI INCORPORADO NO NOVO MÉTODO AUTHENTICATE_USER

            # 💡 SOLUÇÃO: Passar o CÓDIGO (chave) e o PERFIL (valor) para o método centralizado.
            self.app_ref.authenticate_user(codigo, perfil_selecionado) 
        else:
            QMessageBox.critical(self, "Falha", "Código de login ou senha incorreta.")