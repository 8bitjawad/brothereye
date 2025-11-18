# debouncer.py

from collections import deque

class AnomalyDebouncer:
    def __init__(self, window=3, required=2):
        self.history = deque(maxlen=window)
        self.required = required

    def add(self, is_anomaly):
        self.history.append(is_anomaly)
        return self.history.count(True) >= self.required
