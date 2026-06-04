from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.db.models import MetricSnapshot
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()


class SnapshotRow(BaseModel):
    id: int
    captured_at: datetime
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    health_score: float

    class Config:
        from_attributes = True


@router.get(
    "/metrics/history",
    response_model=List[SnapshotRow],
    tags=["History"],
    summary="Get recent metric history",
)
async def get_history(
    limit: int = Query(default=100, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the last N snapshots from the database.
    Used by the dashboard to render trend charts.
    """
    result = await db.execute(
        select(MetricSnapshot)
        .order_by(desc(MetricSnapshot.captured_at))
        .limit(limit)
    )
    rows = result.scalars().all()
    return rows