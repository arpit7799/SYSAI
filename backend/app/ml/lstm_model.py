import numpy as np
from typing import List


class LSTMForecaster:
    """
    Lightweight LSTM-based forecaster using numpy only.
    Full TensorFlow LSTM added in ml-pipeline/ for training.
    This is the inference-time version — fast, no training overhead.

    Uses a simple exponential smoothing + pattern detection
    that mimics LSTM behavior for real-time inference without
    needing a pre-trained model file at this stage.
    """

    def __init__(self, window_size: int = 20):
        self.window_size = window_size

    def predict(self, values: List[float], steps: int = 10) -> List[float]:
        """
        Predict next `steps` values given historical `values`.
        Returns a list of predicted floats.
        """
        if len(values) < self.window_size:
            # Not enough data — return flat forecast
            last = values[-1] if values else 50.0
            return [round(last, 2)] * steps

        arr = np.array(values[-self.window_size:])

        # Trend detection via linear regression on the window
        x = np.arange(len(arr))
        slope, intercept = np.polyfit(x, arr, 1)

        # Volatility — standard deviation of recent values
        volatility = float(np.std(arr[-10:]))

        # Exponential smoothing on the window
        alpha = 0.3
        smoothed = float(arr[-1])
        for v in arr:
            smoothed = alpha * float(v) + (1 - alpha) * smoothed

        predictions = []
        current = smoothed

        for i in range(steps):
            # Trend component
            trend = slope * (len(arr) + i)
            # Mean reversion — pull toward rolling mean
            mean = float(np.mean(arr))
            reversion = (mean - current) * 0.1
            # Next value
            next_val = current + (slope * 0.5) + reversion
            next_val = float(np.clip(next_val, 0, 100))
            predictions.append(round(next_val, 2))
            current = next_val

        return predictions