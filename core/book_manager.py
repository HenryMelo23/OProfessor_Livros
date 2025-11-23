import json
from pathlib import Path
import subprocess
from git import Repo, GitConfigParser, GitCommandError
from datetime import datetime
import os
from .encryption_utils import decrypt_token_from_file
from .setup_utils import setup_persistent_env_key 
from git.exc import GitCommandError

class BookManager:
    """Gerencia o catálogo de livros e a sincronização com o repositório Git."""
    
    # 💡 Aceita 'user_name' no construtor.
    def __init__(self, user_name, caminho_json="catalogo.json"):
        
        self.user_name = user_name # 💡 CRÍTICO: Armazena o nome para uso no commit
        
        # Configura as variáveis de ambiente para definir o autor do commit
        os.environ['GIT_AUTHOR_NAME'] = user_name
        os.environ['GIT_COMMITTER_NAME'] = user_name
    
        # 1. Executa a configuração de ambiente de forma silenciosa
        setup_persistent_env_key() 
        
        REPO_URL = "https://github.com/HenryMelo23/OProfessor_Livros.git"
        
        # --- PARTE 1: CARREGAMENTO DO TOKEN ---
        try:
            TOKEN = decrypt_token_from_file(Path("auth_token.bin"))
            print("✅ Token de autenticação carregado e descriptografado com sucesso.")
            
            self.repo_auth_url = REPO_URL.replace("https://", f"https://oauth2:{TOKEN}@")
            self.auth_success = True
            
        except Exception as e:
            print(f"❌ AVISO CRÍTICO: Não foi possível carregar o Token. {e}")
            print("A sincronização de push automatizada não funcionará.")
            self.repo_auth_url = REPO_URL
            self.auth_success = False
        
        # --- PARTE 2: INICIALIZAÇÃO DO REPOSITÓRIO E CONFIGURAÇÃO DO REMOTE ---
        
        self.caminho = Path(caminho_json)
        self.repo_dir = self.caminho.parent.resolve()

        # 1. Tenta carregar ou inicializar o Repositório
        try:
            self.repo = Repo(self.repo_dir)
            is_new_repo = False
        except Exception:
            print("🚨 Pasta não é um repositório Git, inicializando...")
            self.repo = Repo.init(self.repo_dir)
            is_new_repo = True

        # 2. CHAMA O SETUP DE REMOTE SEMPRE.
        if self.auth_success or is_new_repo:
            self._setup_remote() 
            
        # --- PARTE 3: CARREGAMENTO DO CATÁLOGO ---
        if not self.caminho.exists():
            self.salvar_livros([])
        self.livros = self.carregar_livros()


    def _setup_remote(self):
        """
        Remove o remote antigo e força a configuração com a URL autenticada.
        """
        
        if 'oauth2' not in self.repo_auth_url:
            print("❌ AVISO: Configuração remota ignorada. URL sem token.")
            return 

        try:
            if 'origin' in [remote.name for remote in self.repo.remotes]:
                self.repo.delete_remote('origin')
                print("✅ Remote 'origin' antigo removido para reconfiguração.")
        except Exception as e:
            pass 

        try:
            self.repo.create_remote('origin', self.repo_auth_url)
            print(f"✅ Remote 'origin' configurado para Push/Pull automático.")
        except GitCommandError as e:
             print(f"❌ Erro ao configurar remote: {e}")
        
    def carregar_livros(self):
        with open(self.caminho, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def salvar_livros(self, lista=None):
        if lista is not None:
            self.livros = lista
        with open(self.caminho, "w", encoding="utf-8") as f:
            json.dump(self.livros, f, ensure_ascii=False, indent=2)

    # --- Lógica de Sincronização Git ---

    def _exec_git_command(self, command, message):
        """Executa um comando Git e lida com erros de forma empática."""
        try:
            result = subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            print(f"✅ Git OK: {message}")
            return True
        
        except subprocess.CalledProcessError as e:
            failed_command = ' '.join(e.cmd)
            print(f"❌ Erro Git ({message}): O comando '{failed_command}' falhou.")
            if e.stderr:
                print(f"  STDERR: {e.stderr.strip()}")
            return False
            
        except FileNotFoundError:
            print("❌ Erro: O comando 'git' não foi encontrado.")
            return False
        
        except subprocess.TimeoutExpired:
            print(f"❌ Erro: O comando Git excedeu o tempo limite de 30 segundos durante: {message}")
            return False
        
        except Exception as e:
            print(f"❌ Erro desconhecido durante a execução do Git: {e}")
            return False

    def save_and_push_catalogue(self, action_type="Atualização"):
        """Salva localmente e executa o push imediato usando GitPython."""
        self.salvar_livros()
        
        try:
            index = self.repo.index
            index.add([str(self.caminho.name)])
            
            # 💡 RASTREABILIDADE: Adiciona o nome do usuário na mensagem de commit
            commit_msg = f"feat: Catálogo atualizado via app - {action_type} por {self.user_name}"
            index.commit(commit_msg)
            print("✅ Git OK: Commitando alteração")
            
            self.repo.remotes.origin.push('main') 
            print("✅ Git OK: Enviando alteração para o GitHub")
            
            return True
        except GitCommandError as e:
            print(f"❌ Erro GitPython durante Push/Commit: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro desconhecido durante o Push: {e}")
            return False

    def initial_sync_on_startup(self):
        """
        Checa se há atualização remota. NÃO EXECUTA PULL para evitar colisão de código.
        Apenas recarrega dados locais se o remoto estiver à frente (assumindo que
        o usuário tem a versão mais recente do catalogo.json).
        """
        print("Iniciando checagem de sincronização remota...")
        
        try:
            origin = self.repo.remotes.origin
            
            # 1. Fetch para obter as referências mais recentes
            origin.fetch()
            print("✅ Git OK: Buscando referências remotas")

            local_commit = self.repo.head.commit
            remote_commit = origin.refs.main.commit 
            
            # Se o remoto tem commits que o local não tem...
            if self.repo.iter_commits(f'{local_commit}..{remote_commit}'):
                print("🚨 Atualização remota de dados (catalogo.json) disponível. Recarregando...")
                
                # Recarrega os dados APENAS do arquivo catalogo.json
                self.livros = self.carregar_livros() # Isso deve ler o arquivo catalogo.json atualizado
                print("✅ Recarga de dados 'livros' concluída.")
                
                # Se a lógica de recarga de dados envolve um pull, precisa ser ajustada.
                # Se 'carregar_livros' apenas lê o arquivo local, isso funciona.

                return True 
            else:
                print("✅ Local e remoto sincronizados. Nenhuma ação necessária.")
                return False

        except Exception as e:
            print(f"❌ Erro na checagem de sincronização: {e}")
            return False

    # --- Métodos de Ação (Ajustados para o Push Imediato) ---
    def get_livro_by_titulo(self, titulo: str):
        """
        Retorna o dicionário de livro completo baseado no título.
        """
        return next(
            (l for l in self.livros if l.get("titulo") == titulo), 
            None
        )
    
    def add_livro(self, livro):
        """Adiciona livro, ordena e faz o push imediato."""
        if "data_adicao" not in livro:
             livro["data_adicao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.livros.append(livro)
        self.livros = sorted(self.livros, key=lambda x: x["titulo"].lower())
        return self.save_and_push_catalogue(action_type="Adição")

    def update_livro(self, livro_atualizado):
        """Atualiza livro e faz o push imediato."""
        for i, l in enumerate(self.livros):
            if l["titulo"] == livro_atualizado["titulo"]:
                self.livros[i] = livro_atualizado
                return self.save_and_push_catalogue(action_type="Edição")
        return False

    def remove_livro(self, livro):
        """Remove livro e faz o push imediato."""
        self.livros = [l for l in self.livros if l["titulo"] != livro["titulo"]]
        return self.save_and_push_catalogue(action_type="Remoção")