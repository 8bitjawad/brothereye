# train_model.py (robust)
import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "usage_log.db")

MODEL_PATH = os.path.join(BASE_DIR, "iso_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
THRESH_PATH = os.path.join(BASE_DIR, "threshold.pkl")

# EWMA smoothing (same as realtime)
def ewma_series(arr, alpha=0.4):
    s = []
    last = None
    for v in arr:
        if last is None:
            last = v
        else:
            last = alpha * v + (1 - alpha) * last
        s.append(last)
    return np.array(s)

def train_isolation_forest(min_rows=100, percentile=1.0):
    if not os.path.exists(DB_PATH):
        print("DB not found:", DB_PATH); return

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM usage_log", conn, parse_dates=["timestamp"])
    conn.close()

    if df.empty:
        print("No rows found in DB"); return

    print("Raw rows:", len(df))

    # Ensure timestamp sorted and set index
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp").reset_index(drop=True)
    else:
        # If no timestamp, treat as raw sequence
        print("Warning: no timestamp column -- proceeding with raw ordering")

    feature_cols = ["cpu", "memory", "disk", "battery"]
    for c in feature_cols:
        if c not in df.columns:
            df[c] = 0.0

    df = df[feature_cols].astype(float).fillna(method="ffill").fillna(method="bfill")

    # If timestamps are dense and regular you can resample; otherwise do sequence-based EWMA
    # Check density: if unique timestamps per second ~ total rows / duration is high, resample ok
    use_resample = False
    try:
        if "timestamp" in df.columns and len(df) > 2:
            # estimate density
            df_ts = pd.read_sql_query("SELECT timestamp FROM usage_log", sqlite3.connect(DB_PATH), parse_dates=["timestamp"])
            df_ts = df_ts.sort_values("timestamp")
            duration_s = (df_ts["timestamp"].max() - df_ts["timestamp"].min()).total_seconds() or 1
            density = len(df_ts) / duration_s
            # if density > 0.3 rows/sec (~one row every 3s) we can resample at 1s safely
            if density >= 0.3:
                use_resample = True
    except Exception:
        use_resample = False

    if use_resample:
        print("Using time-based resample (1S) because data is dense enough")
        df_time = df.copy()
        df_time["timestamp"] = pd.to_datetime(pd.read_sql_query("SELECT timestamp FROM usage_log", sqlite3.connect(DB_PATH), parse_dates=["timestamp"])["timestamp"])
        df_time = df_time.set_index("timestamp").resample("1S").mean().interpolate().ffill().bfill()
        df_proc = df_time[feature_cols]
    else:
        print("Using sequence-based EWMA smoothing (no resample)")
        # Apply EWMA on the raw ordered sequence
        df_proc = pd.DataFrame({
            "cpu": ewma_series(df["cpu"].values),
            "memory": ewma_series(df["memory"].values),
            "disk": ewma_series(df["disk"].values),
            "battery": ewma_series(df["battery"].values)
        })

    print("After processing rows:", len(df_proc))

    if len(df_proc) < min_rows:
        print(f"Not enough rows after processing ({len(df_proc)} < {min_rows}). Collect more data and retry.")
        # still continue if you insist, but warn
    X = df_proc.values

    # scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, SCALER_PATH)
    print("Saved scaler:", SCALER_PATH)

    # train iso forest
    iso = IsolationForest(
        contamination=0.01,
        n_estimators=200,
        random_state=42
    )
    iso.fit(X_scaled)
    joblib.dump(iso, MODEL_PATH)
    print("Saved model:", MODEL_PATH)

    # compute threshold
    train_scores = iso.score_samples(X_scaled)
    thresh = np.percentile(train_scores, percentile)
    joblib.dump(thresh, THRESH_PATH)
    print(f"Saved threshold={thresh:.4f} (percentile={percentile}%)")

    print("Score min:", np.min(train_scores))
    print("Score median:", np.median(train_scores))
    print("Score max:", np.max(train_scores))
    print("Estimated anomaly rate:", np.mean(train_scores < thresh))

if __name__ == "__main__":
    train_isolation_forest(min_rows=100, percentile=1.0)
