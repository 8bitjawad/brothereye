import pandas as pd
import matplotlib
matplotlib.use("Agg")
import sqlite3
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score, silhouette_score
import os

# ================================
# 🔥 Cyberpunk Theme Setup
# ================================
plt.style.use("dark_background")

CYAN = "#00ffff"
MAGENTA = "#ff0080"
SOFT_GRID = (0.2, 0.2, 0.2, 0.3)  # subtle grid lines


# ================================
# ✨ Neon Glow Helper Function
# ================================
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


# ================================
# ⚡ Main ML Analysis Function
# ================================
def run_local_ml():

    # -------- Load SQLite Data --------
    conn = sqlite3.connect("usage_log.db")
    df = pd.read_sql_query("SELECT * FROM usage_log", conn)
    conn.close()

    if df.empty or len(df) < 10:
        return "⚠️ Not enough data to run ML yet.", []

    # -------- Preprocessing --------
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", errors="coerce")
    df = df.set_index("timestamp").resample("1min").mean(numeric_only=True).dropna()

    if len(df) < 5:
        return "⚠️ Not enough samples after resampling.", []

    # -------- Build Regression Target --------
    df["cpu_next"] = df["cpu"].shift(-1)
    df = df.dropna()

    X = df[["cpu", "memory", "disk", "battery"]]
    y = df["cpu_next"]

    # -------- Linear Regression --------
    lr = LinearRegression().fit(X, y)
    y_pred = lr.predict(X)
    r2 = r2_score(y, y_pred)
    predicted_next = float(lr.predict([X.iloc[-1]])[0])

    # -------- KMeans Clustering --------
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    sil = silhouette_score(X_scaled, labels)

    # ================================
    # 🔥 PLOT 1: NEON REGRESSION
    # ================================
    lr_plot_path = "ml_lr_plot.png"

    fig, ax = plt.subplots(figsize=(6, 4))

    neon_glow(ax, df.index, y, CYAN)        # actual CPU
    neon_glow(ax, df.index, y_pred, MAGENTA)  # predicted CPU

    ax.set_title("CPU Prediction (Neon Regression)", color=CYAN, fontsize=14, pad=15)
    ax.set_xlabel("Time", color=CYAN)
    ax.set_ylabel("CPU (%)", color=CYAN)
    ax.legend(
        ["Actual CPU", "Predicted CPU"],
        facecolor="#111111",
        edgecolor=CYAN
    )

    ax.grid(color=SOFT_GRID)
    ax.tick_params(colors="#AAAAAA", rotation=45)
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))

    plt.tight_layout()
    plt.savefig(lr_plot_path, dpi=150)
    plt.close()


    # ================================
    # 🔥 PLOT 2: NEON KMEANS SCATTER
    # ================================
    km_plot_path = "ml_kmeans_plot.png"

    plt.figure(figsize=(5, 4))
    plt.scatter(
        X["cpu"],
        X["memory"],
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


    # ================================
    # 📊 Generate Text Summary
    # ================================
    summary = (
        "📊 **Neon ML Analysis Summary**\n\n"
        f"• **Regression R² Score:** `{r2:.3f}`\n"
        f"• **Cluster Silhouette Score:** `{sil:.3f}`\n"
        f"• **Predicted next-minute CPU:** `{predicted_next:.2f}%`\n\n"
        "🖼 **Neon Visualizations Saved:**\n"
        f" → `{lr_plot_path}` (Regression)\n"
        f" → `{km_plot_path}` (KMeans Clustering)"
    )

    return summary, [lr_plot_path, km_plot_path]
