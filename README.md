# Monitor de Impressão Automática de PDFs

Este projeto monitora uma pasta local (onde o script é executado) para detectar novos arquivos PDF. Ao encontrar um arquivo, ele automaticamente o envia para a impressora padrão. Após a impressão, dependendo do comando recebido, o arquivo pode ser apagado, movido para uma pasta específica ou enviado por email. O sistema também lida com falhas, organizando os arquivos problemáticos em pastas dedicadas para análise posterior.

## Técnicas usadas

- Monitoramento do sistema de arquivos em tempo real com [Watchdog](https://python-watchdog.readthedocs.io/en/latest/).
- Impressão via chamadas nativas:
  - Windows: [`os.startfile()`](https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutea) para imprimir diretamente.
  - Linux/macOS: comando [`lp`](https://man7.org/linux/man-pages/man1/lp.1.html).
- Configuração flexível e segura via arquivo [configparser](https://docs.python.org/3/library/configparser.html).
- Envio de email com anexos usando [`smtplib`](https://docs.python.org/3/library/smtplib.html) e [`email.message.EmailMessage`](https://docs.python.org/3/library/email.message.html).
- Organização de arquivos com [`shutil`](https://docs.python.org/3/library/shutil.html), permitindo mover arquivos para diretórios específicos em caso de erro.
- Tratamento simples e direto de argumentos pela biblioteca padrão `sys.argv`.

## Bibliotecas e tecnologias principais

- **[Watchdog](https://pypi.org/project/watchdog/)**: monitoramento cross-platform do sistema de arquivos.
- SMTP nativo para envio de emails — evita dependência em terceiros.
- Configuração via `.ini` — prática e leve, ideal para manter credenciais fora do código.
- Compatibilidade multi-OS com adaptações específicas para cada sistema.

## Instalação rápida

```bash```
# Clone o repositório
git clone <url_do_repositorio>

# Instale as dependências
pip install -r requirements.txt
```/bash```

## Configuração

Edite o arquivo `config.ini` com as credenciais do servidor SMTP e email de origem. Recomenda-se usar senhas de aplicação.

Crie as pastas `falhabefore` e `falhaafter` na raiz do projeto para organizar os arquivos que apresentarem falhas.

## Comandos de execução

```bash```
# Imprimir PDFs e manter os arquivos
python monitor_impressao.py

# Imprimir e apagar arquivos após impressão
python monitor_impressao.py delete

# Imprimir e mover para pasta especificada
python monitor_impressao.py save <caminho_da_pasta>

# Imprimir e enviar por email
python monitor_impressao.py send <email_destino>
```/bash```

## Estrutura do projeto

```plaintext```
monitor_impressao/
├── falhabefore/          # PDFs que falharam na impressão
├── falhaafter/           # PDFs com falha pós-impressão
├── config.ini            # Configurações de email SMTP
├── monitor_impressao.py  # Script principal
├── requirements.txt      # Dependências Python
├── setup.py              # Instalação local como pacote
└── README.md             # Documentação
```/plaintext```

As pastas `falhabefore` e `falhaafter` ajudam a organizar arquivos que apresentaram problemas no processo.
