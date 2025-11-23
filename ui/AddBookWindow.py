from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from datetime import datetime # Importado para data_adicao

class AddBookWindow(QWidget):
    def __init__(self, app_ref):
        super().__init__()
        self.app_ref = app_ref
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Adicionar Novo Livro - O Professor")

        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Adicionar Livro")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(titulo)


        form_layout = QFormLayout()

        self.input_titulo = QLineEdit()
        self.input_autor = QLineEdit()
        self.input_sinopse = QTextEdit()
        self.input_tema = QLineEdit()
        self.input_preco = QLineEdit()
        self.input_preco.setMaxLength(10)
        self.input_preco.setPlaceholderText("Digite apenas números, será formatado em R$")


        self.input_preco.textChanged.connect(self.formatar_preco)

        form_layout.addRow("Título:", self.input_titulo)
        form_layout.addRow("Autor:", self.input_autor)
        form_layout.addRow("Sinopse:", self.input_sinopse)
        form_layout.addRow("Tema:", self.input_tema)
        form_layout.addRow("Preço (R$):", self.input_preco)

        layout.addLayout(form_layout)


        botoes_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("Salvar")
        self.btn_cancelar = QPushButton("Cancelar")
        botoes_layout.addWidget(self.btn_salvar)
        botoes_layout.addWidget(self.btn_cancelar)
        layout.addLayout(botoes_layout)

        self.btn_salvar.clicked.connect(self.salvar)
        self.btn_cancelar.clicked.connect(self.cancelar)


    def formatar_preco(self):
        texto = ''.join(filter(str.isdigit, self.input_preco.text()))
        if texto == '':
            texto = '0'
        valor = int(texto)
        reais = valor // 100
        centavos = valor % 100
        self.input_preco.blockSignals(True)
        self.input_preco.setText(f"{reais},{centavos:02d}")
        self.input_preco.blockSignals(False)
        self.input_preco.setCursorPosition(len(self.input_preco.text()))


    def salvar(self):
        # Validação Contundente
        if not self.input_titulo.text().strip() or not self.input_autor.text().strip():
            QMessageBox.warning(self, "Dados Incompletos", "Os campos Título e Autor são obrigatórios.")
            return

        # Prepara o objeto Livro
        livro = {
            "titulo": self.input_titulo.text().strip(),
            "autor": self.input_autor.text().strip(),
            "sinopse": self.input_sinopse.toPlainText().strip(),
            "tema": self.input_tema.text().strip(),
            "preco": self.input_preco.text(),
            "disponivel": True, # Assume que todo livro adicionado está disponível inicialmente
            "data_adicao": datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Metadado essencial
        }
        
        print("Livro a adicionar:", livro)

        # 💡 Chamada Inovadora: Adiciona, Salva Localmente E Faz o PUSH AUTOMÁTICO
        sucesso = self.app_ref.manager.add_livro(livro)

        if sucesso:
            # 1. Limpa os campos após o sucesso
            self._limpar_campos()
            
            # 2. Atualiza a HomeWindow com a lista completa e sincronizada
            self.app_ref.home.carregar_livros(self.app_ref.manager.livros)
            
            # 3. Retorna para a tela principal
            self.app_ref.setCurrentWidget(self.app_ref.home)
            QMessageBox.information(self, "Sucesso", "Livro adicionado e sincronizado com o GitHub.")
        else:
            QMessageBox.critical(self, "Erro", "Falha ao adicionar e sincronizar o livro. Verifique o console para logs do Git.")


    def cancelar(self):
        self._limpar_campos()
        self.app_ref.setCurrentWidget(self.app_ref.home)

    def _limpar_campos(self):
        self.input_titulo.clear()
        self.input_autor.clear()
        self.input_sinopse.clear()
        self.input_tema.clear()
        self.input_preco.setText("0,00")