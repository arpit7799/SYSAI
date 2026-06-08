import numpy as np
from typing import List, Dict
from app.ml.lstm_model import LSTMForecaster
from app.ml.arima_model import ARIMAForecaster
from app.core.logger import log


class PredictionEngine:
    """
    Ensemble prediction engine combining LSTM and ARIMA.
    Weighted average: LSTM 60% + ARIMA 40%.
    Falls back to ARIMA only if LSTM fails.
    """

    def __init__(self):
        self.lstm = LSTMForecaster(window_size=20)
        self.arima = ARIMAForecaster()
        self.lstm_weight = 0.6
        self.arima_weight = 0.4
        log.info("PredictionEngine initialized")

    def predict(
        self,
        values: List[float],
        steps: int = 10,
        metric_name: str = "metric",
    ) -> Dict:
        """
        Run ensemble prediction.
        Returns dict with lstm, arima, and ensemble forecasts.
        """
        if len(values) < 5:
            log.warning("Not enough data for prediction", count=len(values))
            last = values[-1] if values else 50.0
            flat = [round(last, 2)] * steps
            return {
                "lstm": flat,
                "arima": flat,
                "ensemble": flat,
                "confidence": 0.0,
                "trend": "insufficient_data",
                "warning": False,
            }

        try:
            lstm_pred = self.lstm.predict(values, steps)
        except Exception as e:
            log.error("LSTM prediction failed", error=str(e))
            lstm_pred = [round(values[-1], 2)] * steps

        try:
            arima_pred = self.arima.predict(values, steps)
        except Exception as e:
            log.error("ARIMA prediction failed", error=str(e))
            arima_pred = [round(values[-1], 2)] * steps

        # Weighted ensemble
        ensemble = [
            round(
                self.lstm_weight * l + self.arima_weight * a, 2
            )
            for l, a in zip(lstm_pred, arima_pred)
        ]

        # Trend analysis
        current = float(np.mean(values[-5:]))
        predicted_end = ensemble[-1]
        delta = predicted_end - current

        if delta > 15:
            trend = "spike"
        elif delta > 5:
            trend = "rising"
        elif delta < -10:
            trend = "dropping"
        elif abs(delta) <= 5:
            trend = "stable"
        else:
            trend = "falling"

        # Confidence based on data consistency
        recent_std = float(np.std(values[-10:]))
        confidence = round(max(0, min(100, 100 - recent_std * 2)), 1)

        # Warning if predicted to exceed 85%
        warning = any(v > 85 for v in ensemble)

        log.info(
            "Prediction complete",
            metric=metric_name,
            trend=trend,
            warning=warning,
            confidence=confidence,
        )

        return {
            "lstm": lstm_pred,
            "arima": arima_pred,
            "ensemble": ensemble,
            "confidence": confidence,
            "trend": trend,
            "warning": warning,
        }