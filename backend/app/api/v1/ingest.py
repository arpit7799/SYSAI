from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.session import AsyncSessionLocal
from app.db.models import MetricSnapshot
from app.core.logger import log
import json

router = APIRouter()


class CPUMetricsInput(BaseModel):
    usage_percent: float
    per_core_percent: List[float]
    frequency_mhz: float
    core_count: int
    thread_count: int


class RAMMetricsInput(BaseModel):
    total_gb: float
    used_gb: float
    available_gb: float
    usage_percent: float
    swap_total_gb: float
    swap_used_gb: float
    swap_percent: float


class DiskMetricsInput(BaseModel):
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float
    read_mb_per_sec: float
    write_mb_per_sec: float


class NetworkMetricsInput(BaseModel):
    bytes_sent_mb: float
    bytes_recv_mb: float
    packets_sent: int
    packets_recv: int


class ProcessInfoInput(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str
    username: Optional[str] = None


class MetricsIngestRequest(BaseModel):
    """Host metrics ingestion from external collector"""
    timestamp: str
    cpu: CPUMetricsInput
    ram: RAMMetricsInput
    disk: DiskMetricsInput
    network: NetworkMetricsInput
    top_processes: List[ProcessInfoInput]


@router.post(
    "/metrics/ingest",
    tags=["Metrics"],
    summary="Ingest host metrics from collector",
)
async def ingest_metrics(request: MetricsIngestRequest):
    """
    Accept host system metrics from external collector.
    This bypasses the container-based monitoring entirely.
    Direct database write — metrics are stored as-is.
    """
    try:
        # Parse timestamp
        captured_at = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
        
        # Calculate health score
        health_score = (
            (100 - request.cpu.usage_percent) * 0.4 +
            (100 - request.ram.usage_percent) * 0.4 +
            (100 - request.disk.usage_percent) * 0.2
        )
        
        # Convert processes to JSON
        top_processes_json = json.dumps([p.dict() for p in request.top_processes])

        # Create snapshot using EXACT column names from MetricSnapshot model
        snapshot = MetricSnapshot(
            captured_at=captured_at,
            cpu_percent=request.cpu.usage_percent,
            cpu_per_core=request.cpu.per_core_percent,
            cpu_freq_mhz=request.cpu.frequency_mhz,
            cpu_core_count=request.cpu.core_count,
            cpu_thread_count=request.cpu.thread_count,
            ram_percent=request.ram.usage_percent,
            ram_total_gb=request.ram.total_gb,
            ram_used_gb=request.ram.used_gb,
            ram_available_gb=request.ram.available_gb,
            swap_total_gb=request.ram.swap_total_gb,
            swap_used_gb=request.ram.swap_used_gb,
            swap_percent=request.ram.swap_percent,
            disk_percent=request.disk.usage_percent,
            disk_total_gb=request.disk.total_gb,
            disk_used_gb=request.disk.used_gb,
            disk_free_gb=request.disk.free_gb,
            disk_read_mbps=request.disk.read_mb_per_sec,
            disk_write_mbps=request.disk.write_mb_per_sec,
            net_sent_mb=request.network.bytes_sent_mb,
            net_recv_mb=request.network.bytes_recv_mb,
            health_score=health_score,
            top_processes=top_processes_json,
        )

        async with AsyncSessionLocal() as session:
            session.add(snapshot)
            await session.commit()
            await session.refresh(snapshot)

        log.info(
            "Metrics ingested from host collector",
            cpu=request.cpu.usage_percent,
            ram=request.ram.usage_percent,
            processes=len(request.top_processes),
        )

        return {
            "status": "ok",
            "snapshot_id": snapshot.id,
            "captured_at": snapshot.captured_at.isoformat(),
        }

    except Exception as e:
        log.error("Metrics ingest error", error=str(e), type=type(e).__name__)
        raise HTTPException(status_code=400, detail=str(e))