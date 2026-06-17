import asyncio
from app.agents.base_agent import BaseAgent
from app.agents.event_bus import CHANNEL_MONITORING, EventType
from app.services.health_service import calculate_health_score
from app.core.redis_manager import redis_manager
from app.core.logger import log
from sqlalchemy import update
from app.db.session import AsyncSessionLocal
from app.db.models import MetricSnapshot
from datetime import datetime, timedelta


class HealthAgent(BaseAgent):
    """
    Listens to monitoring events and calculates ML-based health scores.
    Updates the latest metric snapshot with intelligent health scoring.
    """

    def __init__(self):
        super().__init__("HealthAgent")
        self.status = "listening"

    async def on_snapshot(self, data: dict):
        """Callback when a monitoring snapshot is published."""
        try:
            self.status = "scoring"

            current_cpu = data.get("cpu", 0)
            current_ram = data.get("ram", 0)
            current_disk = data.get("disk", 0)

            # Calculate ML-based health score
            health_result = await calculate_health_score(
                current_cpu=current_cpu,
                current_ram=current_ram,
                current_disk=current_disk,
            )

            # Update the latest snapshot in DB with the new health score
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(MetricSnapshot)
                    .where(
                        MetricSnapshot.captured_at >= datetime.utcnow() - timedelta(seconds=10)
                    )
                    .values(health_score=health_result["health_score"])
                )
                await session.commit()

            # Publish health event
            await self.publish_event(
                channel="health:scored",
                event_type=EventType.AGENT_HEALTH,
                data={
                    "health_score": health_result["health_score"],
                    "status": health_result["status"],
                    "issues": health_result["issues"],
                },
            )

            self.status = "idle"
        except Exception as e:
            log.error("HealthAgent error", error=str(e))
            self.status = "error"

    async def run_loop(self):
        """Subscribe to monitoring events and react."""
        log.info("HealthAgent started")
        await redis_manager.subscribe(CHANNEL_MONITORING, self.on_snapshot)