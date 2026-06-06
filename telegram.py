import json
import logging
import requests

from paths import TELEGRAM_CONFIG_PATH


def carregar_token():
    with TELEGRAM_CONFIG_PATH.open("r", encoding="utf-8") as f:
        telegram = json.load(f)

    return telegram["token"]


def enviar(chat_id, mensagem):

    try:
        token = carregar_token()
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as erro:
        logging.error("Configuração do Telegram inválida: %s", erro)
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        resposta = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": mensagem
            },
            timeout=10
        )
        resposta.raise_for_status()
        return True
    except requests.RequestException as erro:
        logging.error("Falha ao enviar mensagem no Telegram: %s", erro)
        return False
