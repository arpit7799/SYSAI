import asyncio
from app.agents.base_agent import BaseAgent
from app.agents.event_bus import CHANNEL_PREDICTION, EventType, CHANNEL_MONITORING
from app.services.prediction_service import predict_metric
from app.core.redis_manager import redis_manager
from app.core.logger import log


class PredictionAgent(BaseAgent):
    """
    Listens to monitoring events and runs predictions.
    Publishes forecast events.
    """

    def __init__(self):
        super().__init__("PredictionAgent")
        self.status = "listening"

    async def on_snapshot(self, data: dict):
        """Callback when a monitoring snapshot is published."""
        try:
            self.status = "predicting"

            # Run predictions for each metric
            for metric in ["cpu", "ram", "disk"]:
                result = await predict_metric(metric=metric, steps=10)

                await self.publish_event(
                    channel=CHANNEL_PREDICTION,
                    event_type=EventType.PREDICTION_COMPLETE,
                    data={
                        "metric": metric,
                        "confidence": result.confidence,
                        "trend": result.trend,
                        "warning": result.warning,
                    },
                )

            self.status = "idle"
        except Exception as e:
            log.error("PredictionAgent error", error=str(e))
            self.status = "error"

    async def run_loop(self):
        """Subscribe to monitoring events and react."""
        log.info("PredictionAgent started")
        await redis_manager.subscribe(CHANNEL_MONITORING, self.on_snapshot)