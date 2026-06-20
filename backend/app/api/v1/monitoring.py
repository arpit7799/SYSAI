from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import MetricSnapshot
from app.core.logger import log
from datetime import datetime
import json

router = APIRouter()


@router.get(
    "/metrics/snapshot",
    tags=["Metrics"],
    summary="Get latest system metrics snapshot",
)
async def get_latest_snapshot(db: AsyncSession = Depends(get_db)):
    """
    Get the most recent metrics snapshot from host collector.
    Fetches directly from database — no SystemMonitor calls.
    """
    try:
        # Fetch latest snapshot from database
        result = await db.execute(
            select(MetricSnapshot)
            .order_by(desc(MetricSnapshot.captured_at))
            .limit(1)
        )
        snapshot = result.scalars().first()

        if not snapshot:
            log.warning("No metrics snapshots in database yet")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "usage_percent": 0,
                    "per_core_percent": [],
                    "frequency_mhz": 0,
                    "core_count": 0,
                    "thread_count": 0,
                },
                "ram": {
                    "total_gb": 0,
                    "used_gb": 0,
                    "available_gb": 0,
                    "usage_percent": 0,
                    "swap_total_gb": 0,
                    "swap_used_gb": 0,
                    "swap_percent": 0,
                },
                "disk": {
                    "total_gb": 0,
                    "used_gb": 0,
                    "free_gb": 0,
                    "usage_percent": 0,
                    "read_mb_per_sec": 0,
                    "write_mb_per_sec": 0,
                },
                "network": {
                    "bytes_sent_mb": 0,
                    "bytes_recv_mb": 0,
                    "packets_sent": 0,
                    "packets_recv": 0,
                },
                "top_processes": [],
                "health_score": 0,
            }

        # Parse top_processes JSON
        top_processes = []
        if snapshot.top_processes:
            try:
                top_processes = json.loads(snapshot.top_processes)
            except:
                top_processes = []

        # Format response
        return {
            "timestamp": snapshot.captured_at.isoformat(),
            "cpu": {
                "usage_percent": snapshot.cpu_percent,
                "per_core_percent": snapshot.cpu_per_core or [],
                "frequency_mhz": snapshot.cpu_freq_mhz or 0,
                "core_count": snapshot.cpu_core_count or 0,
                "thread_count": snapshot.cpu_thread_count or 0,
            },
            "ram": {
                "total_gb": snapshot.ram_total_gb or 0,
                "used_gb": snapshot.ram_used_gb or 0,
                "available_gb": snapshot.ram_available_gb or 0,
                "usage_percent": snapshot.ram_percent,
                "swap_total_gb": snapshot.swap_total_gb or 0,
                "swap_used_gb": snapshot.swap_used_gb or 0,
                "swap_percent": snapshot.swap_percent or 0,
            },
            "disk": {
                "total_gb": snapshot.disk_total_gb or 0,
                "used_gb": snapshot.disk_used_gb or 0,
                "free_gb": snapshot.disk_free_gb or 0,
                "usage_percent": snapshot.disk_percent,
                "read_mb_per_sec": snapshot.disk_read_mbps or 0,
                "write_mb_per_sec": snapshot.disk_write_mbps or 0,
            },
            "network": {
                "bytes_sent_mb": snapshot.net_sent_mb or 0,
                "bytes_recv_mb": snapshot.net_recv_mb or 0,
                "packets_sent": 0,
                "packets_recv": 0,
            },
            "top_processes": top_processes,
            "health_score": snapshot.health_score or 0,
        }

    except Exception as e:
        log.error("Error fetching snapshot", error=str(e))
        raise


@router.get(
    "/metrics/history",
    tags=["Metrics"],
    summary="Get historical metrics",
)
async def get_metrics_history(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get recent metric snapshots from database"""
    result = await db.execute(
        select(MetricSnapshot)
        .order_by(desc(MetricSnapshot.captured_at))
        .limit(limit)
    )
    snapshots = result.scalars().all()
    return [
        {
            "timestamp": s.captured_at.isoformat(),
            "cpu_percent": s.cpu_percent,
            "ram_percent": s.ram_percent,
            "disk_percent": s.disk_percent,
            "health_score": s.health_score,
        }
        for s in snapshots
    ]
