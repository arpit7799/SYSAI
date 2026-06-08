from typing import List
from sqlalchemy import select, desc, func
from app.db.session import AsyncSessionLocal
from app.db.models import MetricSnapshot, AnomalyEvent
from app.ml.anomaly_detector import AnomalyEngine
from app.schemas.anomaly import AnomalySummary, AnomalyEventResponse
from app.core.logger import log

_engine = AnomalyEngine()


async def run_anomaly_detection() -> List:
    """
    Fetch recent snapshots, run anomaly detection,
    save detected anomalies to DB.
    Called every 30 seconds from background task.
    """
    from typing import List

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MetricSnapshot)
            .order_by(desc(MetricSnapshot.captured_at))
            .limit(100)
        )
        rows = result.scalars().all()

    if len(rows) < 10:
        log.info("Not enough data for anomaly detection")
        return []

    # Convert to dicts for the engine
    snapshots = [
        {
            "cpu_percent": r.cpu_percent,
            "ram_percent": r.ram_percent,
            "disk_percent": r.disk_percent or 0,
            "top_processes": r.top_processes or [],
        }
        for r in reversed(rows)  # chronological order
    ]

    anomalies = _engine.analyze(snapshots)

    # Save to DB
    saved = []
    async with AsyncSessionLocal() as session:
        for a in anomalies:
            event = AnomalyEvent(
                severity=a["severity"],
                category=a["category"],
                description=a["description"],
                process_name=a.get("process_name"),
                raw_data={"score": a.get("score", 0)},
            )
            session.add(event)
            saved.append(event)
        await session.commit()

    if anomalies:
        log.info("Anomalies detected", count=len(anomalies))

    return saved


async def get_anomaly_summary() -> AnomalySummary:
    """
    Return summary of all anomalies with recent 20 events.
    """
    async with AsyncSessionLocal() as session:
        # Total count
        total_result = await session.execute(
            select(func.count(AnomalyEvent.id))
        )
        total = total_result.scalar() or 0

        # Count by severity
        for severity in ["critical", "high", "medium", "low"]:
            r = await session.execute(
                select(func.count(AnomalyEvent.id))
                .where(AnomalyEvent.severity == severity)
            )
            locals()[severity] = r.scalar() or 0

        # Recent 20
        recent_result = await session.execute(
            select(AnomalyEvent)
            .order_by(desc(AnomalyEvent.detected_at))
            .limit(20)
        )
        recent = recent_result.scalars().all()

    return AnomalySummary(
        total=total,
        critical=locals().get("critical", 0),
        high=locals().get("high", 0),
        medium=locals().get("medium", 0),
        low=locals().get("low", 0),
        recent=[AnomalyEventResponse.model_validate(r) for r in recent],
    )