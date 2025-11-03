import sqlite3

DB_PATH = "pc_server/data/brother_eye.db"

def init_db():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_log (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu REAL,
                memory REAL,
                disk REAL,
                battery REAL
            )
        """)
        conn.commit()
    except Exception as e:
        print("Error initializing DB:", e)
    finally:
        if conn:
            conn.close()

def insert_stats(cpu, memory, disk, battery):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usage_log (cpu, memory, disk, battery) VALUES (?, ?, ?, ?)",
            (cpu, memory, disk, battery)
        )
        conn.commit()
    except Exception as e:
        print("Error inserting stats:", e)
    finally:
        if conn:
            conn.close()
