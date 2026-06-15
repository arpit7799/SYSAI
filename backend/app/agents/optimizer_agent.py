import asyncio
from app.agents.base_agent import BaseAgent
from app.agents.event_bus import CHANNEL_OPTIMIZATION, EventType, CHANNEL_ANOMALY
from app.services.optimization_service import run_optimization
from app.core.redis_manager import redis_manager
from app.core.logger import log


class OptimizerAgent(BaseAgent):
    """
    Listens to anomaly events and automatically optimizes.
    Publishes optimization actions.
    """

    def __init__(self):
        super().__init__("OptimizerAgent")
        self.status = "listening"

    async def on_anomaly(self, data: dict):
        """Callback when an anomaly is detected."""
        try:
            self.status = "optimizing"

            # Run optimization in safe mode
            result = await run_optimization(mode="safe")

            if result.get("actions"):
                await self.publish_event(
                    channel=CHANNEL_OPTIMIZATION,
                    event_type=EventType.OPTIMIZATION_EXECUTED,
                    data={
                        "action_count": len(result["actions"]),
                        "actions": result["actions"],
                        "status": result.get("status"),
                    },
                )

            self.status = "idle"
        except Exception as e:
            log.error("OptimizerAgent error", error=str(e))
            self.status = "error"

    async def run_loop(self):
        """Subscribe to anomaly events and react."""
        log.info("OptimizerAgent started")
        await redis_manager.subscribe(CHANNEL_ANOMALY, self.on_anomaly)