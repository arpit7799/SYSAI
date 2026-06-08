from fastapi import APIRouter
from app.services.anomaly_service import get_anomaly_summary
from app.schemas.anomaly import AnomalySummary

router = APIRouter()


@router.get(
    "/anomalies",
    response_model=AnomalySummary,
    tags=["Anomalies"],
    summary="Get anomaly detection summary and recent events",
)
async def get_anomalies():
    """
    Returns summary counts and the 20 most recent anomaly events.
    Anomaly detection runs every 30 seconds in the background.
    """
    return await get_anomaly_summary()