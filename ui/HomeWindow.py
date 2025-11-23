from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QFrame, QHeaderView, QMessageBox
)
import os
import requests
from ui.filter_window import FilterWindow
from PyQt5.QtCore import Qt, QTimer # 💡 Adicionar QTimer para feedback visual
from PyQt5.QtGui import QPixmap
# Importa o módulo secrets para a nova funcionalidade de ADM, se estiver sendo usado aqui
# from core.book_manager import BookManager # Não é necessário importar aqui, mas a classe App o usa

class HomeWindow(QWidget):
    def __init__(self, app_ref):
        super().__init__()
        self.app_ref = app_ref
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Gerenciador de Livros - O Professor")

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, 10)


        titulo = QLabel("Catálogo de Livros")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(titulo)

        busca_layout = QHBoxLayout()

        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("Buscar livro por título ou autor...")
        
        self.busca_input.returnPressed.connect(self.buscar)

        botao_buscar = QPushButton("Buscar")
        botao_buscar.clicked.connect(self.buscar)

        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.clicked.connect(self.abrir_filtro)

        busca_layout.addWidget(self.busca_input)
        busca_layout.addWidget(botao_buscar)
        busca_layout.addWidget(self.btn_filtrar)

        left_layout.addLayout(busca_layout)


        # Tabela com 6 Colunas
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        # Cabeçalhos atualizados para refletir o loop de carregamento
        self.tabela.setHorizontalHeaderLabels(["Título", "Autor", "Sinopse", "Característica", "Preço", "Disponível"]) 
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Garante que a tabela se ajuste
        self.tabela.setSelectionBehavior(self.tabela.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        left_layout.addWidget(self.tabela)

        
        botoes_layout = QHBoxLayout()

        self.btn_editar = QPushButton("Editar Livro")
        self.btn_add = QPushButton("Adicionar Livro")
        self.btn_sync = QPushButton("Sincronizar GitHub")
        self.btn_perfil = QPushButton("Meu Perfil") 
        self.btn_gerenciar_usuarios = QPushButton("Gerenciar Usuários (ADM)")

        self.btn_perfil.setStyleSheet("background-color: #3498db; color: white;")
        self.btn_gerenciar_usuarios.setStyleSheet("background-color: #e67e22; color: white;")

        botoes_layout.addWidget(self.btn_add)
        botoes_layout.addWidget(self.btn_editar)
        botoes_layout.addWidget(self.btn_sync)
        botoes_layout.addWidget(self.btn_perfil)
        botoes_layout.addWidget(self.btn_gerenciar_usuarios)

        left_layout.addLayout(botoes_layout)

        # Conectando ações
        self.btn_add.clicked.connect(self.abrir_add)
        self.btn_editar.clicked.connect(self.abrir_editar)
        self.btn_sync.clicked.connect(self.abrir_sync)
        self.btn_perfil.clicked.connect(self.abrir_perfil)
        self.btn_gerenciar_usuarios.clicked.connect(self.app_ref.go_user_management)

        # Direita: painel de detalhes
        self.painel_detalhes = QFrame()
        self.painel_detalhes.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout()
        self.painel_detalhes.setLayout(right_layout)
        main_layout.addWidget(self.painel_detalhes, 1)
        self.painel_detalhes.setFixedHeight(460)


        # Capa do livro
        self.label_capa = QLabel()
        self.label_capa.setFixedSize(200, 300)
        self.label_capa.setStyleSheet("border: 1px solid gray;")
        self.label_capa.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.label_capa, alignment=Qt.AlignCenter) # Ajusta alinhamento

        # Título e autor
        self.label_titulo = QLabel("Título")
        self.label_titulo.setWordWrap(True)
        self.label_titulo.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(self.label_titulo)

        self.label_autor = QLabel("Autor")
        right_layout.addWidget(self.label_autor)


        self.label_data = QLabel("Data de adição: Há muito tempo")
        right_layout.addWidget(self.label_data)

        right_layout.addStretch()
  

        self.tabela.itemSelectionChanged.connect(self.atualizar_painel)


    
    def abrir_filtro(self):
        self.janela_filtro = FilterWindow(self)
        self.janela_filtro.show()

    def buscar(self):
        texto = self.busca_input.text().lower().strip()
        
        # Garante que o manager existe
        if not hasattr(self.app_ref, 'manager') or self.app_ref.manager is None:
            QMessageBox.critical(self, "Erro", "Manager não inicializado.")
            return

        livros = self.app_ref.manager.livros
        resultado = []

        if not texto:
            self.carregar_livros(livros)
            return

        for l in livros:
            titulo = l.get("titulo", "").lower()
            autor = l.get("autor", "").lower()

            if texto in titulo or texto in autor:
                resultado.append(l)

        self.carregar_livros(resultado)


    def abrir_add(self):
        print("Abrindo tela de adicionar livro...")
        self.app_ref.go_add_book()

    def abrir_editar(self):
        print("Abrindo tela de edição do livro...")
        self.app_ref.go_edit_book()

    def abrir_sync(self):
        """
        Dispara a sincronização manual.
        """
        print("Disparando sincronização manual do catálogo com o GitHub...")
        
        if not hasattr(self.app_ref, 'manager') or self.app_ref.manager is None:
            QMessageBox.critical(self, "Erro", "Manager não inicializado.")
            return
            
        original_text = self.btn_sync.text()
        self.btn_sync.setText("Sincronizando...")
        self.btn_sync.setEnabled(False)

        try:
            # Retorna True se houve pull e a lista de livros foi atualizada.
            atualizado = self.app_ref.manager.initial_sync_on_startup() 
            
            if atualizado:
                print("Sincronização (Pull) concluída com sucesso!")
                self.carregar_livros(self.app_ref.manager.livros) 
                self.btn_sync.setText("Atualizado!")
            else:
                print("✅ Catálogo já estava sincronizado com o remoto.")
                self.btn_sync.setText("Já Sincronizado")

        except Exception as e:
            print(f"❌ Erro crítico durante a sincronização: {e}")
            QMessageBox.critical(self, "Erro de Sincronização", f"Falha: {e}")
            self.btn_sync.setText("Erro de Sync!")
            
        finally:
            QTimer.singleShot(2000, lambda: self._restore_sync_button(original_text))

    def abrir_perfil(self):
        """Dispara a transição para a tela de Perfil."""
        print("Abrindo tela de configurações de perfil...")
        self.app_ref.go_profile()

    def _restore_sync_button(self, text):
        """Método auxiliar para restaurar o botão de sync."""
        self.btn_sync.setText(text)
        self.btn_sync.setEnabled(True)


    def carregar_livros(self, lista_livros):
        self.tabela.setRowCount(len(lista_livros))

        for i, livro in enumerate(lista_livros):
            # 💡 Garante que as chaves usadas correspondem ao esperado:
            self.tabela.setItem(i, 0, QTableWidgetItem(livro.get('titulo', '')))
            self.tabela.setItem(i, 1, QTableWidgetItem(livro.get('autor', '')))
            self.tabela.setItem(i, 2, QTableWidgetItem(livro.get('sinopse', '')))
            self.tabela.setItem(i, 3, QTableWidgetItem(livro.get('caracteristica', '')))
            self.tabela.setItem(i, 4, QTableWidgetItem(livro.get('preco', '0,00')))
            self.tabela.setItem(i, 5, QTableWidgetItem("Sim" if livro.get('disponivel', False) else "Indisponivel"))
    
        self._check_privileges() # Garante que os privilégios sejam checados após o carregamento


    def _check_privileges(self):
        """
        Verifica o cargo do usuário logado e ajusta a visibilidade dos botões.
        """
        profile = self.app_ref.logged_user_profile
        # Acesso seguro ao cargo. Se não houver perfil, assume-se Funcionario.
        cargo = profile.get("cargo", "Funcionario") if profile else "Funcionario"

        is_admin = cargo == "ADM"
        
        self.btn_gerenciar_usuarios.setVisible(is_admin)
        self.btn_sync.setVisible(is_admin or cargo == "Gestor")
        self.btn_add.setVisible(True) # Visível para todos por padrão
        self.btn_editar.setVisible(True) # Visível para todos por padrão


    def aplicar_filtros(self, filtros):
        # Garante que o manager existe
        if not hasattr(self.app_ref, 'manager') or self.app_ref.manager is None:
            QMessageBox.critical(self, "Erro", "Manager não inicializado.")
            return

        livros = self.app_ref.manager.livros
        resultado = []

        for l in livros:
            ok = True

            # Disponibilidade
            if filtros["disponivel"] == "Disponível":
                if not l.get("disponivel", False):
                    ok = False

            elif filtros["disponivel"] == "Indisponível":
                if l.get("disponivel", True):
                    ok = False

            # Autor
            if filtros["autor"]:
                if filtros["autor"].lower() not in l.get("autor", "").lower():
                    ok = False

            # Característica
            if filtros["caracteristica"]:
                if filtros["caracteristica"].lower() not in l.get("caracteristica", "").lower():
                    ok = False

            # --- PREÇO ---
            preco_min_filtro = filtros["preco_min"] / 100
            preco_max_filtro = filtros["preco_max"] / 100

            preco_str = l.get("preco", "0").replace("R$", "").replace(",", ".")
            try:
                preco_livro = float(preco_str)
            except ValueError:
                preco_livro = 0.0 # Caso o formato do preço seja inválido
                
            if not (preco_min_filtro <= preco_livro <= preco_max_filtro):
                ok = False

            if ok:
                resultado.append(l)

        self.carregar_livros(resultado)

    def limpar_filtros(self):
        if hasattr(self.app_ref, 'manager') and self.app_ref.manager:
            self.carregar_livros(self.app_ref.manager.livros)


    
    def atualizar_painel(self):
        selecionados = self.tabela.selectedItems()
        if not selecionados:
            self.label_capa.clear()
            self.label_capa.setText("Sem capa")
            self.label_titulo.setText("")
            self.label_autor.setText("")
            self.label_data.setText("")
            return

        linha = selecionados[0].row()

        titulo = self.tabela.item(linha, 0).text()
        autor = self.tabela.item(linha, 1).text()

        # Garante que o manager existe antes de buscar
        if not hasattr(self.app_ref, 'manager') or self.app_ref.manager is None:
            return

        livro = next((l for l in self.app_ref.manager.livros if l["titulo"] == titulo), None)
        
        data = livro.get("data_adicao", "Desconhecida") if livro else "Desconhecida"

        self.label_titulo.setText(titulo)
        self.label_autor.setText(autor)
        self.label_data.setText(f"Adicionado em: {data}")

        # Capa
        capa_path = f"imagens/{titulo}.png"

        if os.path.exists(capa_path):
            pixmap = QPixmap(capa_path)
            self.label_capa.setPixmap(
                pixmap.scaled(self.label_capa.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.label_capa.setText("Sem capa")


    def baixar_capa(self, titulo):
        url = f"https://raw.githubusercontent.com/HenryMelo23/OProfessor_Livros/main/imagens/{titulo.replace(' ', '%20')}.png"
        caminho = f"imagens/{titulo}.png"

        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(caminho, "wb") as f:
                    f.write(r.content)
                return True
        except:
            pass
        return False