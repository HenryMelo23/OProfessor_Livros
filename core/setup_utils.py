import os
import winreg # Biblioteca nativa do Windows para acessar o Registro
import subprocess

# 🚨 SUA CHAVE SECRETA REAL DEVE SER EMBUTIDA AQUI
CHERSES_SECRET_KEY = "kZ9ltKtqZ1ylWfhwOljkL7sRqgiwzubxx4ej2RWwZ8c="
VAR_NAME = "CHERSES_ENC_KEY"

def setup_persistent_env_key():
    """
    Verifica e define a variável de ambiente do usuário no Registro do Windows.
    Isto só precisa ser executado uma vez.
    """
    if os.getenv(VAR_NAME) == CHERSES_SECRET_KEY:
        # A chave já está definida corretamente. Não faça nada.
        return True

    try:
        # Chave do Registro para Variáveis de Ambiente do Usuário Atual (HKEY_CURRENT_USER)
        # HKCU\Environment
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Environment",
            0,
            winreg.KEY_ALL_ACCESS
        )

        # Define o valor da chave
        winreg.SetValueEx(key, VAR_NAME, 0, winreg.REG_SZ, CHERSES_SECRET_KEY)
        winreg.CloseKey(key)

        # 💡 Ação Contundente: Informa o Windows que as variáveis de ambiente mudaram.
        # Isso garante que processos futuros (como o próprio aplicativo) possam ler a nova chave
        # sem precisar reiniciar.
        # Define o valor como 0 para forçar uma atualização nas variáveis
        # (Chave WM_SETTINGCHANGE).
        subprocess.run(
            ['powershell', 'Set-ItemProperty', 'HKCU:\Environment', VAR_NAME, '-Value', CHERSES_SECRET_KEY],
            check=True, capture_output=True, text=True
        )
        
        print(f"✅ Variável de ambiente '{VAR_NAME}' configurada com sucesso para o usuário.")
        return True

    except Exception as e:
        print(f"❌ Erro ao configurar variável de ambiente: {e}")
        # A aplicação ainda pode rodar, mas a sincronização falhará.
        return False