from sqlalchemy import select, desc
from app.db.session import AsyncSessionLocal
from app.db.models import MetricSnapshot
from app.ml.prediction_engine import PredictionEngine
from app.schemas.prediction import PredictionResponse
from app.core.logger import log

engine = PredictionEngine()


async def predict_metric(metric: str, steps: int = 10) -> PredictionResponse:
    """
    Fetch recent historical data from DB and run prediction.
    metric: 'cpu' | 'ram' | 'disk' | 'network'
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MetricSnapshot)
            .order_by(desc(MetricSnapshot.captured_at))
            .limit(100)
        )
        rows = result.scalars().all()

    if not rows:
        log.warning("No historical data for prediction")
        return PredictionResponse(
            metric=metric,
            current_value=0.0,
            lstm_forecast=[0.0] * steps,
            arima_forecast=[0.0] * steps,
            ensemble_forecast=[0.0] * steps,
            confidence=0.0,
            trend="no_data",
            warning=False,
            steps=steps,
            data_points_used=0,
        )

    # Rows are newest-first — reverse for chronological order
    rows = list(reversed(rows))

    # Extract the right metric column
    metric_map = {
        "cpu": lambda r: r.cpu_percent,
        "ram": lambda r: r.ram_percent,
        "disk": lambda r: r.disk_percent,
    }

    extractor = metric_map.get(metric)
    if not extractor:
        raise ValueError(f"Unknown metric: {metric}")

    values = [float(extractor(r)) for r in rows if extractor(r) is not None]
    current = values[-1] if values else 0.0

    result = engine.predict(values, steps=steps, metric_name=metric)

    return PredictionResponse(
        metric=metric,
        current_value=round(current, 2),
        lstm_forecast=result["lstm"],
        arima_forecast=result["arima"],
        ensemble_forecast=result["ensemble"],
        confidence=result["confidence"],
        trend=result["trend"],
        warning=result["warning"],
        steps=steps,
        data_points_used=len(values),
    )