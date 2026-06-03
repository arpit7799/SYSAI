from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str
    timestamp: str


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Liveness probe endpoint.
    Used by Docker, Kubernetes, and load balancers to confirm the service is alive.
    """
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )