# GestãoIP

Sistema de monitoramento de dispositivos de rede por IP, com alertas profissionais via Telegram e registro de eventos em SQLite.

O GestãoIP verifica periodicamente uma lista de equipamentos, detecta falhas consecutivas, registra eventos de queda/retorno e envia alertas formatados para um grupo do Telegram por cliente.

<img width="554" height="669" alt="image" src="https://github.com/user-attachments/assets/92a74ca4-2def-443b-b547-cb61a2b02d1e" />

## Funcionalidades

- Monitoramento por `ping`
- Alertas de equipamento offline e retorno online com formatação HTML
- Emojis automáticos por tipo de equipamento (impressora, switch, câmera, DVR, roteador, etc.)
- Exibe horário da queda, horário do retorno e tempo total offline
- Notificação de monitoramento iniciado e encerrado (com tempo ativo)
- Scroll com mouse na interface gráfica
- Um grupo do Telegram por cliente — nome do cliente não aparece nas mensagens
- Registro de eventos em SQLite
- Configuração por arquivos JSON
- Logs em `logs/gestaoip.log`
- Compatível com Linux e Windows
- Preparado para uso com PyInstaller

## Estrutura

```text
gestaoip/
├── main.py
├── monitor.py
├── database.py
├── telegram.py
├── paths.py
├── ui.py
├── logger_setup.py
├── requirements.txt
├── data/
│   ├── config.json
│   ├── config.example.json
│   ├── telegram_config.json
│   └── telegram_config.example.json
└── logs/
```

## Instalação

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

No Windows:

```bat
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Configuração

Crie os arquivos reais a partir dos exemplos:

```bash
cp data/config.example.json data/config.json
cp data/telegram_config.example.json data/telegram_config.json
```

No Windows, copie os arquivos manualmente pelo Explorer.

### `data/telegram_config.json`

```json
{
    "token": "COLE_AQUI_O_TOKEN_DO_BOTFATHER"
}
```

O token é gerado no BotFather do Telegram. O mesmo token é usado para todos os clientes.

### `data/config.json`

```json
{
    "cliente": "Empresa Exemplo",
    "telegram": {
        "chat_id": "-1001234567890"
    },
    "monitorar_24h": true,
    "monitorar_inicio": "07:00",
    "monitorar_fim": "17:00",
    "intervalo_verificacao": 30,
    "falhas_para_alerta": 3,
    "equipamentos": [
        {
            "nome": "Roteador principal",
            "ip": "192.168.0.1",
            "tipo": "roteador"
        },
        {
            "nome": "Impressora RH",
            "ip": "192.168.0.50",
            "tipo": "impressora"
        }
    ]
}
```

Campos principais:

- `cliente`: nome do cliente (usado nos logs internos).
- `telegram.chat_id`: ID do grupo do Telegram do cliente.
- `monitorar_24h`: `true` para monitorar o dia inteiro.
- `monitorar_inicio` e `monitorar_fim`: usados quando `monitorar_24h` for `false`.
- `intervalo_verificacao`: tempo em segundos entre verificações.
- `falhas_para_alerta`: quantidade de falhas consecutivas antes de enviar alerta.
- `equipamentos`: lista de dispositivos monitorados.

### Tipos de equipamento suportados

| Tipo no JSON   | Emoji | Label          |
|----------------|-------|----------------|
| `roteador`     | 📡    | ROTEADOR       |
| `switch`       | 🔀    | SWITCH         |
| `access point` | 📶    | ACCESS POINT   |
| `impressora`   | 🖨    | IMPRESSORA     |
| `servidor`     | 🖥    | SERVIDOR       |
| `nas`          | 💾    | NAS            |
| `camera`       | 📷    | CÂMERA         |
| `dvr`          | 📹    | DVR            |
| `nvr`          | 📹    | NVR            |
| `computador`   | 💻    | COMPUTADOR     |
| `notebook`     | 💻    | NOTEBOOK       |
| `celular`      | 📱    | CELULAR        |
| `telefone`     | 📞    | TELEFONE       |
| `voip`         | 📞    | TELEFONE VOIP  |

Qualquer outro valor usa 🔌 DISPOSITIVO como padrão.

## Configuração do Telegram

Para enviar alertas a um grupo por cliente:

1. Crie o bot no BotFather e salve o token.
2. Coloque o token em `data/telegram_config.json`.
3. Crie um grupo no Telegram para o cliente e adicione o bot.
4. Desative a privacidade do bot no BotFather com `/setprivacy` → `Disable`.
5. Envie uma mensagem qualquer no grupo.
6. Acesse a URL abaixo para obter o `chat_id`:

```
https://api.telegram.org/botSEU_TOKEN/getUpdates
```

Procure o campo `chat.id` do grupo. Normalmente é negativo:

```json
"chat": {
    "id": -1001234567890,
    "title": "Empresa Exemplo",
    "type": "supergroup"
}
```

Use esse ID em `data/config.json`.

## Execução

```bash
.venv/bin/python main.py
```

No Windows:

```bat
.venv\Scripts\python main.py
```

Para rodar sem interface gráfica (modo terminal):

```bash
.venv/bin/python main.py --terminal
```

## Gerar executável para Windows

O executável deve ser gerado em uma máquina Windows.

```bat
.venv\Scripts\pip install pyinstaller
.venv\Scripts\pyinstaller --onefile --windowed --name GestaoIP --collect-all customtkinter main.py
```

O `.exe` gerado fica em `dist\GestaoIP.exe`.

Monte a pasta do cliente assim:

```text
GestaoIP\
├── GestaoIP.exe
├── data\
│   ├── config.json
│   └── telegram_config.json
└── logs\
```

O executável procura `data/config.json` e `data/telegram_config.json` na mesma pasta onde ele estiver.

## Segurança

Nunca publique os arquivos abaixo — estão no `.gitignore`:

- `data/config.json`
- `data/telegram_config.json`
- `data/monitor.db`
- `logs/`

O token do Telegram permite controlar o bot. Se vazar, gere um novo no BotFather.

## Autor

Desenvolvido por Caio.
