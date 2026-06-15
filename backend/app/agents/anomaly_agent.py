import asyncio
from app.agents.base_agent import BaseAgent
from app.agents.event_bus import CHANNEL_ANOMALY, EventType, CHANNEL_MONITORING
from app.services.anomaly_service import run_anomaly_detection
from app.core.redis_manager import redis_manager
from app.core.logger import log


class AnomalyAgent(BaseAgent):
    """
    Listens to monitoring events and runs anomaly detection.
    Publishes anomaly alerts.
    """

    def __init__(self):
        super().__init__("AnomalyAgent")
        self.status = "listening"

    async def on_snapshot(self, data: dict):
        """Callback when a monitoring snapshot is published."""
        try:
            self.status = "analyzing"

            # Run anomaly detection
            anomalies = await run_anomaly_detection()

            if anomalies:
                await self.publish_event(
                    channel=CHANNEL_ANOMALY,
                    event_type=EventType.ANOMALY_DETECTED,
                    data={
                        "count": len(anomalies),
                        "anomalies": [
                            {
                                "severity": a.severity,
                                "category": a.category,
                                "description": a.description,
                            }
                            for a in anomalies
                        ],
                    },
                )

            self.status = "idle"
        except Exception as e:
            log.error("AnomalyAgent error", error=str(e))
            self.status = "error"

    async def run_loop(self):
        """Subscribe to monitoring events and react."""
        log.info("AnomalyAgent started")
        await redis_manager.subscribe(CHANNEL_MONITORING, self.on_snapshot)