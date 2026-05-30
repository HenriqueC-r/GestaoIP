from twilio.rest import Client


class WhatsAppNotifier:

    def __init__(self, sid, token, from_number):
        self.client = Client(sid, token)
        self.from_number = from_number

    def enviar(self, numero, mensagem):

        try:
            msg = self.client.messages.create(
                from_=self.from_number,
                body=mensagem,
                to=f"whatsapp:{numero}"
            )

            print(f"[WHATSAPP ENVIADO] SID: {msg.sid}")

        except Exception as e:
            print(f"[ERRO WHATSAPP] {e}")