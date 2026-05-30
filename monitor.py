import time
import subprocess
import platform

from datetime import datetime

from database import salvar_evento

estado_dispositivos = {}


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

    inicio = datetime.strptime(
        config["horario_inicio"],
        "%H:%M"
    ).time()

    fim = datetime.strptime(
        config["horario_fim"],
        "%H:%M"
    ).time()

    return inicio <= agora <= fim


def verificar_dispositivo(dispositivo, config):

    nome = dispositivo["nome"]
    ip = dispositivo["ip"]

    if ip not in estado_dispositivos:

        estado_dispositivos[ip] = {
            "falhas": 0,
            "offline": False,
            "offline_desde": None
        }

    estado = estado_dispositivos[ip]

    resposta = ping_host(ip)

    # ONLINE
    if resposta:

        print(f"[OK] {nome} ({ip})")

        if estado["offline"]:

            tempo_offline = (
                datetime.now() -
                estado["offline_desde"]
            )

            print(
                f"\n✅ EQUIPAMENTO RECUPERADO"
                f"\nNome: {nome}"
                f"\nIP: {ip}"
                f"\nTempo offline: {tempo_offline}\n"
            )

            salvar_evento(
                nome,
                ip,
                "ONLINE"
            )

            estado["offline"] = False
            estado["offline_desde"] = None

        estado["falhas"] = 0

    # OFFLINE
    else:

        estado["falhas"] += 1

        print(
            f"[FALHA {estado['falhas']}/{config['falhas_para_alerta']}] "
            f"{nome} ({ip})"
        )

        if (
            estado["falhas"] >= config["falhas_para_alerta"]
            and not estado["offline"]
        ):

            estado["offline"] = True
            estado["offline_desde"] = datetime.now()

            print(
                f"\n🚨 EQUIPAMENTO OFFLINE"
                f"\nNome: {nome}"
                f"\nIP: {ip}"
                f"\nDetectado: "
                f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            )

            salvar_evento(
                nome,
                ip,
                "OFFLINE"
            )


def monitorar(config):

    print("\nIniciando monitoramento...")

    print(f"Cliente: {config['cliente']}")
    print(
        f"Monitorando "
        f"{len(config['equipamentos'])} equipamentos"
    )
    print(
        f"Intervalo: "
        f"{config['intervalo_verificacao']} segundos"
    )

    print("-" * 50)

    while True:

        if dentro_do_horario(config):

            print(
                f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                f"Verificando equipamentos..."
            )

            for dispositivo in config["equipamentos"]:

                verificar_dispositivo(
                    dispositivo,
                    config
                )

        else:

            print(
                f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                f"Fora do horário de monitoramento"
            )

        time.sleep(
            config["intervalo_verificacao"]
        )