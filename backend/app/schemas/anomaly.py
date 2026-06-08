from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AnomalyEventResponse(BaseModel):
    id: int
    detected_at: datetime
    severity: str
    category: str
    description: str
    process_name: Optional[str] = None

    class Config:
        from_attributes = True


class AnomalySummary(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    recent: List[AnomalyEventResponse]