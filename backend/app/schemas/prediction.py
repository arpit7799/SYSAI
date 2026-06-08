from pydantic import BaseModel
from typing import List


class PredictionResponse(BaseModel):
    metric: str
    current_value: float
    lstm_forecast: List[float]
    arima_forecast: List[float]
    ensemble_forecast: List[float]
    confidence: float
    trend: str
    warning: bool
    steps: int
    data_points_used: int