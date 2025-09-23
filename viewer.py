import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime

conn=sqlite3.connect("usage_log.db")
c=conn.cursor()

# reading data into pandas dataframe
df = pd.read_sql_query("SELECT * FROM usage_log", conn)
df["timestamp"] = pd.to_datetime(df["timestamp"])

df['date'] = df['timestamp'].dt.date

daily_stats=df.groupby("date").agg({
    "cpu":["mean","max","min"],
    "memory":["mean","max","min"],
    "disk":["mean","max","min"],
    "battery":["mean","max","min"]
}).reset_index()

daily_stats.columns=["date","cpu_mean","cpu_max","cpu_min","memory_mean","memory_max","memory_min","disk_mean","disk_max","disk_min","battery_mean","battery_max","battery_min"]
print(daily_stats)

# c.execute("SELECT * FROM usage_log")
# rows=c.fetchall()

# for row in rows:
#     print(row)

plt.figure(figsize=(12,6))
plt.plot(df['timestamp'],df['cpu'],label="CPU %")
plt.plot(df['timestamp'],df['memory'],label="Memory %")
plt.plot(df['timestamp'],df['disk'],label="Disk %")
plt.plot(df['timestamp'],df['battery'],label="Battery %")
plt.xlabel("Time")
plt.ylabel("Usage %")
plt.title("System Usage")
plt.legend()
plt.tight_layout()
plt.show()

one_week= pd.Timestamp.now()-pd.Timedelta(days=7)
last_week=df[df['timestamp'] >= one_week]

avg_cpu= last_week['cpu'].mean()
peak_cpu= last_week['cpu'].max()

avg_memory = last_week['memory'].mean()
peak_memory = last_week['memory'].max()

avg_disk = last_week['disk'].mean()
peak_disk = last_week['disk'].max()

avg_battery = last_week['battery'].mean()
peak_battery = last_week['battery'].max()

print(f"Weekly Summary (last 7 days):")
print(f"Average CPU Usage: {avg_cpu:.2f}%, Peak CPU Usage: {peak_cpu:.2f}%")
print(f"Average Memory Usage: {avg_memory:.2f}%, Peak Memory Usage: {peak_memory:.2f}%")
print(f"Average Disk Usage: {avg_disk:.2f}%, Peak Disk Usage: {peak_disk:.2f}%")
print(f"Average Battery Usage: {avg_battery:.2f}%, Peak Battery Usage: {peak_battery:.2f}%")

plt.savefig("weekly_usage.png")

# Machine Learning aspect
df['hour'] = df['timestamp'].dt.hour

# local time
df['local_time']=df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
df['hour_local'] = df['local_time'].dt.hour

# CPU usage analysis

cpu_spikes=df[df['cpu'] > 85]

if not cpu_spikes.empty:
    most_common_hour = cpu_spikes['hour_local'].mode()[0]
    print(f"Most common hour for CPU spikes: {most_common_hour}:00 hours")
else:
    print("No CPU spikes detected in the last week.")

# Memory Usage analysis

avg_memory = df['memory'].mean()
peak_memory = df['memory'].max()
print(f"Average Memory Usage: {avg_memory:.2f}%")
print(f"Peak Memory Usage: {peak_memory:.2f}%")
if avg_memory > 85: 
    print("Average memory usage is high → consider upgrading RAM or closing background apps")
else:
    print("Memory usage is within normal range")
    
mem_spikes = df[df['memory'] > 90]
if not mem_spikes.empty:
    most_common_mem_hour = mem_spikes['hour_local'].mode()[0]
    print(f"Most memory spikes occur around {most_common_mem_hour}:00 hours")


conn.close()