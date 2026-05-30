import sqlite3


def criar_banco():
    conn = sqlite3.connect("data/monitor.db")

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
    conn = sqlite3.connect("data/monitor.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO eventos (equipamento, ip, status)
        VALUES (?, ?, ?)
    """, (equipamento, ip, status))

    conn.commit()
    conn.close()