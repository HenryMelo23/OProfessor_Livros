# app/app.py

from PyQt5.QtWidgets import QStackedWidget
from ui.HomeWindow import HomeWindow
from ui.AddBookWindow import AddBookWindow
from ui.EditBookWindow import EditBookWindow
from ui.login_window import LoginWindow 
from core.book_manager import BookManager 
from ui.ProfileWindow import ProfileWindow
from ui.UserManagementWindow import UserManagementWindow # 💡 Importa a nova tela de ADM


class App(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        self.current_user = None         # Nome completo para commits
        self.logged_user_profile = None  # Dicionário COMPLETO do perfil (inclui 'cargo')
        self.logged_user_code = None     # Código de login (Ex: "101")
        self.manager = None      # Manager será inicializado após o login
        
        # 1. Inicializa o Widget de Login e o define como a tela inicial
        self.login = LoginWindow(self)
        self.addWidget(self.login)
        self.setCurrentWidget(self.login)

        # 2. Inicializa as outras janelas
        self.profile = ProfileWindow(self)
        self.addWidget(self.profile)
        
        self.home = HomeWindow(self)
        self.addWidget(self.home)
        
        self.add_book = AddBookWindow(self)
        self.addWidget(self.add_book)
        
        self.edit_book = EditBookWindow(self)
        self.addWidget(self.edit_book)

        # 💡 NOVO: Inicializa a tela de Gerenciamento de Usuários (ADM)
        self.user_management = UserManagementWindow(self)
        self.addWidget(self.user_management)


    def authenticate_user(self, user_code, user_profile):
        """
        Método chamado pela LoginWindow após autenticação BEM-SUCEDIDA.
        Define as variáveis de estado do App e chama show_home.
        """
        self.logged_user_code = user_code
        self.logged_user_profile = user_profile
        # Usa o nome para commits/UI
        self.current_user = user_profile.get("nome", f"Usuário {user_code}") 
        
        self.show_home()


    def show_home(self):
        """
        Chamado APÓS a autenticação bem-sucedida ou ao voltar.
        Inicializa o Manager e carrega os dados.
        """
        
        # 1. 💡 Instancia o Gerenciador de Livros (COM Atraso)
        if self.manager is None:
            print("Iniciando Manager e checagem de sincronização remota...")
            # 💡 Ajuste contundente: BookManager é inicializado com o nome do usuário logado
            self.manager = BookManager(self.current_user) 
            
            # 2. Executa a Sincronização Otimizada (Com Atraso)
            self.manager.initial_sync_on_startup() 
        
        # 3. Carrega os livros (garantidamente atualizados)
        if self.manager:
            self.home.carregar_livros(self.manager.livros)
        
        # 4. Libera o acesso para a HomeWindow
        self.setCurrentWidget(self.home)


    def go_add_book(self):
        self.setCurrentWidget(self.add_book)

    def go_edit_book(self):
        # Lógica de edição
        if self.manager is None: return # Segurança
        
        selecionados = self.home.tabela.selectedItems()
        if selecionados:
            linha = selecionados[0].row()
            livro_titulo = self.home.tabela.item(linha, 0).text()
            
            # 💡 Melhor prática: Buscar o livro completo no manager
            livro_completo = self.manager.get_livro_by_titulo(livro_titulo) 

            # Usa o objeto livro completo se o método existir
            livro_a_editar = livro_completo if livro_completo else {
                 "titulo": livro_titulo,
                 "autor": self.home.tabela.item(linha, 1).text(),
                 "sinopse": self.home.tabela.item(linha, 2).text(),
                 "tema": self.home.tabela.item(linha, 3).text(),
                 "preco": self.home.tabela.item(linha, 4).text(),
            }
            
            self.edit_book.carregar_livro(livro_a_editar)
            self.setCurrentWidget(self.edit_book)
            
    def go_profile(self):
        print("Abrindo tela de configurações de perfil...") 
        self.profile.load_profile_data() 
        self.setCurrentWidget(self.profile)

    def go_sync(self):
        print("A sincronização manual será tratada na HomeWindow.")
        
    def go_user_management(self): # 💡 NOVO MÉTODO DE TRANSIÇÃO (ADM)
        """Dispara a transição para a tela de Gerenciamento de Usuários (ADM)."""
        print("Abrindo tela de gerenciamento de usuários...")
        self.user_management.load_profiles() # Garante que os dados estejam frescos
        self.setCurrentWidget(self.user_management)