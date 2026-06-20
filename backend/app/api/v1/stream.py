from fastapi import APIRouter, WebSocket, Query
from app.core.websocket_manager import manager
from app.core.logger import log

router = APIRouter()

@router.websocket("/ws/metrics")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None)
):
    print("\n========== WS REQUEST ==========")
    print("Client:", websocket.client)
    print("Headers:", dict(websocket.headers))
    print("Query:", websocket.query_params)
    print("================================\n")

    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        log.error("WebSocket error", error=str(e))
    finally:
        manager.disconnect(websocket)
        log.info("WebSocket client disconnected")