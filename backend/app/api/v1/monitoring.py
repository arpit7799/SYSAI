from fastapi import APIRouter
from app.agents.monitoring_agent import MonitoringAgent
from app.schemas.metrics import SystemSnapshot

router = APIRouter()

# Single agent instance — reused across requests
_agent = MonitoringAgent()


@router.get(
    "/metrics/snapshot",
    response_model=SystemSnapshot,
    tags=["Monitoring"],
    summary="Get a full real-time system snapshot",
)
async def get_snapshot():
    """
    Returns a complete real-time snapshot of the system:
    CPU, RAM, Disk, Network, top processes, and health score.
    Called every second by the frontend dashboard (Step 6).
    WebSocket streaming added in Step 3.
    """
    return _agent.run()