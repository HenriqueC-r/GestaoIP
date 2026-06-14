import time
import subprocess
import platform
import logging
import threading

from datetime import datetime
from database import salvar_evento
import telegram

estado_dispositivos = {}
_stop_event = threading.Event()


def registrar(mensagem):
    logging.info(mensagem)


def separador():
    registrar("=" * 56)


def registrar_alerta(titulo, linhas):
    registrar("")
    registrar("!" * 56)
    registrar(titulo)
    registrar("-" * 56)

    for rotulo, valor in linhas:
        registrar(f"{rotulo:<14} {valor}")

    registrar("!" * 56)
    registrar("")


def ping_host(ip):
    sistema = platform.system().lower()

    if sistema == "windows":
        comando = ["ping", "-n", "1", "-w", "1000", ip]
    else:
        comando = ["ping", "-c", "1", "-W", "1", ip]

    resultado = subprocess.run(
        comando,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return resultado.returncode == 0


def dentro_do_horario(config):
    if config.get("monitorar_24h", False):
        return True

    agora = datetime.now().time()

    inicio = datetime.strptime(config["monitorar_inicio"], "%H:%M").time()
    fim = datetime.strptime(config["monitorar_fim"], "%H:%M").time()

    if inicio <= fim:
        return inicio <= agora <= fim

    return agora >= inicio or agora <= fim


def verificar_dispositivo(dispositivo, config, callback=None):
    nome = dispositivo["nome"]
    ip = dispositivo["ip"]
    tipo = dispositivo.get("tipo", "desconhecido").upper()

    if ip not in estado_dispositivos:
        estado_dispositivos[ip] = {
            "falhas": 0,
            "offline": False,
            "offline_desde": None
        }

    estado = estado_dispositivos[ip]
    resposta = ping_host(ip)

    # =========================
    # ONLINE
    # =========================
    if resposta:
        registrar(f"  [OK]     {nome} ({ip})")

        if estado["offline"]:
            tempo_offline = datetime.now() - estado["offline_desde"]
            tempo_formatado = str(tempo_offline).split(".")[0]

            mensagem = (
                f"✅ ONLINE [{tipo}]\n\n"
                f"Cliente: {config['cliente']}\n"
                f"Nome: {nome}\n"
                f"IP: {ip}\n"
                f"Tempo offline: {tempo_formatado}"
            )

            registrar_alerta(
                f"✅ ONLINE [{tipo}]",
                [
                    ("Cliente:", config["cliente"]),
                    ("Nome:", nome),
                    ("IP:", ip),
                    ("Offline por:", tempo_formatado),
                ],
            )

            salvar_evento(nome, ip, "ONLINE")

            telegram_ok = telegram.enviar(config["telegram"]["chat_id"], mensagem)

            if callback:
                callback(nome, ip, "ONLINE", telegram_ok)

            estado["offline"] = False
            estado["offline_desde"] = None

        else:
            if callback:
                callback(nome, ip, "ONLINE", False)

        estado["falhas"] = 0

    # =========================
    # OFFLINE
    # =========================
    else:
        estado["falhas"] += 1

        registrar(
            f"  [FALHA]  {nome} ({ip})"
            f" - {estado['falhas']}/{config['falhas_para_alerta']}"
        )

        if (
            estado["falhas"] >= config["falhas_para_alerta"]
            and not estado["offline"]
        ):
            estado["offline"] = True
            estado["offline_desde"] = datetime.now()
            detectado = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

            mensagem = (
                f"🚨 OFFLINE [{tipo}]\n\n"
                f"Cliente: {config['cliente']}\n"
                f"Nome: {nome}\n"
                f"IP: {ip}\n"
                f"Detectado: {detectado}"
            )

            registrar_alerta(
                f"🚨 OFFLINE [{tipo}]",
                [
                    ("Cliente:", config["cliente"]),
                    ("Nome:", nome),
                    ("IP:", ip),
                    ("Detectado:", detectado),
                ],
            )

            salvar_evento(nome, ip, "OFFLINE")

            telegram_ok = telegram.enviar(config["telegram"]["chat_id"], mensagem)

            if callback:
                callback(nome, ip, "OFFLINE", telegram_ok)

        elif estado["offline"]:
            if callback:
                callback(nome, ip, "OFFLINE", False)

        else:
            if callback:
                callback(nome, ip, "AGUARDANDO", False)


def parar():
    _stop_event.set()


def monitorar(config, callback=None):
    _stop_event.clear()

    registrar("")
    separador()
    registrar("GestaoIP - Monitoramento iniciado")
    separador()
    registrar(f"Cliente:       {config['cliente']}")
    registrar(f"Equipamentos:  {len(config['equipamentos'])}")
    registrar(f"Intervalo:     {config['intervalo_verificacao']} segundos")
    registrar(f"Alertar após:  {config['falhas_para_alerta']} falhas seguidas")
    registrar("")

    while not _stop_event.is_set():
        if dentro_do_horario(config):
            separador()
            registrar(
                f"Verificação iniciada às "
                f"{datetime.now().strftime('%H:%M:%S')}"
            )
            registrar("-" * 56)

            for dispositivo in config["equipamentos"]:
                verificar_dispositivo(dispositivo, config, callback)

            registrar("")

        else:
            separador()
            registrar(
                f"{datetime.now().strftime('%H:%M:%S')} - "
                f"Fora do horário de monitoramento"
            )
            registrar("")

        _stop_event.wait(timeout=config["intervalo_verificacao"])