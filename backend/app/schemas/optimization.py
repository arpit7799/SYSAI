from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class OptimizationActionResponse(BaseModel):
    id: int
    executed_at: datetime
    action_type: str
    target: str
    reason: str
    success: int
    rollback_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class OptimizationRequest(BaseModel):
    mode: str = "safe"   # safe | aggressive


class OptimizationSummary(BaseModel):
    total_actions: int
    successful: int
    failed: int
    recent: List[OptimizationActionResponse]
    recommendations: List[str]