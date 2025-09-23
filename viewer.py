import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

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
    # Work on a copy to avoid mutating the caller's DataFrame
    df_work = df.copy()

    # Ensure datetime index
    df_work = df_work.set_index('timestamp')

    # Ensure numeric types to avoid pandas aggregation errors if any stray strings appear
    numeric_cols = ['cpu', 'memory', 'disk', 'battery']
    for col in numeric_cols:
        df_work[col] = pd.to_numeric(df_work[col], errors='coerce')

    # Resample hourly and compute mean; numeric_only guards against non-numeric dtypes in newer pandas
    df_hourly = df_work[numeric_cols].resample('1h').mean(numeric_only=True)

    # Add next-hour targets
    df_hourly['cpu_next'] = df_hourly['cpu'].shift(-1)
    df_hourly['memory_next'] = df_hourly['memory'].shift(-1)
    df_hourly['disk_next'] = df_hourly['disk'].shift(-1)
    df_hourly['battery_next'] = df_hourly['battery'].shift(-1)

    # Drop rows with NA created by shift or resampling
    df_model = df_hourly.dropna().copy()
    if df_model.empty:
        print("Not enough data after resampling to run prediction.")
        return None

    # Add hour features (handle both naive and tz-aware indexes)
    df_model.loc[:, 'hour'] = df_model.index.hour
    if df_model.index.tz is None:
        df_model.loc[:, 'hour_local'] = df_model.index.tz_localize('UTC').tz_convert('Asia/Kolkata').hour
    else:
        df_model.loc[:, 'hour_local'] = df_model.index.tz_convert('Asia/Kolkata').hour

    # Features and target
    X = df_model[['cpu', 'memory', 'disk', 'battery', 'hour', 'hour_local']]
    y = df_model[['cpu_next', 'memory_next', 'disk_next', 'battery_next']]

    # Train model
    model_multi = LinearRegression()
    model_multi.fit(X, y)

    # Predict next hour using the most recent available row
    last_row = pd.DataFrame([X.iloc[-1].values], columns=X.columns)
    predicted = model_multi.predict(last_row)[0]

    print(f"Predicted next hour CPU: {predicted[0]:.2f}%")
    print(f"Predicted next hour Memory: {predicted[1]:.2f}%")
    print(f"Predicted next hour Disk: {predicted[2]:.2f}%")
    print(f"Predicted next hour Battery: {predicted[3]:.2f}%")

    if predicted[0] > 90:
        print("⚠️ Warning: CPU usage predicted to exceed 90% soon!")
    if predicted[1] > 85:
        print("⚠️ Warning: Memory usage predicted to stay high!")

    return predicted  # return predicted array for further use

# KMeans
def run_kmeans(df, n_clusters=3, resample_rule='1h', visualize=True, random_state=42):
    df_work = df.copy()
    df_work = df_work.set_index('timestamp')

    metric_cols = ['cpu', 'memory', 'disk', 'battery']
    for col in metric_cols:
        df_work[col] = pd.to_numeric(df_work[col], errors='coerce')

    df_hourly = df_work[metric_cols].resample(resample_rule).mean(numeric_only=True)
    df_model = df_hourly.dropna().copy()
    if df_model.empty:
        print("Not enough data after resampling to run KMeans.")
        return None, None

    df_model['hour'] = df_model.index.hour
    if df_model.index.tz is None:
        df_model['hour_local'] = df_model.index.tz_localize('UTC').tz_convert('Asia/Kolkata').hour
    else:
        df_model['hour_local'] = df_model.index.tz_convert('Asia/Kolkata').hour

    if len(df_model) < n_clusters:
        print(f"Not enough samples ({len(df_model)}) for n_clusters={n_clusters}.")
        return None, None

    features = ['cpu', 'memory', 'disk', 'battery', 'hour', 'hour_local']
    X = df_model[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if n_clusters > 1:
        k_temp = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        labels_temp = k_temp.fit_predict(X_scaled)
        sil = silhouette_score(X_scaled, labels_temp)
    else:
        sil = None

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    kmeans.fit(X_scaled)
    labels = kmeans.labels_

    df_model = df_model.copy()
    df_model['cluster'] = labels

    centers_scaled = kmeans.cluster_centers_
    centers = scaler.inverse_transform(centers_scaled)
    cluster_summary = pd.DataFrame(centers, columns=features)
    cluster_summary.index.name = 'cluster'

    counts = df_model['cluster'].value_counts().sort_index()
    cluster_summary['count'] = counts.values
    cluster_summary['proportion_%'] = (counts.values / len(df_model) * 100).round(2)

    cpu_order = cluster_summary['cpu'].sort_values(ascending=False).index.tolist()
    labels_map = {}
    human_labels = ['High load', 'Medium load', 'Low load']
    for i, cl in enumerate(cpu_order):
        lab = human_labels[i] if i < len(human_labels) else f"Cluster {i}"
        labels_map[cl] = lab
    cluster_summary['meaning'] = [labels_map[c] for c in cluster_summary.index]
    df_model['cluster_meaning'] = df_model['cluster'].map(labels_map)

    print("\nKMeans cluster summary (centers in original feature scale):")
    print(cluster_summary[['cpu','memory','disk','battery','count','proportion_%','meaning']])

    if sil is not None:
        print(f"\nSilhouette score for k={n_clusters}: {sil:.3f}")

    print("\nMost common local hour for each cluster (mode of hour_local):")
    for cl in sorted(df_model['cluster'].unique()):
        mode_hour = df_model[df_model['cluster'] == cl]['hour_local'].mode()
        if not mode_hour.empty:
            print(f"  Cluster {cl} ({labels_map[cl]}): around {int(mode_hour.iloc[0])}:00 local")
        else:
            print(f"  Cluster {cl}: no mode hour found")

    if visualize:
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)

        plt.figure(figsize=(10,4))
        plt.subplot(1,2,1)
        scatter = plt.scatter(X_pca[:,0], X_pca[:,1], c=labels, cmap='viridis', alpha=0.7)
        plt.title(f'KMeans (k={n_clusters}) - PCA projection')
        plt.xlabel('PC1'); plt.ylabel('PC2')
        plt.colorbar(scatter, label='cluster id')

        plt.subplot(1,2,2)
        plt.scatter(df_model['cpu'], df_model['memory'], c=df_model['cluster'], cmap='viridis', alpha=0.7)
        plt.xlabel('CPU %'); plt.ylabel('Memory %')
        plt.title('CPU vs Memory colored by cluster')

        plt.tight_layout()
        plt.show()

    return df_model, cluster_summary

# New combined function
def predict_and_analyze(df):
    print("\n=== Combined Prediction & Clustering ===")
    predicted = run_prediction(df)
    if predicted is None:
        print("Skipping KMeans due to insufficient data.")
        return
    df_model, cluster_summary = run_kmeans(df, visualize=True)
    if df_model is None:
        print("Skipping cluster labeling due to insufficient data.")
        return

    # Map predicted CPU to nearest cluster
    cpu_diffs = (cluster_summary['cpu'] - predicted[0]).abs()
    nearest_cluster = cpu_diffs.idxmin()
    print(f"\nPredicted CPU falls into cluster: {cluster_summary.loc[nearest_cluster,'meaning']}")

def main():
    df = load_data()

    while True:
        print("\n=== System Monitoring Viewer ===")
        print("1. Show usage graphs")
        print("2. Show weekly summary")
        print("3. Run predictive model")
        print("4. Show daily stats")
        print("5. Run KMeans")
        print("6. Exit")
        print("7. Predict next hour + cluster analysis")  # new option

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
            run_kmeans(df)
        elif choice == '6':
            break
        elif choice == '7':
            predict_and_analyze(df)
        else:
            print("Invalid choice! Please enter 1-7.")

if __name__ == "__main__":
    main()
