import os
from cryptography.fernet import Fernet

# Gera uma chave Fernet aleatória e segura (32 url-safe base64-encoded bytes)
chave_secreta = Fernet.generate_key()

# Imprime a chave gerada. COPIE ESTA CHAVE!
print(chave_secreta.decode())