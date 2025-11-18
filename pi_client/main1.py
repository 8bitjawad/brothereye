# main1.py  (temporary script to populate usage_log.db)

import time
import psutil
from db_manager import init_db, insert_stats

# Initialize DB + table
init_db()

print("📊 Collecting data… Press CTRL + C to stop.")

while True:
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    gpu = 0.0  # or implement GPU logic if you want
    battery = psutil.sensors_battery().percent if psutil.sensors_battery() else 100

    insert_stats(cpu, memory, disk, gpu, battery)

    print(f"Inserted → CPU={cpu}% | MEM={memory}% | DISK={disk}% | BATT={battery}%")
    time.sleep(1)
