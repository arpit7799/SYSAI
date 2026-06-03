from app.services.system_monitor import SystemMonitor
from app.schemas.metrics import SystemSnapshot
from app.core.logger import log


class MonitoringAgent:
    """
    Agent wrapper around SystemMonitor.
    In Step 11, this agent will communicate with other agents
    via Redis pub/sub. For now it runs synchronously.
    """

    def __init__(self):
        self.monitor = SystemMonitor()
        log.info("MonitoringAgent initialized")

    def run(self) -> SystemSnapshot:
        snapshot = self.monitor.snapshot()
        log.info(
            "Snapshot collected",
            cpu=snapshot.cpu.usage_percent,
            ram=snapshot.ram.usage_percent,
            health=snapshot.health_score,
        )
        return snapshot