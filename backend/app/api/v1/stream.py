import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
from app.agents.monitoring_agent import MonitoringAgent
from app.core.logger import log

router = APIRouter()

# Reuse the same agent instance
_agent = MonitoringAgent()

STREAM_INTERVAL_SECONDS = 1.0  # push every 1 second


@router.websocket("/ws/metrics")
async def metrics_stream(websocket: WebSocket):
    """
    WebSocket endpoint that streams live system metrics every second.

    Connect from frontend with:
        const ws = new WebSocket("ws://localhost:8000/ws/metrics")

    Each message is a full SystemSnapshot serialized as JSON.
    """
    await manager.connect(websocket)

    try:
        while True:
            # Collect snapshot
            snapshot = _agent.run()

            # .model_dump() converts Pydantic model → plain dict → JSON-safe
            await manager.send(websocket, snapshot.model_dump())

            # Wait before next push
            await asyncio.sleep(STREAM_INTERVAL_SECONDS)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        log.info("WebSocket disconnected cleanly")

    except Exception as e:
        manager.disconnect(websocket)
        log.error("WebSocket error", error=str(e))