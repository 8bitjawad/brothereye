# smoothing.py

class EWMASmoother:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.last = None

    def update(self, x):
        if self.last is None:
            self.last = x
        else:
            self.last = self.alpha * x + (1 - self.alpha) * self.last
        return self.last
