from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

# Event channels
CHANNEL_MONITORING = "monitoring:snapshot"
CHANNEL_PREDICTION = "prediction:forecast"
CHANNEL_ANOMALY = "anomaly:detected"
CHANNEL_OPTIMIZATION = "optimization:executed"


@dataclass
class AgentEvent:
    """Base event structure for all agents."""
    agent_name: str
    event_type: str
    timestamp: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict:
        return {
            "agent_name": self.agent_name,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "data": self.data,
        }


# Event types
class EventType:
    SNAPSHOT_COLLECTED = "snapshot_collected"
    PREDICTION_COMPLETE = "prediction_complete"
    ANOMALY_DETECTED = "anomaly_detected"
    OPTIMIZATION_EXECUTED = "optimization_executed"
    AGENT_ERROR = "agent_error"
    AGENT_HEALTH = "agent_health"