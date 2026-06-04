from app.db.session import AsyncSessionLocal
from app.db.models import MetricSnapshot
from app.schemas.metrics import SystemSnapshot
from app.core.logger import log


class DBWriter:
    """
    Persists metric snapshots to PostgreSQL.
    Called every 5 seconds from the background task in events.py.
    """

    async def save_snapshot(self, snapshot: SystemSnapshot) -> None:
        async with AsyncSessionLocal() as session:
            try:
                row = MetricSnapshot(
                    cpu_percent=snapshot.cpu.usage_percent,
                    cpu_per_core=snapshot.cpu.per_core_percent,
                    cpu_freq_mhz=snapshot.cpu.frequency_mhz,
                    ram_percent=snapshot.ram.usage_percent,
                    ram_used_gb=snapshot.ram.used_gb,
                    swap_percent=snapshot.ram.swap_percent,
                    disk_percent=snapshot.disk.usage_percent,
                    disk_read_mbps=snapshot.disk.read_mb_per_sec,
                    disk_write_mbps=snapshot.disk.write_mb_per_sec,
                    net_sent_mb=snapshot.network.bytes_sent_mb,
                    net_recv_mb=snapshot.network.bytes_recv_mb,
                    health_score=snapshot.health_score,
                    top_processes=[
                        p.model_dump() for p in snapshot.top_processes
                    ],
                )
                session.add(row)
                await session.commit()
                log.info("Snapshot saved to DB", health=snapshot.health_score)
            except Exception as e:
                await session.rollback()
                log.error("Failed to save snapshot", error=str(e))