from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.db.base import Base


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    captured_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    cpu_percent = Column(Float, nullable=False)
    cpu_per_core = Column(JSON, nullable=False)
    cpu_freq_mhz = Column(Float)
    ram_percent = Column(Float, nullable=False)
    ram_used_gb = Column(Float)
    swap_percent = Column(Float)
    disk_percent = Column(Float)
    disk_read_mbps = Column(Float)
    disk_write_mbps = Column(Float)
    net_sent_mb = Column(Float)
    net_recv_mb = Column(Float)
    health_score = Column(Float)
    top_processes = Column(JSON)


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    severity = Column(String(20))
    category = Column(String(50))
    description = Column(String(500))
    process_name = Column(String(200), nullable=True)
    raw_data = Column(JSON, nullable=True)


class OptimizationAction(Base):
    __tablename__ = "optimization_actions"

    id = Column(Integer, primary_key=True, index=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    action_type = Column(String(100))
    target = Column(String(200))
    reason = Column(String(500))
    success = Column(Integer, default=1)
    rollback_data = Column(JSON, nullable=True)


class User(Base):
    """
    System users who can access the SYSAI API.
    Passwords are bcrypt hashed — never stored in plaintext.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AgentEvent(Base):
    """
    Log of all agent events for auditability and debugging.
    """
    __tablename__ = "agent_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    agent_name = Column(String(100), index=True)
    event_type = Column(String(100), index=True)
    channel = Column(String(100))
    data = Column(JSON, nullable=True)