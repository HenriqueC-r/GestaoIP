import sys
from pathlib import Path


def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


BASE_DIR = app_dir()
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_PATH = DATA_DIR / "config.json"
TELEGRAM_CONFIG_PATH = DATA_DIR / "telegram_config.json"
DB_PATH = DATA_DIR / "monitor.db"
