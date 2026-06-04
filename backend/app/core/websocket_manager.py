from fastapi import WebSocket
from typing import List
from app.core.logger import log


class ConnectionManager:
    """
    Manages all active WebSocket connections.
    In Step 11, this will broadcast messages from the Redis event bus
    instead of directly from the monitor loop.

    Supports multiple simultaneous dashboard clients.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        log.info("WebSocket client connected",
                 total=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        log.info("WebSocket client disconnected",
                 total=len(self.active_connections))

    async def send(self, websocket: WebSocket, data: dict):
        """Send data to a single connection."""
        await websocket.send_json(data)

    async def broadcast(self, data: dict):
        """
        Send data to ALL connected clients simultaneously.
        Used in Step 11 when Redis publishes a new metric event.
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                # Client disconnected ungracefully
                disconnected.append(connection)

        # Clean up dead connections
        for conn in disconnected:
            self.disconnect(conn)


# Single shared instance across the entire app
manager = ConnectionManager()