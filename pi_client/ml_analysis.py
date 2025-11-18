import pandas as pd
import matplotlib
matplotlib.use("Agg")
import sqlite3
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import os

plt.style.use("dark_background")

CYAN = "#00ffff"
MAGENTA = "#ff0080"
SOFT_GRID = (0.2, 0.2, 0.2, 0.3)  # subtle grid lines


def neon_glow(ax, x, y, color, glow_radius=10):
    """Draw neon glow lines by layering thick low-alpha lines under the main line."""
    for i in range(glow_radius, 0, -1):
        ax.plot(
            x, y,
            color=color,
            linewidth=2 + i,
            alpha=0.03
        )
    ax.plot(
        x, y,
        color=color,
        linewidth=2.5
    )


def run_local_ml(days=3):
    """
    Perform KMeans clustering on the last N days of system usage data
    to determine load distribution (Idle / Moderate / High Load).
    """

    # -------- Load SQLite Data --------
    conn = sqlite3.connect("usage_log.db")
    df = pd.read_sql_query("SELECT * FROM usage_log", conn)
    conn.close()

    if df.empty or len(df) < 10:
        return "⚠️ Not enough data to run ML yet.", []

    # -------- Preprocessing --------
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Filter for only the last N days
    from datetime import datetime, timedelta
    min_date = datetime.now() - timedelta(days=days)
    df = df[df["timestamp"] >= min_date]

    if df.empty or len(df) < 10:
        return f"⚠️ Not enough data in the last {days} days to run ML.", []

    # Resample to 1-minute averages for stability
    df = df.set_index("timestamp").resample("1min").mean(numeric_only=True).dropna()

    if len(df) < 5:
        return "⚠️ Not enough samples after resampling.", []

    # -------- Features --------
    X = df[["cpu", "memory", "disk", "battery"]]

    # -------- KMeans Clustering --------
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    sil = silhouette_score(X_scaled, labels)

    # =====================================
    #  SMART CLUSTER NAMING (CPU + MEMORY)
    # =====================================
    cluster_scores = (
        0.7 * df["cpu"].groupby(labels).mean() +
        0.3 * df["memory"].groupby(labels).mean()
    )

    # Sort clusters by load score
    sorted_clusters = cluster_scores.sort_values().index.tolist()

    cluster_names = {
        sorted_clusters[0]: "Idle",
        sorted_clusters[1]: "Moderate",
        sorted_clusters[2]: "High Load"
    }

    # =====================================
    #  USAGE DISTRIBUTION PERCENTAGES
    # =====================================
    counts = pd.Series(labels).value_counts()
    total = len(labels)
    percentages = (counts / total * 100).round(2)

    usage_summary = "\n".join(
        f"- {cluster_names[c]}: {percentages[c]}%"
        for c in sorted_clusters
    )

    # =====================================
    #  PLOT — NEON KMEANS (CPU vs Memory)
    # =====================================
    km_plot_path = "ml_kmeans_plot.png"

    plt.figure(figsize=(5, 4))
    plt.scatter(
        X["cpu"], X["memory"],
        c=labels,
        cmap="cool",
        s=70,
        edgecolors=MAGENTA,
        linewidth=0.5,
        alpha=0.9
    )

    plt.title("System State Clusters", color=MAGENTA, fontsize=14, pad=12)
    plt.xlabel("CPU (%)", color=CYAN)
    plt.ylabel("Memory (%)", color=CYAN)

    plt.grid(color=SOFT_GRID)
    plt.xticks(color="#AAAAAA")
    plt.yticks(color="#AAAAAA")
    plt.tight_layout()
    plt.savefig(km_plot_path, dpi=150)
    plt.close()

    # =====================================
    #  SUMMARY
    # =====================================
    summary = (
        f"Predictions / Analysis Summary (Last {days} Days)\n\n"
        f"Cluster Silhouette Score: `{sil:.3f}`\n\n"
        f"Usage Distribution (last 3 days):\n"
        f"{usage_summary}\n\n"
        "🖼 Visualization Saved:\n"
        f" → `{km_plot_path}` (KMeans Clustering)\n"
    )

    return summary, [km_plot_path]
