# GestaoIP

Sistema simples de monitoramento de dispositivos de rede por IP, com alertas via Telegram e registro de eventos em SQLite.

O GestaoIP verifica periodicamente uma lista de equipamentos, detecta falhas consecutivas, registra eventos de queda/retorno e envia alertas para um chat ou grupo do Telegram.

<img width="554" height="669" alt="image" src="https://github.com/user-attachments/assets/92a74ca4-2def-443b-b547-cb61a2b02d1e" />


## Funcionalidades

- Monitoramento por `ping`
- Alertas de equipamento offline
- Alertas de retorno online
- Envio de mensagens para grupo do Telegram
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
│   └── telegram_config.json
└── logs/
```

## Instalação

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

No Windows:

```bat
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --windowed --name GestaoIP --collect-all customtkinter main.py
```

## Configuração

Crie os arquivos reais a partir dos exemplos:

```bash
cp data/config.example.json data/config.json
cp data/telegram_config.example.json data/telegram_config.json
```

No Windows, você pode copiar os arquivos manualmente pelo Explorer.

### `data/telegram_config.json`

```json
{
    "token": "COLE_AQUI_O_TOKEN_DO_BOTFATHER"
}
```

O token é gerado no BotFather do Telegram.

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
        }
    ]
}
```

Campos principais:

- `cliente`: nome do cliente que aparece nas mensagens.
- `telegram.chat_id`: ID do chat ou grupo que recebera os alertas.
- `monitorar_24h`: `true` para monitorar o dia inteiro.
- `monitorar_inicio` e `monitorar_fim`: usados quando `monitorar_24h` for `false`.
- `intervalo_verificacao`: tempo em segundos entre verificações.
- `falhas_para_alerta`: quantidade de falhas seguidas antes de enviar alerta.
- `equipamentos`: lista de dispositivos monitorados.

## Telegram

Para enviar alertas a um grupo:

1. Crie o bot no BotFather.
2. Coloque o token em `data/telegram_config.json`.
3. Adicione o bot no grupo.
4. Desative a privacidade do bot no BotFather usando `/setprivacy` e escolhendo `Disable`.
5. Envie uma mensagem no grupo.
6. Acesse:

```text
https://api.telegram.org/botSEU_TOKEN/getUpdates
```

Procure o campo `chat.id` do grupo. Normalmente ele é negativo, por exemplo:

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

O monitoramento roda em loop até ser encerrado manualmente.

## Gerar executável com PyInstaller

Instale o PyInstaller no ambiente:

```bash
.venv/bin/pip install pyinstaller
```

Gere o executável:

```bash
.venv/bin/pyinstaller --onefile --name GestaoIP main.py
```

No Windows:

```bat
.venv\Scripts\pip install pyinstaller
.venv\Scripts\pyinstaller --onefile --name GestaoIP main.py
```

Depois de gerar, monte a pasta do cliente assim:

```text
GestaoIP/
├── GestaoIP.exe
├── data/
│   ├── config.json
│   └── telegram_config.json
└── logs/
```

O executável procura `data/config.json` e `data/telegram_config.json` na mesma pasta onde ele estiver.

## Segurança

Não publique os arquivos reais abaixo:

- `data/config.json`
- `data/telegram_config.json`
- `data/monitor.db`
- `logs/`

O token do Telegram permite controlar o bot. Se ele vazar, gere um novo token no BotFather.

## Autor

Desenvolvido por Caio.
