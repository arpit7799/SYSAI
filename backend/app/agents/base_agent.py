from typing import Dict, Any
from app.core.redis_manager import redis_manager
from app.core.logger import log
from datetime import datetime
from app.agents.event_bus import AgentEvent


class BaseAgent:
    """
    Base class for all autonomous agents.
    Handles event publishing and logging.
    """

    def __init__(self, name: str):
        self.name = name
        self.event_count = 0
        self.last_run = None
        self.status = "idle"

    async def publish_event(
        self,
        channel: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Publish an event to Redis."""
        event = AgentEvent(
            agent_name=self.name,
            event_type=event_type,
            timestamp=datetime.utcnow().isoformat(),
            data=data,
        )
        await redis_manager.publish(channel, event.to_dict())
        self.event_count += 1
        self.last_run = datetime.utcnow().isoformat()

    def get_status(self) -> Dict[str, Any]:
        """Return agent status."""
        return {
            "name": self.name,
            "status": self.status,
            "event_count": self.event_count,
            "last_run": self.last_run,
        }