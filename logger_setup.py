import logging
import sys

from paths import LOGS_DIR


def configurar_logs():
    LOGS_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    arquivo = logging.FileHandler(LOGS_DIR / "gestaoip.log", encoding="utf-8")
    arquivo.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    terminal = logging.StreamHandler(sys.stdout)
    terminal.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(arquivo)
    logger.addHandler(terminal)
