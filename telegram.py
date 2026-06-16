import json
import logging
import requests

from datetime import datetime, timedelta
from paths import TELEGRAM_CONFIG_PATH


# ---------------------------------------------------------------------------
# Tipos de dispositivo → emoji + label
# ---------------------------------------------------------------------------

_DEVICE_TYPES = {
    "impressora":   ("🖨",  "IMPRESSORA"),
    "printer":      ("🖨",  "IMPRESSORA"),
    "servidor":     ("🖥",  "SERVIDOR"),
    "server":       ("🖥",  "SERVIDOR"),
    "nas":          ("💾",  "NAS"),
    "switch":       ("🔀",  "SWITCH"),
    "roteador":     ("📡",  "ROTEADOR"),
    "router":       ("📡",  "ROTEADOR"),
    "access point": ("📶",  "ACCESS POINT"),
    "access_point": ("📶",  "ACCESS POINT"),
    "ap":           ("📶",  "ACCESS POINT"),
    "camera":       ("📷",  "CÂMERA"),
    "câmera":       ("📷",  "CÂMERA"),
    "cam":          ("📷",  "CÂMERA"),
    "dvr":          ("📹",  "DVR"),
    "nvr":          ("📹",  "NVR"),
    "computador":   ("💻",  "COMPUTADOR"),
    "pc":           ("💻",  "COMPUTADOR"),
    "workstation":  ("💻",  "WORKSTATION"),
    "notebook":     ("💻",  "NOTEBOOK"),
    "celular":      ("📱",  "CELULAR"),
    "smartphone":   ("📱",  "CELULAR"),
    "telefone":     ("📞",  "TELEFONE"),
    "voip":         ("📞",  "TELEFONE VOIP"),
}

_DEFAULT_DEVICE = ("🔌", "DISPOSITIVO")

SIGNATURE = "\n\n🤖 <b>GestãoIP</b>"


def _device_info(tipo: str) -> tuple:
    """Retorna (emoji, label) para o tipo de dispositivo."""
    key = (tipo or "").strip().lower()
    return _DEVICE_TYPES.get(key, _DEFAULT_DEVICE)


# ---------------------------------------------------------------------------
# Formatação de data/hora e duração
# ---------------------------------------------------------------------------

def _fmt_dt(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M:%S")


def _fmt_duration(seconds: int) -> str:
    td = timedelta(seconds=max(0, seconds))
    h, rem = divmod(int(td.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# ---------------------------------------------------------------------------
# Montagem das mensagens
# ---------------------------------------------------------------------------

def _mensagem_offline(nome: str, ip: str, tipo: str, detectado_em: datetime) -> str:
    emoji, label = _device_info(tipo)
    return (
        f"🚨 <b>EQUIPAMENTO OFFLINE</b>\n"
        f"\n"
        f"{emoji} <b>{nome}</b>   📍 IP: <code>{ip}</code>\n"
        f"\n"
        f"🕐 Detectado: <b>{_fmt_dt(detectado_em)}</b>\n"
        f"⚡ Tipo: <b>{label}</b>"
        f"{SIGNATURE}"
    )


def _mensagem_online(
    nome: str,
    ip: str,
    tipo: str,
    offline_desde: datetime,
    voltou_em: datetime,
) -> str:
    emoji, _ = _device_info(tipo)
    segundos = int((voltou_em - offline_desde).total_seconds())
    return (
        f"✅ <b>EQUIPAMENTO RESTABELECIDO</b>\n"
        f"\n"
        f"{emoji} <b>{nome}</b>   📍 IP: <code>{ip}</code>\n"
        f"\n"
        f"🔴 Caiu: <b>{_fmt_dt(offline_desde)}</b>\n"
        f"🟢 Voltou: <b>{_fmt_dt(voltou_em)}</b>\n"
        f"⏱ Tempo offline: <b>{_fmt_duration(segundos)}</b>"
        f"{SIGNATURE}"
    )


# ---------------------------------------------------------------------------
# Envio
# ---------------------------------------------------------------------------

def carregar_token() -> str:
    with TELEGRAM_CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)["token"]


def enviar(chat_id: str, mensagem: str) -> bool:
    """Envia mensagem em texto puro (legado)."""
    return _post(chat_id, mensagem, parse_mode=None)


def enviar_monitoramento_iniciado(chat_id: str, total_equipamentos: int) -> bool:
    """Envia notificação de que o monitoramento foi iniciado."""
    agora = datetime.now()
    mensagem = (
        f"🟢 <b>MONITORAMENTO INICIADO</b>\n"
        f"\n"
        f"🕐 <b>{_fmt_dt(agora)}</b>\n"
        f"📋 Equipamentos monitorados: <b>{total_equipamentos}</b>"
        f"{SIGNATURE}"
    )
    return _post(chat_id, mensagem, parse_mode="HTML")


def enviar_monitoramento_encerrado(chat_id: str, iniciado_em: datetime) -> bool:
    """Envia notificação de que o monitoramento foi encerrado."""
    agora = datetime.now()
    segundos = int((agora - iniciado_em).total_seconds())
    tempo_ativo = _fmt_duration(segundos)
    mensagem = (
        f"🔴 <b>MONITORAMENTO ENCERRADO</b>\n"
        f"\n"
        f"🕐 <b>{_fmt_dt(agora)}</b>\n"
        f"⏱ Tempo ativo: <b>{tempo_ativo}</b>"
        f"{SIGNATURE}"
    )
    return _post(chat_id, mensagem, parse_mode="HTML")


def enviar_offline(
    chat_id: str,
    nome: str,
    ip: str,
    tipo: str,
    detectado_em: datetime,
) -> bool:
    """Envia alerta de equipamento offline com formatação HTML."""
    mensagem = _mensagem_offline(nome, ip, tipo, detectado_em)
    return _post(chat_id, mensagem, parse_mode="HTML")


def enviar_online(
    chat_id: str,
    nome: str,
    ip: str,
    tipo: str,
    offline_desde: datetime,
    voltou_em: datetime,
) -> bool:
    """Envia alerta de equipamento restabelecido com formatação HTML."""
    mensagem = _mensagem_online(nome, ip, tipo, offline_desde, voltou_em)
    return _post(chat_id, mensagem, parse_mode="HTML")


def _post(chat_id: str, mensagem: str, parse_mode: str | None) -> bool:
    try:
        token = carregar_token()
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as erro:
        logging.error("Configuração do Telegram inválida: %s", erro)
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensagem}
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        resposta = requests.post(url, json=payload, timeout=10)
        if not resposta.ok:
            logging.error(
                "Telegram rejeitou a mensagem (HTTP %s): %s",
                resposta.status_code,
                resposta.text,
            )
            return False
        return True
    except requests.RequestException as erro:
        logging.error("Falha ao enviar mensagem no Telegram: %s", erro)
        return False