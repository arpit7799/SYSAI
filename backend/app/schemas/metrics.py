from pydantic import BaseModel
from typing import List, Optional


class CPUMetrics(BaseModel):
    usage_percent: float          # overall CPU %
    per_core_percent: List[float] # per-core breakdown
    frequency_mhz: float          # current clock speed
    core_count: int
    thread_count: int


class RAMMetrics(BaseModel):
    total_gb: float
    used_gb: float
    available_gb: float
    usage_percent: float
    swap_total_gb: float
    swap_used_gb: float
    swap_percent: float


class DiskMetrics(BaseModel):
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float
    read_mb_per_sec: float
    write_mb_per_sec: float


class NetworkMetrics(BaseModel):
    bytes_sent_mb: float
    bytes_recv_mb: float
    packets_sent: int
    packets_recv: int


class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str
    username: Optional[str] = None


class SystemSnapshot(BaseModel):
    timestamp: str
    cpu: CPUMetrics
    ram: RAMMetrics
    disk: DiskMetrics
    network: NetworkMetrics
    top_processes: List[ProcessInfo]  
    health_score: float             