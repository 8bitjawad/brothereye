# train_model.py

import sqlite3
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib

MODEL_PATH = "iso_model.pkl"
SCALER_PATH = "scaler.pkl"

def train_isolation_forest():
    conn = sqlite3.connect("usage_log.db")
    df = pd.read_sql_query("SELECT * FROM usage_log", conn)
    conn.close()

    if df.empty:
        print("No data available!")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.set_index("timestamp").resample("15s").mean(numeric_only=True).dropna()

    feature_cols = ["cpu", "memory", "disk", "battery"]
    df = df[feature_cols].dropna()

    # Smooth for stability
    df = df.ewm(alpha=0.3).mean()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    iso = IsolationForest(
        contamination=0.005,
        n_estimators=200,
        random_state=42
    )
    iso.fit(X_scaled)

    joblib.dump(iso, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    print("Isolation Forest model trained and saved!")

if __name__ == "__main__":
    train_isolation_forest()
