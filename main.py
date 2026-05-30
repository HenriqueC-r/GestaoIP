from config import carregar_config
from database import criar_banco
from monitor import monitorar
from whatsapp import WhatsAppNotifier


def main():

    print("Iniciando monitoramento...")

    criar_banco()

    config = carregar_config()

    whatsapp = WhatsAppNotifier(
        sid="SEU_SID",  # Substitua pelo seu SID da Twilio
        token="SEU_TOKEN",  # Substitua pelo seu Token da Twilio
        from_number="whatsapp:+14155238886" # Número oficial do sandbox do WhatsApp da Twilio
    )

    monitorar(config, whatsapp)


if __name__ == "__main__":
    main()