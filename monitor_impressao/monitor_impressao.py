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
from datetime import datetime

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FALHA_BEFORE = os.path.join(BASE_DIR, "falhabefore")
FALHA_AFTER = os.path.join(BASE_DIR, "falhaafter")
LOG_PATH = os.path.join(BASE_DIR, "monitor.log")

ACAO = None
DESTINO = None
ADOBE_PATH_CUSTOM = None
CONFIG_EMAIL = {}

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    linha = f"{timestamp} {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(linha + "\n")

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
        log("[ERRO] Configuração de email inválida no ficheiro config.ini")
        sys.exit(1)

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

def imprimir_ficheiro(caminho_ficheiro):
    log(f"[INFO] Novo PDF detectado: {caminho_ficheiro}")
    try:
        if platform.system() == "Windows":
            if ADOBE_PATH_CUSTOM and os.path.exists(ADOBE_PATH_CUSTOM):
                acrobat_path = ADOBE_PATH_CUSTOM
            else:
                caminhos = [
                    r"C:\Program Files\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
                    r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
                    r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
                ]
                acrobat_path = next((p for p in caminhos if os.path.exists(p)), None)

            if not acrobat_path:
                raise FileNotFoundError("Adobe Reader não encontrado.")

            # Inicia o Adobe em modo oculto para impressão
            process = subprocess.Popen([acrobat_path, "/h", "/t", caminho_ficheiro],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)

            # Espera tempo suficiente para spooler aceitar o trabalho
            time.sleep(15)

            # Tenta terminar o processo do Adobe
            process.terminate()
            time.sleep(3)
            # Se ainda estiver aberto, mata com taskkill
            subprocess.run(["taskkill", "/f", "/im", os.path.basename(acrobat_path)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        else:
            subprocess.run(["lp", caminho_ficheiro], check=True)

        log("[INFO] Ficheiro enviado para a impressora.")
        return True

    except Exception as e:
        log(f"[ERRO] Impressão falhou: {e}")
        mover_para_falha(caminho_ficheiro, FALHA_BEFORE)
        return False

def pos_processar_ficheiro(caminho_ficheiro):
    try:
        if ACAO == "delete":
            # Aguarda o Adobe fechar completamente antes de deletar (opcional 5 seg)
            time.sleep(5)
            os.remove(caminho_ficheiro)
            log("[INFO] Ficheiro apagado.")
        elif ACAO == "save":
            if not os.path.exists(DESTINO):
                os.makedirs(DESTINO)
            destino = os.path.join(DESTINO, os.path.basename(caminho_ficheiro))
            shutil.move(caminho_ficheiro, destino)
            log(f"[INFO] Ficheiro movido para: {destino}")
        elif ACAO == "send":
            enviar_email_com_anexo(DESTINO, caminho_ficheiro)
            log(f"[INFO] Ficheiro enviado para o email: {DESTINO}")
    except Exception as e:
        log(f"[ERRO] Pós-processamento falhou: {e}")
        mover_para_falha(caminho_ficheiro, FALHA_AFTER)

def mover_para_falha(caminho, pasta_destino):
    try:
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)
        destino = os.path.join(pasta_destino, os.path.basename(caminho))
        shutil.move(caminho, destino)
        log(f"[INFO] Ficheiro movido para pasta de falhas: {destino}")
    except Exception as e:
        log(f"[ERRO] Falha ao mover para pasta de falhas: {e}")

class ImpressoraHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            time.sleep(1)
            sucesso = imprimir_ficheiro(event.src_path)
            if sucesso:
                pos_processar_ficheiro(event.src_path)

def iniciar_monitoramento():
    log(f"[MONITOR] Pasta monitorada: {BASE_DIR}")
    if ACAO == "save":
        log(f"[AÇÃO] Após imprimir, mover para: {DESTINO}")
    elif ACAO == "delete":
        log("[AÇÃO] Após imprimir, apagar ficheiro.")
    elif ACAO == "send":
        log(f"[AÇÃO] Após imprimir, enviar para: {DESTINO}")
    else:
        log("[AÇÃO] Nenhuma ação adicional.")

    observer = Observer()
    observer.schedule(ImpressoraHandler(), BASE_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("[MONITOR] Encerrado.")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print("Uso:")
        print("  python monitor_impressao.py delete")
        print("  python monitor_impressao.py save <pasta_destino>")
        print("  python monitor_impressao.py send <email_destino>")
        print("  [opcional] -d \"Caminho_para_Adobe.exe\"")
        sys.exit(1)

    if args[0].lower() == "delete":
        ACAO = "delete"
    elif args[0].lower() == "save" and len(args) >= 2:
        ACAO = "save"
        DESTINO = args[1]
    elif args[0].lower() == "send" and len(args) >= 2:
        ACAO = "send"
        DESTINO = args[1]
        carregar_config_email()
    else:
        print("[ERRO] Argumentos inválidos.")
        sys.exit(1)

    if "-d" in args:
        try:
            idx = args.index("-d")
            ADOBE_PATH_CUSTOM = args[idx + 1]
            if not os.path.exists(ADOBE_PATH_CUSTOM):
                log(f"[ERRO] Caminho inválido para o Adobe Reader: {ADOBE_PATH_CUSTOM}")
                sys.exit(1)
        except IndexError:
            log("[ERRO] Caminho para o Adobe não especificado após -d.")
            sys.exit(1)

    iniciar_monitoramento()
