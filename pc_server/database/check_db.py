import sqlite3

DB_PATH = "pc-server/data/brother_eye.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in DB:", tables)

cursor.execute("SELECT * FROM usage_log;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
