import numpy as np
from typing import List


class ARIMAForecaster:
    """
    Simplified ARIMA(1,1,1) implementation.
    Full statsmodels ARIMA used in ml-pipeline/ for research.
    This version runs without fitting overhead for real-time use.

    AR(1): next value depends on previous value
    I(1):  works on first differences (removes trend)
    MA(1): accounts for previous forecast error
    """

    def __init__(self):
        self.ar_coef = 0.7    # autoregressive coefficient
        self.ma_coef = 0.3    # moving average coefficient

    def predict(self, values: List[float], steps: int = 10) -> List[float]:
        if len(values) < 5:
            last = values[-1] if values else 50.0
            return [round(last, 2)] * steps

        arr = np.array(values, dtype=float)

        # First differences (I=1) — removes non-stationarity
        diffs = np.diff(arr)

        if len(diffs) == 0:
            return [round(float(arr[-1]), 2)] * steps

        # Estimate AR coefficient from autocorrelation
        if len(diffs) > 1:
            mean_diff = float(np.mean(diffs))
        else:
            mean_diff = 0.0

        predictions = []
        last_val = float(arr[-1])
        last_diff = float(diffs[-1])
        last_error = 0.0

        for _ in range(steps):
            # ARIMA forecast on differences
            next_diff = (
                self.ar_coef * last_diff
                + self.ma_coef * last_error
                + mean_diff * 0.1
            )
            # Invert differencing
            next_val = last_val + next_diff
            next_val = float(np.clip(next_val, 0, 100))

            # Update error term
            last_error = next_diff - last_diff
            last_diff = next_diff
            last_val = next_val

            predictions.append(round(next_val, 2))

        return predictions