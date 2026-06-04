from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class MetricSnapshot(Base):
    """
    Stores one complete system snapshot every 5 seconds.
    This is the primary time-series table.
    All ML models train on this data.
    """
    __tablename__ = "metric_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    captured_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,           # indexed for fast time-range queries
    )

    # CPU
    cpu_percent = Column(Float, nullable=False)
    cpu_per_core = Column(JSON, nullable=False)   # list of floats
    cpu_freq_mhz = Column(Float)

    # RAM
    ram_percent = Column(Float, nullable=False)
    ram_used_gb = Column(Float)
    swap_percent = Column(Float)

    # Disk
    disk_percent = Column(Float)
    disk_read_mbps = Column(Float)
    disk_write_mbps = Column(Float)

    # Network
    net_sent_mb = Column(Float)
    net_recv_mb = Column(Float)

    # Health
    health_score = Column(Float)

    # Top processes stored as JSON array
    top_processes = Column(JSON)


class AnomalyEvent(Base):
    """
    Stores detected anomalies. Populated in Step 8.
    """
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    severity = Column(String(20))        # low / medium / high / critical
    category = Column(String(50))        # cpu / ram / process / network
    description = Column(String(500))
    process_name = Column(String(200), nullable=True)
    raw_data = Column(JSON, nullable=True)


class OptimizationAction(Base):
    """
    Audit log of every optimization the engine performs. Populated in Step 9.
    """
    __tablename__ = "optimization_actions"

    id = Column(Integer, primary_key=True, index=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    action_type = Column(String(100))    # kill_process / set_priority / etc
    target = Column(String(200))
    reason = Column(String(500))
    success = Column(Integer, default=1) # 1 = success, 0 = failed
    rollback_data = Column(JSON, nullable=True)