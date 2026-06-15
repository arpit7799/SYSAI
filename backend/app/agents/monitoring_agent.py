import asyncio
from app.agents.base_agent import BaseAgent
from app.agents.event_bus import CHANNEL_MONITORING, EventType
from app.services.system_monitor import SystemMonitor
from app.core.logger import log
from datetime import datetime

monitor = SystemMonitor()


class MonitoringAgent(BaseAgent):
    """
    Continuously monitors system metrics and publishes snapshots.
    Runs every 5 seconds.
    """

    def __init__(self):
        super().__init__("MonitoringAgent")
        self.status = "running"

    async def run_loop(self):
        """Main agent loop — runs indefinitely."""
        log.info("MonitoringAgent started")
        while True:
            try:
                self.status = "collecting"
                snapshot = monitor.snapshot()

                log.info("Snapshot collected", cpu=snapshot.cpu.usage_percent)

                await self.publish_event(
                    channel=CHANNEL_MONITORING,
                    event_type=EventType.SNAPSHOT_COLLECTED,
                    data={
                        "cpu": snapshot.cpu.usage_percent,
                        "ram": snapshot.ram.usage_percent,
                        "disk": snapshot.disk.usage_percent,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

                self.status = "idle"
                log.info("Event published", count=self.event_count)
                await asyncio.sleep(5)

            except Exception as e:
                log.error("MonitoringAgent error", error=str(e), type=type(e).__name__)
                self.status = "error"
                await asyncio.sleep(5)

    def run(self):
        """Synchronous wrapper for backward compatibility."""
        return monitor.snapshot()