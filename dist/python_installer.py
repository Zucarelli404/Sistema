import os
import sys
import subprocess
import urllib.request
import time
import shutil
import tempfile

# Obtém o caminho da área de trabalho do usuário
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
working_dir = os.path.join(desktop_path, "cabare_painel")

# Verifica se a pasta existe
if not os.path.exists(working_dir):
    print(f"Erro: A pasta {working_dir} não foi encontrada.")
    sys.exit(1)

os.chdir(working_dir)  # Muda para o diretório desejado

def is_python_installed(version="3.12.1"):
    try:
        output1 = subprocess.check_output(["python", "--version"], stderr=subprocess.STDOUT).decode("utf-8").strip()
        output2 = subprocess.check_output(["py", "--version"], stderr=subprocess.STDOUT).decode("utf-8").strip()
        return version in output1 or version in output2
    except Exception:
        return False

def download_python_installer(url, filename):
    print("Baixando o instalador do Python...")
    try:
        if os.path.exists(filename):
            os.remove(filename)  # Remove o arquivo existente se necessário
        urllib.request.urlretrieve(url, filename)
        print("Download concluído.")
        return True
    except Exception as e:
        print(f"Erro ao baixar o Python: {e}")
        return False

def install_python(installer_path):
    print("Instalando Python...")
    try:
        subprocess.run([installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1", "ForceInstall=1"], check=True)
        print("Instalação concluída. Pode ser necessário reiniciar o sistema.")
        return True
    except Exception as e:
        print(f"Erro na instalação do Python: {e}")
        return False

def main():
    # URL do instalador correto (EXE e não MSI)
    python_url = "https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe"

    # Diretório temporário
    temp_dir = tempfile.gettempdir()

    # Caminho para salvar o instalador
    installer_path = os.path.join(temp_dir, "python-3.12.1-amd64.exe")

    # Verifica se o Python já está instalado
    if not is_python_installed():
        if download_python_installer(python_url, installer_path):
            if install_python(installer_path):
                os.remove(installer_path)  # Remove o instalador após a instalação
                time.sleep(5)  # Aguarda um tempo antes de prosseguir
            else:
                print("Falha na instalação do Python.")
                sys.exit(1)
        else:
            print("Falha no download do instalador.")
            sys.exit(1)

if __name__ == "__main__":
    main()