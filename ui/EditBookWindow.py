from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, 
    QPushButton, QHBoxLayout, QLabel, QMessageBox, QFileDialog, 
    QComboBox # QComboBox agora será usado para disponibilidade
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os
import shutil 


class EditBookWindow(QWidget):
    def __init__(self, app_ref):
        super().__init__()
        self.app_ref = app_ref
        self.livro_atual = None
        self.novo_caminho_capa = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Editar Livro - O Professor")

        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Editar Livro")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(titulo)


        form_layout = QFormLayout()

        self.input_titulo = QLineEdit()
        self.input_titulo.setReadOnly(True) 
        
        self.input_autor = QLineEdit()
        self.input_sinopse = QTextEdit()
        self.input_tema = QLineEdit()
        self.input_preco = QLineEdit()
        self.input_preco.setMaxLength(10)
        self.input_preco.setPlaceholderText("Digite apenas números, será formatado em R$")
        self.input_preco.textChanged.connect(self.formatar_preco)
        
        # --- AJUSTE: CAMPO DE DISPONIBILIDADE (QComboBox) ---
        self.select_disponivel = QComboBox()
        self.select_disponivel.addItems(["Disponível", "Indisponível"])
        
        # Seleção de Imagem
        self.btn_selecionar_capa = QPushButton("Trocar Capa (Selecionar Imagem)")
        self.btn_selecionar_capa.clicked.connect(self.selecionar_capa)
        
        self.label_capa_status = QLabel("Capa atual: Nenhuma")


        form_layout.addRow("Título:", self.input_titulo)
        form_layout.addRow("Autor:", self.input_autor)
        form_layout.addRow("Sinopse:", self.input_sinopse)
        form_layout.addRow("Tema:", self.input_tema)
        form_layout.addRow("Preço (R$):", self.input_preco)
        form_layout.addRow("Disponibilidade:", self.select_disponivel) # Novo ComboBox
        form_layout.addRow("Capa Atual:", self.label_capa_status)
        form_layout.addRow("Nova Capa:", self.btn_selecionar_capa)

        layout.addLayout(form_layout)


        botoes_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("Salvar Alterações")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_excluir = QPushButton("Excluir Livro")

        botoes_layout.addWidget(self.btn_salvar)
        botoes_layout.addWidget(self.btn_cancelar)
        botoes_layout.addWidget(self.btn_excluir)
        layout.addLayout(botoes_layout)

        self.btn_salvar.clicked.connect(self.salvar)
        self.btn_cancelar.clicked.connect(self.cancelar)
        self.btn_excluir.clicked.connect(self.excluir)

    def selecionar_capa(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            self, 
            "Selecionar Nova Capa", 
            "", 
            "Arquivos de Imagem (*.png *.jpg *.jpeg)"
        )

        if caminho_arquivo:
            self.novo_caminho_capa = caminho_arquivo
            self.label_capa_status.setText(f"Nova capa selecionada: {os.path.basename(caminho_arquivo)}")
            QMessageBox.information(
                self, 
                "Capa Selecionada", 
                "A nova capa será aplicada ao salvar o livro."
            )
        else:
            self.novo_caminho_capa = None
            self.label_capa_status.setText("Capa atual: Nenhuma alteração")


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

    def carregar_livro(self, livro):
        """Preenche os campos com o livro selecionado e inicializa o estado."""
        self.livro_atual = livro
        self.novo_caminho_capa = None
        
        self.input_titulo.setText(livro.get("titulo", ""))
        self.input_autor.setText(livro.get("autor", ""))
        self.input_sinopse.setText(livro.get("sinopse", ""))
        self.input_tema.setText(livro.get("tema", ""))
        self.input_preco.setText(livro.get("preco", "0,00"))
        
        # --- AJUSTE: Carrega disponibilidade para o ComboBox ---
        disponivel = livro.get("disponivel", False)
        if disponivel:
            self.select_disponivel.setCurrentText("Disponível")
        else:
            self.select_disponivel.setCurrentText("Indisponível")
        
        # Mostra status da capa
        caminho_capa_atual = f"imagens/{livro.get('titulo', '')}.png"
        if os.path.exists(caminho_capa_atual):
            self.label_capa_status.setText(f"Capa atual: {os.path.basename(caminho_capa_atual)}")
        else:
            self.label_capa_status.setText("Capa atual: Não encontrada.")


    def salvar(self):
        if not self.livro_atual:
            return
        
        # Atualiza os dados do livro com os valores dos campos
        self.livro_atual["titulo"] = self.input_titulo.text()
        self.livro_atual["autor"] = self.input_autor.text()
        self.livro_atual["sinopse"] = self.input_sinopse.toPlainText()
        self.livro_atual["tema"] = self.input_tema.text()
        self.livro_atual["preco"] = self.input_preco.text()
        
        # --- AJUSTE: Salva o estado da disponibilidade do ComboBox ---
        status_selecionado = self.select_disponivel.currentText()
        self.livro_atual["disponivel"] = (status_selecionado == "Disponível")


        # Lógica para trocar a imagem
        if self.novo_caminho_capa:
            novo_nome_capa = f"{self.livro_atual['titulo']}.png"
            destino = os.path.join("imagens", novo_nome_capa)
            
            os.makedirs("imagens", exist_ok=True)
            
            try:
                shutil.copy2(self.novo_caminho_capa, destino)
                QMessageBox.information(
                    self, 
                    "Sucesso", 
                    f"A capa do livro foi atualizada e salva como '{novo_nome_capa}'."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Erro ao Salvar Capa", 
                    f"Não foi possível copiar a imagem. Erro: {e}"
                )
                
            self.novo_caminho_capa = None

        # Salva o livro no manager, recarrega a tabela e volta para a Home
        self.app_ref.manager.update_livro(self.livro_atual)
        self.app_ref.home.carregar_livros(self.app_ref.manager.livros)
        
        self.app_ref.home.atualizar_painel() 
        
        self.app_ref.setCurrentWidget(self.app_ref.home)


    def cancelar(self):
        self.app_ref.setCurrentWidget(self.app_ref.home)

    def excluir(self):
        if not self.livro_atual:
            return
        
        resposta = QMessageBox.question(
            self,
            "Confirmação",
            f"Tem certeza que deseja excluir o livro '{self.livro_atual['titulo']}'?\nEsta ação removerá o livro do catálogo.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta == QMessageBox.Yes:
            titulo = self.livro_atual.get('titulo', '')
            caminho_capa = f"imagens/{titulo}.png"
            if os.path.exists(caminho_capa):
                try:
                    os.remove(caminho_capa)
                except Exception as e:
                    print(f"Não foi possível remover o arquivo de capa: {e}")

            self.app_ref.manager.remove_livro(self.livro_atual)
            self.app_ref.home.carregar_livros(self.app_ref.manager.livros)
            self.app_ref.setCurrentWidget(self.app_ref.home)