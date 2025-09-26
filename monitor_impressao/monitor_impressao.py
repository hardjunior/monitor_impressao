import os
import sys
import time
import platform
import shutil
import subprocess
import smtplib
from email.message import EmailMessage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser

# 📁 Diretório atual onde o script está
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🗂️ Pastas de erro
FALHA_BEFORE = os.path.join(BASE_DIR, "falhabefore")
FALHA_AFTER = os.path.join(BASE_DIR, "falhaafter")

# 📦 Argumentos
ACAO = None
DESTINO = None

# 🔐 Configurações do email (lidas de config.ini)
CONFIG_EMAIL = {}

def carregar_config_email():
    config_path = os.path.join(BASE_DIR, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    try:
        CONFIG_EMAIL["from"] = config["EMAIL"]["from"]
        CONFIG_EMAIL["password"] = config["EMAIL"]["password"]
        CONFIG_EMAIL["smtp_server"] = config["EMAIL"]["smtp_server"]
        CONFIG_EMAIL["smtp_port"] = int(config["EMAIL"]["smtp_port"])
    except KeyError:
        print("[ERRO] Configuração de email inválida no ficheiro config.ini")
        sys.exit(1)

# 🖨️ Impressão
def imprimir_ficheiro(caminho_ficheiro):
    print(f"[INFO] Novo PDF detectado: {caminho_ficheiro}")
    try:
        if platform.system() == "Windows":
            os.startfile(caminho_ficheiro, "print")
        else:
            subprocess.run(["lp", caminho_ficheiro], check=True)
        print("[INFO] Ficheiro enviado para a impressora.")
        return True
    except Exception as e:
        print(f"[ERRO] Impressão falhou: {e}")
        mover_para_falha(caminho_ficheiro, FALHA_BEFORE)
        return False

# 🧹 Pós-processamento
def pos_processar_ficheiro(caminho_ficheiro):
    try:
        if ACAO == "delete":
            os.remove(caminho_ficheiro)
            print("[INFO] Ficheiro apagado.")
        elif ACAO == "save":
            if not os.path.exists(DESTINO):
                os.makedirs(DESTINO)
            novo_caminho = os.path.join(DESTINO, os.path.basename(caminho_ficheiro))
            shutil.move(caminho_ficheiro, novo_caminho)
            print(f"[INFO] Ficheiro movido para: {novo_caminho}")
        elif ACAO == "send":
            enviar_email_com_anexo(DESTINO, caminho_ficheiro)
            print(f"[INFO] Ficheiro enviado para o email: {DESTINO}")
    except Exception as e:
        print(f"[ERRO] Pós-processamento falhou: {e}")
        mover_para_falha(caminho_ficheiro, FALHA_AFTER)

# 📧 Enviar email
def enviar_email_com_anexo(destinatario, caminho_anexo):
    msg = EmailMessage()
    msg["Subject"] = "Documento impresso"
    msg["From"] = CONFIG_EMAIL["from"]
    msg["To"] = destinatario
    msg.set_content("Segue em anexo o ficheiro impresso.")

    with open(caminho_anexo, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(caminho_anexo)
        msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

    with smtplib.SMTP(CONFIG_EMAIL["smtp_server"], CONFIG_EMAIL["smtp_port"]) as smtp:
        smtp.starttls()
        smtp.login(CONFIG_EMAIL["from"], CONFIG_EMAIL["password"])
        smtp.send_message(msg)

# 📂 Mover ficheiros com falha
def mover_para_falha(caminho, pasta_destino):
    try:
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)
        destino = os.path.join(pasta_destino, os.path.basename(caminho))
        shutil.move(caminho, destino)
        print(f"[INFO] Ficheiro movido para pasta de falhas: {destino}")
    except Exception as e:
        print(f"[ERRO] Não foi possível mover para pasta de falhas: {e}")

# 👂 Monitor de eventos
class ImpressoraHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            time.sleep(1)
            sucesso = imprimir_ficheiro(event.src_path)
            if sucesso:
                pos_processar_ficheiro(event.src_path)

# 🚀 Monitoramento
def iniciar_monitoramento():
    print(f"[MONITOR] Pasta monitorada: {BASE_DIR}")
    if ACAO == "save":
        print(f"[AÇÃO] Após imprimir, mover para: {DESTINO}")
    elif ACAO == "delete":
        print("[AÇÃO] Após imprimir, apagar ficheiro.")
    elif ACAO == "send":
        print(f"[AÇÃO] Após imprimir, enviar para: {DESTINO}")
    else:
        print("[AÇÃO] Nenhuma ação extra após imprimir.")

    observer = Observer()
    observer.schedule(ImpressoraHandler(), BASE_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MONITOR] Encerrado.")
        observer.stop()
    observer.join()

# ▶️ Main
if __name__ == "__main__":
    # Argumentos
    if len(sys.argv) >= 2:
        arg = sys.argv[1].lower()
        if arg == "delete":
            ACAO = "delete"
        elif arg == "save" and len(sys.argv) >= 3:
            ACAO = "save"
            DESTINO = sys.argv[2]
        elif arg == "send" and len(sys.argv) >= 3:
            ACAO = "send"
            DESTINO = sys.argv[2]
            carregar_config_email()
        else:
            print("[ERRO] Argumentos inválidos.")
            print("Uso:")
            print("  python monitor_impressao.py delete")
            print("  python monitor_impressao.py save <pasta_destino>")
            print("  python monitor_impressao.py send <email_destino>")
            sys.exit(1)

    iniciar_monitoramento()
