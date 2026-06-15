from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class AgentEventResponse(BaseModel):
    id: int
    timestamp: datetime
    agent_name: str
    event_type: str
    channel: str
    data: Dict[str, Any]

    class Config:
        from_attributes = True


class AgentStatus(BaseModel):
    name: str
    status: str
    event_count: int
    last_run: str | None


class AgentStatusSummary(BaseModel):
    monitoring: AgentStatus
    prediction: AgentStatus
    anomaly: AgentStatus
    optimizer: AgentStatus
    recent_events: list[AgentEventResponse]