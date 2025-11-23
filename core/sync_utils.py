import requests
from datetime import datetime
from pathlib import Path
import json
from PyQt5.QtWidgets import QMessageBox

# --- CONFIGURAÇÃO DE SINCRONIZAÇÃO (USANDO O REPOSITÓRIO RAW) ---
# O raw.githubusercontent.com é necessário para baixar o conteúdo binário.
REMOTE_CONFIG_BASE_URL = "https://raw.githubusercontent.com/HenryMelo23/OProfessor_Livros/main/" 
LOCAL_TIMESTAMP_FILE = Path("sync_timestamp.json") # Arquivo local para rastrear sincronização

def get_remote_timestamp(file_name):
    """
    Busca a última modificação do arquivo remoto.
    Usaremos a data da resposta como proxy, mas não é 100% confiável no GitHub Raw.
    """
    url = f"{REMOTE_CONFIG_BASE_URL}{file_name}"
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            # Tenta usar o cabeçalho 'Last-Modified' se existir
            last_modified = response.headers.get('Last-Modified')
            if last_modified:
                return datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')
            
            # Alternativa: usa a data do servidor como último recurso, embora menos preciso
            date_header = response.headers.get('Date')
            if date_header:
                return datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S GMT')
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Falha ao obter timestamp remoto para {file_name}: {e}")
    return None

def download_and_replace(file_name):
    """Baixa o arquivo da URL RAW e substitui o local."""
    url = f"{REMOTE_CONFIG_BASE_URL}{file_name}"
    try:
        print(f"📥 Baixando e substituindo: {file_name}")
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Erro se status for 4xx ou 5xx
        
        Path(file_name).write_bytes(response.content)
        return True
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(None, "Erro de Conexão/Download", 
                             f"❌ Falha ao baixar o arquivo crítico **{file_name}**. Verifique a URL e a conexão: {e}")
        return False

def update_local_timestamp(file_name, timestamp):
    """Atualiza o timestamp local no arquivo JSON."""
    data = {}
    if LOCAL_TIMESTAMP_FILE.exists():
        try:
            data = json.loads(LOCAL_TIMESTAMP_FILE.read_text())
        except:
            pass
            
    data[file_name] = timestamp.isoformat()
    LOCAL_TIMESTAMP_FILE.write_text(json.dumps(data, indent=4))

def get_local_timestamp(file_name):
    """Lê o timestamp local do arquivo JSON."""
    if LOCAL_TIMESTAMP_FILE.exists():
        try:
            data = json.loads(LOCAL_TIMESTAMP_FILE.read_text())
            ts_str = data.get(file_name)
            if ts_str:
                return datetime.fromisoformat(ts_str)
        except:
            pass
    return None

def sync_critical_files(files_to_sync):
    """Verifica se há versão mais nova no repositório e sincroniza."""
    synced_count = 0
    for file_name in files_to_sync:
        remote_ts = get_remote_timestamp(file_name)
            
        local_ts = get_local_timestamp(file_name)
        
        # Se não houver timestamp local, ou se o remoto for mais novo
        if not local_ts or (remote_ts and remote_ts > local_ts):
            if download_and_replace(file_name):
                # Se baixou, atualiza o timestamp local (usamos o remoto ou a hora atual)
                update_local_timestamp(file_name, remote_ts or datetime.now())
                synced_count += 1
                
    if synced_count > 0:
        QMessageBox.information(None, "Sincronização Concluída", 
                                f"✅ {synced_count} arquivo(s) crítico(s) atualizado(s) remotamente. Reinicie a aplicação para carregar os novos dados.")
        return True
    return False