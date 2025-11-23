# core/encryption_utils.py

from cryptography.fernet import Fernet
from pathlib import Path
import os
import sys

# 💡 NOTA: O PyInstaller exige que as funções de acesso a arquivos usem caminhos robustos.
def get_resource_path(relative_path):
    """Obtém o caminho correto, mesmo quando empacotado pelo PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(relative_path)


def get_fernet_key() -> bytes:
    """Busca a chave de criptografia na variável de ambiente."""
    key_b64 = os.getenv("CHERSES_ENC_KEY")
    if not key_b64:
        raise ValueError("❌ ERRO CRÍTICO: A variável de ambiente 'CHERSES_ENC_KEY' não foi definida.")
    return key_b64.encode()


def decrypt_token_from_file(file_path: Path) -> str:
    """Carrega a chave e descriptografa o token de um arquivo binário."""
    try:
        key = get_fernet_key()
        f = Fernet(key)
        
        # Usa o caminho robusto para carregar o arquivo
        token_path = get_resource_path(file_path)

        with open(token_path, "rb") as f_in:
            encrypted_data = f_in.read()
        
        # Descriptografa e decodifica o token
        return f.decrypt(encrypted_data).decode()
    
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ ERRO: Arquivo de token criptografado não encontrado em {file_path}")
    except ValueError as e:
        raise ValueError(f"❌ ERRO: Chave inválida ou Token corrompido. {e}")
    except Exception as e:
        # Erro de variável de ambiente, por exemplo.
        raise Exception(f"❌ ERRO INESPERADO ao descriptografar token: {e}")


def save_encrypted_token(token: str, file_path: Path):
    """Função ÚTIL: Cria o arquivo criptografado (uso único)."""
    key = get_fernet_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(token.encode())
    
    with open(file_path, "wb") as f_out:
        f_out.write(encrypted_data)
    print(f"✅ Token criptografado salvo em {file_path}")