import json


def carregar_config():
    with open("data/config.json", "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)