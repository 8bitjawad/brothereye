import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

def load_data():
    conn=sqlite3.connect("usage_log.db")
    # reading data into pandas dataframe
    df = pd.read_sql_query("SELECT * FROM usage_log", conn)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    conn.close()
    return df

# Function to show matplotlib graphs for weekly usage
def show_graphs(df):
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

    save = input("Do you want to save this plot as 'weekly_usage.png'? (y/n): ")
    if save.lower() == 'y':
        plt.savefig("weekly_usage.png")
        print("Plot saved successfully!")

def show_daily_stats(df):
    df['date'] = df['timestamp'].dt.date
    daily_stats=df.groupby("date").agg({
        "cpu":["mean","max","min"],
        "memory":["mean","max","min"],
        "disk":["mean","max","min"],
        "battery":["mean","max","min"]
    }).reset_index()
    daily_stats.columns=["date","cpu_mean","cpu_max","cpu_min","memory_mean","memory_max","memory_min","disk_mean","disk_max","disk_min","battery_mean","battery_max","battery_min"]
    print("\nDaily Stats:")
    print(daily_stats)

def weekly_summary(df):
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


# Machine Learning aspect
def analyze_usage(df):
    df['hour'] = df['timestamp'].dt.hour
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
    else:
        print("No memory spikes detected in the last week.")

# Linear Regression

def run_prediction(df):
    # Set timestamp as index
    df.set_index('timestamp', inplace=True)

    # Resample hourly
    df_hourly = df.resample('1h').mean()

    # Add CPU next hour
    df_hourly['cpu_next'] = df_hourly['cpu'].shift(-1)
    df_model = df_hourly.dropna().copy()

    # Add hour features
    df_model.loc[:, 'hour'] = df_model.index.hour
    df_model.loc[:, 'hour_local'] = df_model.index.tz_localize('UTC').tz_convert('Asia/Kolkata').hour

    # Features and target
    X = df_model[['cpu','memory','disk','battery','hour','hour_local']]
    y = df_model['cpu_next']

    # Train model
    model_cpu = LinearRegression()
    model_cpu.fit(X, y)

    # Predict next hour CPU
    last_row = pd.DataFrame([df_model[['cpu','memory','disk','battery','hour','hour_local']].iloc[-1].values],
                        columns=['cpu','memory','disk','battery','hour','hour_local'])
    predicted_cpu = model_cpu.predict(last_row)

    print(f"Predicted CPU usage next hour: {predicted_cpu[0]:.2f}%")

    # Future alert
    if predicted_cpu[0] > 90:
        print("Warning: CPU usage predicted to exceed 90% soon!")


def main():
    df = load_data()

    while True:
        print("\n=== System Monitoring Viewer ===")
        print("1. Show usage graphs")
        print("2. Show weekly summary")
        print("3. Run predictive model")
        print("4. Show daily stats")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            show_graphs(df)
        elif choice == '2':
            weekly_summary(df)
        elif choice == '3':
            run_prediction(df)
        elif choice == '4':
            show_daily_stats(df)
        elif choice == '5':
            break
        else:
            print("Invalid choice! Please enter 1-4.")

if __name__ == "__main__":
    main()
