import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score, silhouette_score
import os

def run_local_ml():
    
    conn = sqlite3.connect("usage_log.db")
    df = pd.read_sql_query("SELECT * FROM usage_log", conn)
    conn.close()

    if df.empty or len(df) < 10:
        return "⚠️ Not enough data to run ML yet.", []

    # --- Preprocess ---
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
    df = df.set_index("timestamp").resample("1min").mean(numeric_only=True).dropna()

    if len(df) < 5:
        return "⚠️ Not enough hourly samples.", []

    # --- Linear Regression ---
    df["cpu_next"] = df["cpu"].shift(-1)
    df = df.dropna()
    X = df[["cpu", "memory", "disk", "battery"]]
    y = df["cpu_next"]

    lr = LinearRegression().fit(X, y)
    y_pred = lr.predict(X)
    r2 = r2_score(y, y_pred)
    predicted_next = float(lr.predict([X.iloc[-1]])[0])

    # --- KMeans Clustering ---
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels)

    # --- Plot 1: Linear Regression ---
    plt.figure(figsize=(6, 4))
    plt.plot(df.index, y, label="Actual CPU", color="cyan", linewidth=2)
    plt.plot(df.index, y_pred, label="Predicted CPU", color="magenta", linestyle="--", linewidth=2)
    plt.title("Linear Regression: CPU Usage Prediction")
    plt.xlabel("Time")
    plt.ylabel("CPU (%)")
    plt.legend()
    plt.grid(alpha=0.3)
    lr_plot_path = "ml_lr_plot.png"
    plt.tight_layout()
    plt.savefig(lr_plot_path, dpi=150)
    plt.close()

    # --- Plot 2: KMeans Clusters (CPU vs Memory) ---
    plt.figure(figsize=(5, 4))
    plt.scatter(X["cpu"], X["memory"], c=labels, cmap="cool", s=50, alpha=0.7)
    plt.xlabel("CPU (%)")
    plt.ylabel("Memory (%)")
    plt.title("KMeans Clustering: CPU vs Memory")
    plt.grid(alpha=0.3)
    km_plot_path = "ml_kmeans_plot.png"
    plt.tight_layout()
    plt.savefig(km_plot_path, dpi=150)
    plt.close()

    summary = (
        "📊 **ML Analysis Summary**\n\n"
        f"• R² Score (Regression): **{r2:.3f}**\n"
        f"• Silhouette Score (Clustering): **{sil:.3f}**\n"
        f"• Predicted next-minute CPU: **{predicted_next:.2f}%**\n\n"
        "✅ Analysis complete. Visualizations saved as:\n"
        f" → `{lr_plot_path}` (Regression)\n"
        f" → `{km_plot_path}` (Clustering)"
    )

    return summary, [lr_plot_path, km_plot_path]
