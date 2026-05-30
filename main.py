from config import carregar_config
from database import criar_banco
from monitor import monitorar


def main():

    print("Iniciando monitoramento...")

    criar_banco()

    config = carregar_config()

    monitorar(config)


if __name__ == "__main__":
    main()