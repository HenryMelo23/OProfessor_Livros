from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
    QPushButton, QLabel, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from core.encryption_utils import decrypt_token_from_file, save_encrypted_token
from ui.login_window import LoginWindow # Para acessar o path do users.bin
import json

class ProfileWindow(QWidget):
    def __init__(self, app_ref):
        super().__init__()
        self.app_ref = app_ref
        self.user_profile = None # Perfil atual logado
        self.user_code = None # Código do usuário logado
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Configurações do Perfil")
        
        layout = QVBoxLayout()
        self.setLayout(layout) # 💡 CORREÇÃO CRÍTICA: Anexa o layout ao widget principal.
        
        titulo = QLabel("Meu Perfil & Configurações de Acesso")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(titulo)

        form = QFormLayout()
        
        # Campos de Informação
        self.lbl_codigo = QLabel("Código: -")
        self.input_nome = QLineEdit()
        self.input_email = QLineEdit()
        
        # Campos de Senha (Sensível)
        self.input_senha_nova = QLineEdit()
        self.input_senha_nova.setEchoMode(QLineEdit.Password)
        self.input_senha_nova.setPlaceholderText("Deixe em branco para não alterar")
        
        self.input_senha_confirm = QLineEdit()
        self.input_senha_confirm.setEchoMode(QLineEdit.Password)
        
        form.addRow(QLabel("Código de Login:"), self.lbl_codigo)
        form.addRow("Nome Completo:", self.input_nome)
        form.addRow("E-mail (Gmail/Outro):", self.input_email)
        form.addRow(QLabel("--- Alterar Senha ---"))
        form.addRow("Nova Senha:", self.input_senha_nova)
        form.addRow("Confirmação:", self.input_senha_confirm)
        
        layout.addLayout(form)
        
        self.btn_salvar = QPushButton("Salvar Alterações no Perfil")
        self.btn_salvar.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px;")
        self.btn_salvar.clicked.connect(self.save_profile)
        
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.clicked.connect(self.app_ref.show_home)
        
        botoes_layout = QHBoxLayout()
        botoes_layout.addWidget(self.btn_salvar)
        botoes_layout.addWidget(self.btn_voltar)
        
        layout.addStretch(1) # Empurra tudo para cima
        layout.addLayout(botoes_layout)
        # O self.setLayout(layout) foi movido para o topo para garantir a renderização.

    def load_profile_data(self):
        """
        Carrega os dados do usuário logado na UI, lendo o estado centralizado no App.
        Chamado pelo App.go_profile()
        """
        
        print("✅ ProfileWindow: Tentando carregar dados do App...")
        
        if not self.app_ref.logged_user_profile:
            print("❌ Erro: Estado do usuário logado não encontrado. Voltando ao login.")
            self.app_ref.setCurrentWidget(self.app_ref.login)
            return

        # Atribui o Perfil (Lendo do App)
        self.user_profile = self.app_ref.logged_user_profile
        self.user_code = self.app_ref.logged_user_code
        
        self.lbl_codigo.setText(self.user_code)
        self.input_nome.setText(self.user_profile.get("nome", ""))
        self.input_email.setText(self.user_profile.get("email", ""))
        
        # Limpa os campos de senha
        self.input_senha_nova.clear()
        self.input_senha_confirm.clear()
        
        print("✅ ProfileWindow: Dados carregados com sucesso. Pronta para exibição.")
        
    def save_profile(self):
        nova_senha = self.input_senha_nova.text()
        confirma_senha = self.input_senha_confirm.text()
        
        novo_nome = self.input_nome.text().strip()
        novo_email = self.input_email.text().strip()
        
        # 1. Validação de Senha
        if nova_senha and nova_senha != confirma_senha:
            QMessageBox.warning(self, "Erro", "A nova senha e a confirmação não coincidem.")
            return

        # 2. Atualiza o dicionário local
        self.user_profile["nome"] = novo_nome
        self.user_profile["email"] = novo_email
        if nova_senha:
            self.user_profile["senha"] = nova_senha
            
        # 3. 🛡️ Atualiza e criptografa o arquivo 'users.bin'
        if not self._update_and_encrypt_all_profiles():
            QMessageBox.critical(self, "Erro de Segurança", "Falha ao salvar o arquivo de perfis. Alterações não persistiram.")
            return
            
        # 4. Atualiza o estado centralizado do App após o salvamento bem-sucedido
        self.app_ref.current_user = novo_nome 
        self.app_ref.logged_user_profile = self.user_profile # Atualiza a referência do App

        QMessageBox.information(self, "Sucesso", "Perfil atualizado e criptografado.")
        self.app_ref.show_home()


    def _update_and_encrypt_all_profiles(self):
        """
        Carrega todos os perfis, atualiza o perfil atual e salva tudo criptografado.
        """
        try:
            # Carrega todos os perfis criptografados
            perfis_json_str = decrypt_token_from_file(LoginWindow.PERFIS_CRIPTOGRAFADOS_PATH)
            all_profiles = json.loads(perfis_json_str)

            # Atualiza APENAS o perfil modificado usando a chave (user_code)
            all_profiles[self.user_code] = self.user_profile
            
            # Criptografa e salva de volta
            perfis_json_atualizado = json.dumps(all_profiles)
            save_encrypted_token(perfis_json_atualizado, LoginWindow.PERFIS_CRIPTOGRAFADOS_PATH)
            
            return True
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao criptografar perfis: {e}")
            return False