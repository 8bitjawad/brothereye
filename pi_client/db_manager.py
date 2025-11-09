# pi_client/db_manager.py
import sqlite3

def init_db():
    conn = sqlite3.connect("usage_log.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS usage_log (
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        cpu REAL,
        memory REAL,
        disk REAL,
        gpu REAL,
        battery REAL
    )
    """)
    conn.commit()
    conn.close()

def insert_stats(cpu, memory, disk, gpu, battery):
    conn = sqlite3.connect("usage_log.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO usage_log (cpu, memory, disk, gpu, battery) VALUES (?, ?, ?, ?, ?)",
        (cpu, memory, disk, gpu, battery)
    )
    conn.commit()
    conn.close()
