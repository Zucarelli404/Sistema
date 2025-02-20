import os
import subprocess
import sys
import webbrowser

# Define o diretório base onde os arquivos estão localizados
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "cabare_painel")

# Caminho para os arquivos
requirements_path = os.path.join(BASE_DIR, "requirements.txt")
app_path = os.path.join(BASE_DIR, "app.py")

# Garante que estamos no diretório correto
os.chdir(BASE_DIR)

# Instala os requisitos
print("Instalando os requisitos...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], check=True)

# Executa o app
print("Iniciando o aplicativo...")
subprocess.Popen([sys.executable, app_path])

# Aguarda um tempo para garantir que o servidor inicie
import time
print("Aguardando o servidor iniciar...")
time.sleep(5)

# Abre o navegador automaticamente
url = "http://127.0.0.1:5000"
print(f"Abrindo {url} no navegador...")
webbrowser.open(url)
