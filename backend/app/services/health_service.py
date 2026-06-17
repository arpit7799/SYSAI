from sqlalchemy import select, desc
from app.db.session import AsyncSessionLocal
from app.db.models import MetricSnapshot
from app.ml.health_scorer import HealthScorer
from app.core.logger import log
from typing import Dict, Any

scorer = HealthScorer()


async def calculate_health_score(
    current_cpu: float,
    current_ram: float,
    current_disk: float,
) -> Dict[str, Any]:
    """
    Calculate comprehensive health score using ML engine.
    Fetches recent history from DB and scores current state.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MetricSnapshot)
            .order_by(desc(MetricSnapshot.captured_at))
            .limit(100)
        )
        rows = result.scalars().all()

    if not rows:
        # Not enough data yet
        log.warning("Not enough historical data for health scoring")
        return {
            "health_score": 50.0,
            "status": "initializing",
            "factors": {
                "current_metrics": 50.0,
                "trends": 50.0,
                "volatility": 50.0,
                "anomalies": 50.0,
            },
            "trends": {"cpu": "unknown", "ram": "unknown", "disk": "unknown"},
            "issues": ["Collecting system data"],
        }

    # Reverse to chronological order
    rows = list(reversed(rows))

    # Extract histories
    cpu_history = [float(r.cpu_percent) for r in rows if r.cpu_percent is not None]
    ram_history = [float(r.ram_percent) for r in rows if r.ram_percent is not None]
    disk_history = [float(r.disk_percent) for r in rows if r.disk_percent is not None]

    # Score
    result = scorer.score(
        cpu_history=cpu_history,
        ram_history=ram_history,
        disk_history=disk_history,
        current_cpu=current_cpu,
        current_ram=current_ram,
        current_disk=current_disk,
    )

    log.info(
        "Health score calculated",
        score=result["health_score"],
        status=result["status"],
    )

    return result