import socket
import json
import sqlite3

# Database creation and connection
conn= sqlite3.connect("usage_log.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS usage_log (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, cpu REAL, memory REAL, disk REAL, battery REAL)""")
conn.commit()

# Server setup, currently using localhost for both HOST AND PORT. In future, will change to Raspberry Pi.
HOST='127.0.0.1'
PORT=5000

# Server socket creation and binding. First we create a TCP connection using IPv4 (AF_INET). Then, we bind it to the HOST and PORT.
server= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST,PORT))
server.listen(1)
print("Server listening", PORT)

# Accepting connection from client here. conn_client is the connection object and addr is the address of the client.
conn_client, addr= server.accept()
print("Connected by", addr)

# Receive newline-delimited JSON messages and log them.
try:
    with conn_client:
        # Use a text wrapper to read line-delimited JSON safely.
        with conn_client.makefile('r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    stats = json.loads(line)
                except json.JSONDecodeError as e:
                    print("Failed to decode JSON:", e, "Raw:", line)
                    continue

                print(stats)
                c.execute(
                    "INSERT INTO usage_log (cpu, memory, disk, battery) VALUES (?, ?, ?, ?)",
                    (stats.get('cpu'), stats.get('memory'), stats.get('disk'), stats.get('battery'))
                )
                conn.commit() # data logged and committed to sqlite db
                print("Logged:", stats)
except ConnectionResetError:
    print("Connection was reset by client.")
finally:
    conn.close()

