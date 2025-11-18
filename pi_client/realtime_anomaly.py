import pandas as pd
import joblib
import numpy as np
from .smoothing import EWMASmoother
from .debouncer import AnomalyDebouncer
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "iso_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
THRESH_PATH = os.path.join(BASE_DIR, "threshold.pkl")

class RealtimeAnomalyDetector:
    def reset(self):
        self.cpu_s.last = None
        self.mem_s.last = None
        self.disk_s.last = None
        self.batt_s.last = None
        self.score_history.clear()
        self.debouncer.history.clear()

    def __init__(self):
        # Load trained components
        self.iso = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        self.threshold = joblib.load(THRESH_PATH)

        # EWMAs
        self.cpu_s = EWMASmoother(alpha=0.4)
        self.mem_s = EWMASmoother(alpha=0.4)
        self.disk_s = EWMASmoother(alpha=0.4)
        self.batt_s = EWMASmoother(alpha=0.4)

        # Debouncer (2/3 rule)
        self.debouncer = AnomalyDebouncer(window=3, required=2)

        # Keep last ~300 scores for optional dynamic thresholding
        self.score_history = []
        self.history_limit = 300  # ~5 minutes at 1 second interval

    def check(self, cpu, memory, disk, battery):
        # Smooth input values
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

        # IF score (lower => more anomalous)
        anomaly_score = self.iso.score_samples(X_scaled)[0]

        # Store score history for drift adaptation
        self.score_history.append(anomaly_score)
        if len(self.score_history) > self.history_limit:
            self.score_history.pop(0)

        # Use trained threshold as primary cutoff
        dynamic_threshold = self.threshold

        # Optional: adaptive threshold if system drifts significantly
        if len(self.score_history) > 50:
            # Look at lower extreme (3rd percentile of recent scores)
            drift_low = np.percentile(self.score_history, 3)
            # Choose the SAFER one (less sensitive)
            dynamic_threshold = min(dynamic_threshold, drift_low)

        # Determine anomaly
        anomaly = anomaly_score < dynamic_threshold

        # Debug (enable while tuning)
        print(
            f"Score={anomaly_score:.4f}, "
            f"Thresh={dynamic_threshold:.4f}, "
            f"A={anomaly}"
        )

        # Debounced result
        final = self.debouncer.add(anomaly)

        if final:
            print("🔴 DEBOUNCED ANOMALY TRIGGERED!")

        return final
