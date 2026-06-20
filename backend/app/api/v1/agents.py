from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import AgentEvent as AgentEventModel
from app.schemas.agent_event import AgentEventResponse, AgentStatusSummary, AgentStatus

router = APIRouter()


@router.get(
    "/agents/status",
    response_model=AgentStatusSummary,
    tags=["Agents"],
    summary="Get all agent statuses",
)
async def get_agent_status(db: AsyncSession = Depends(get_db)):
    """Get real-time status of all autonomous agents."""
    from app.core.events import _monitor, _prediction, _anomaly, _optimizer
    
    result = await db.execute(
        select(AgentEventModel)
        .order_by(desc(AgentEventModel.timestamp))
        .limit(20)
    )
    recent = result.scalars().all()

    return AgentStatusSummary(
        monitoring=AgentStatus(**_monitor.get_status()),
        prediction=AgentStatus(**_prediction.get_status()),
        anomaly=AgentStatus(**_anomaly.get_status()),
        optimizer=AgentStatus(**_optimizer.get_status()),
        recent_events=[AgentEventResponse.model_validate(e) for e in recent],
    )