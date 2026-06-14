import sys
import json
import logging

from logger_setup import configurar_logs
from database import criar_banco
from paths import CONFIG_PATH


def carregar_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = json.load(f)

    validar_config(config)
    return config


def validar_config(config):
    campos_obrigatorios = [
        "cliente",
        "telegram",
        "intervalo_verificacao",
        "falhas_para_alerta",
        "equipamentos",
    ]

    for campo in campos_obrigatorios:
        if campo not in config:
            raise ValueError(f"Campo obrigatório ausente no config.json: {campo}")

    if "chat_id" not in config["telegram"]:
        raise ValueError("Campo obrigatório ausente no config.json: telegram.chat_id")

    if config["intervalo_verificacao"] <= 0:
        raise ValueError("intervalo_verificacao deve ser maior que zero")

    if config["falhas_para_alerta"] <= 0:
        raise ValueError("falhas_para_alerta deve ser maior que zero")

    if not config["equipamentos"]:
        raise ValueError("Adicione pelo menos um equipamento no config.json")

    for posicao, equipamento in enumerate(config["equipamentos"], start=1):
        if "nome" not in equipamento or "ip" not in equipamento:
            raise ValueError(
                f"Equipamento {posicao} precisa ter os campos nome e ip"
            )


def modo_terminal():
    from monitor import monitorar

    configurar_logs()

    try:
        config = carregar_config()
        criar_banco()
        monitorar(config)
    except FileNotFoundError as erro:
        logging.error("Arquivo de configuração não encontrado: %s", erro.filename)
    except (json.JSONDecodeError, ValueError) as erro:
        logging.error("Configuração inválida: %s", erro)
    except KeyboardInterrupt:
        logging.info("Monitoramento encerrado pelo usuário.")


def modo_ui():
    from ui import iniciar
    iniciar()


if __name__ == "__main__":
    if "--terminal" in sys.argv:
        modo_terminal()
    else:
        modo_ui()