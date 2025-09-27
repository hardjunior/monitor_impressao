# Monitor de Impressão Automático

Este projeto é um script Python para monitorar uma pasta, imprimir automaticamente arquivos PDF usando o Adobe Acrobat Reader e realizar uma ação após a impressão (apagar, mover ou enviar por email).

---

## Funcionalidades

- Monitoramento em tempo real da pasta onde o script está rodando.
- Impressão automática dos PDFs detectados via Adobe Acrobat Reader (Windows) ou lp (Linux).
- Opções para após impressão:
  - Apagar o arquivo PDF.
  - Mover para uma pasta destino.
  - Enviar por email para um destinatário configurado.
- Configuração de caminho customizado do Adobe Acrobat Reader via parâmetro `-d`.
- Log básico via terminal.
- Organização de arquivos com falha em pastas específicas.

---

## Como usar

1. Clone ou copie os arquivos para a pasta desejada.

2. Crie um arquivo chamado `config.ini` para configuração do email (se for usar o envio por email):

```ini
[EMAIL]
from = seuemail@exemplo.com
password = sua_senha_de_app_ou_senha_real
smtp_server = smtp.exemplo.com
smtp_port = 587
```

3. Execute o script com uma das opções:

```bash
python monitor_impressao.py delete
python monitor_impressao.py save C:\caminho\para\pasta_destino
python monitor_impressao.py send destinatario@exemplo.com
python monitor_impressao.py send destinatario@exemplo.com -d "C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
```

- O parâmetro `-d` é opcional e indica o caminho para o executável do Adobe Reader caso não esteja no local padrão.

---

## Como funciona

- O script monitora a pasta onde está rodando.
- Ao detectar um PDF novo, ele envia para a impressora via Adobe Reader.
- Após a impressão, realiza a ação escolhida (`delete`, `save` ou `send`).
- Em caso de erro, o arquivo é movido para uma pasta de falhas.

---

## Dependências

- Python 3.x
- watchdog (`pip install watchdog`)

---

## Estrutura de pastas

- monitor_impressao.py  # Script principal
- config.ini            # Configuração do email
- falhabefore/          # PDFs que falharam antes da impressão
- falhaafter/           # PDFs que falharam após impressão

---

## Exemplo de comando

```bash
python monitor_impressao.py send seuemail@exemplo.com -d "C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
```

---
## Observações

- Certifique-se de que o Adobe Acrobat Reader esteja instalado e acessível no caminho especificado.
- O script foi testado em ambientes Windows e Linux, mas pode precisar de ajustes dependendo da configuração do sistema.
- Mantenha o arquivo `config.ini` seguro, especialmente se contiver senhas.

---
## Converter para .exe (Windows)

Para converter o script Python em um executável (.exe) no Windows, você pode usar o `pyinstaller`. Siga os passos abaixo:

1. Instale o `pyinstaller`:

```bash
pip install pyinstaller
```

2. Navegue até a pasta onde está o script `monitor_impressao.py`.

3. Execute o seguinte comando:

```bash
pyinstaller --onefile --windowed monitor_impressao.py
```

4. Após a conclusão, você encontrará o executável na pasta `dist`.
- Para debugar, remova o `--windowed` do comando acima.

---

## Contato

Para dúvidas ou sugestões, entre em contato.