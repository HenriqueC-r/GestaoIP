import sqlite3
from paths import DATA_DIR, DB_PATH


def criar_banco():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipamento TEXT,
            ip TEXT,
            status TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def salvar_evento(equipamento, ip, status):
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO eventos (equipamento, ip, status)
        VALUES (?, ?, ?)
    """, (equipamento, ip, status))

    conn.commit()
    conn.close()
