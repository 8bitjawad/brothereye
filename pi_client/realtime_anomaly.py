# realtime_anomaly.py
import pandas as pd
import joblib
import numpy as np
from .smoothing import EWMASmoother
from .debouncer import AnomalyDebouncer
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "iso_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

class RealtimeAnomalyDetector:
    def reset(self):
        self.cpu_s.last = None
        self.mem_s.last = None
        self.disk_s.last = None
        self.batt_s.last = None
        self.debouncer.history.clear()

    def __init__(self):
        self.iso = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)

        # smoothers for each metric
        self.cpu_s = EWMASmoother(alpha=0.4)
        self.mem_s = EWMASmoother(alpha=0.4)
        self.disk_s = EWMASmoother(alpha=0.4)
        self.batt_s = EWMASmoother(alpha=0.4)

        # debounce: last 3 predictions → 2 anomalies required
        self.debouncer = AnomalyDebouncer(window=3, required=2)

    # In realtime_anomaly.py - modify the check method:

    # In realtime_anomaly.py - replace the entire check method:

    def check(self, cpu, memory, disk, battery):
        cpu_s = self.cpu_s.update(cpu)
        mem_s = self.mem_s.update(memory)
        disk_s = self.disk_s.update(disk)
        batt_s = self.batt_s.update(battery)

        df = pd.DataFrame([{
            "cpu": cpu_s,
            "memory": mem_s,
            "disk": disk_s,
            "battery": batt_s
        }])

        X_scaled = self.scaler.transform(df)
        
        # Use score instead of prediction
        anomaly_score = self.iso.score_samples(X_scaled)[0]
        
        # Lower threshold = more sensitive to anomalies
        # Scores below -0.55 are considered anomalies
        anomaly = (anomaly_score < -0.55)
        
        # Debug logging
        print(f"📊 CPU={cpu:.1f}% (smoothed={cpu_s:.1f}%) | MEM={memory:.1f}% (smoothed={mem_s:.1f}%)")
        print(f"   Score={anomaly_score:.4f} | Anomaly={anomaly}")
        
        if anomaly:
            print(f"🚨 RAW ANOMALY: Score {anomaly_score:.4f} is below threshold -0.55")
        
        final = self.debouncer.add(anomaly)
        
        if final:
            print(f"🔴 DEBOUNCED ANOMALY TRIGGERED!")
        
        return final