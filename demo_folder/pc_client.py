import psutil
import time
import json
import socket
def get_stats():
    stats={
        "cpu": psutil.cpu_percent(),
        "memory":psutil.virtual_memory().percent,
        "disk":psutil.disk_usage("/").percent,
        "battery":psutil.sensors_battery().percent
    }
    return stats

HOST='127.0.0.1'
PORT=5000

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((HOST,PORT))

while True:
    data=get_stats()
    client.sendall((json.dumps(data) + "\n").encode())
    print("Sent:",data)
    time.sleep(5)