from pydantic import BaseModel
from datetime import datetime
from typing import List


class AgentStatus(BaseModel):
    name: str
    status: str
    event_count: int
    last_run: datetime | None


class AgentEventResponse(BaseModel):
    id: int
    agent_name: str
    event_type: str
    timestamp: datetime

    class Config:
        from_attributes = True


class AgentStatusSummary(BaseModel):
    monitoring: AgentStatus
    prediction: AgentStatus
    anomaly: AgentStatus
    optimizer: AgentStatus
    recent_events: List[AgentEventResponse]