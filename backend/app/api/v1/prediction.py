from fastapi import APIRouter, Query
from app.services.prediction_service import predict_metric
from app.schemas.prediction import PredictionResponse

router = APIRouter()


@router.get(
    "/prediction/{metric}",
    response_model=PredictionResponse,
    tags=["Prediction"],
    summary="Forecast future resource usage",
)
async def get_prediction(
    metric: str,
    steps: int = Query(default=10, ge=1, le=30),
):
    """
    Predict future values for a given metric.

    - metric: cpu | ram | disk
    - steps: how many future data points to forecast (1–30)

    Returns LSTM forecast, ARIMA forecast, and weighted ensemble.
    """
    return await predict_metric(metric=metric, steps=steps)