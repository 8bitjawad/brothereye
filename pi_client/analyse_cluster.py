import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# === Load data from the local BrotherEye database ===
DB_PATH = "usage_log.db"  # Path to your Pi client database
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM usage_log", conn)
conn.close()

# === Preprocess the data ===
df = df.dropna()
features = ['cpu', 'memory', 'disk', 'battery']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

# === Run KMeans clustering ===
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_scaled)

silhouette = silhouette_score(X_scaled, df['cluster'])
print(f"✅ Silhouette Score: {silhouette:.3f}")

# === Compute cluster centers (mean feature values per cluster) ===
cluster_summary = df.groupby('cluster')[features].mean().round(2)
cluster_summary['Count'] = df['cluster'].value_counts().sort_index().values

# === Display as table ===
print("\n=== Cluster Summary Table ===")
print(cluster_summary)

# === Plot cluster visualization ===
plt.figure(figsize=(8, 6))
plt.scatter(df['cpu'], df['memory'], c=df['cluster'], cmap='viridis', s=60, alpha=0.7)
plt.xlabel("CPU Usage (%)")
plt.ylabel("Memory Usage (%)")
plt.title(f"KMeans Clustering of System States (Silhouette: {silhouette:.3f})")
plt.colorbar(label="Cluster ID")
plt.grid(True)
plt.tight_layout()
plt.savefig("kmeans_clusters.png", dpi=300)
plt.show()

# === Save summary table as CSV for paper ===
cluster_summary.to_csv("cluster_summary.csv")
print("\n📄 Table saved as 'cluster_summary.csv'")
print("📊 Plot saved as 'kmeans_clusters.png'")
