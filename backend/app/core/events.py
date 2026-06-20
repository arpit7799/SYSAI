import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logger import setup_logging, log
from app.core.redis_manager import redis_manager
from app.db.base import Base
from app.db.session import engine

_agent_tasks = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──
    setup_logging()
    log.info("SYSAI starting (host-based monitoring)", env=app.state.settings.app_env)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Add missing columns to existing tables (safe to re-run)
        new_columns = [
            ("metric_snapshots", "ram_total_gb", "FLOAT"),
            ("metric_snapshots", "ram_available_gb", "FLOAT"),
            ("metric_snapshots", "swap_total_gb", "FLOAT"),
            ("metric_snapshots", "swap_used_gb", "FLOAT"),
            ("metric_snapshots", "cpu_core_count", "INTEGER"),
            ("metric_snapshots", "cpu_thread_count", "INTEGER"),
            ("metric_snapshots", "disk_total_gb", "FLOAT"),
            ("metric_snapshots", "disk_used_gb", "FLOAT"),
            ("metric_snapshots", "disk_free_gb", "FLOAT"),
        ]
        from sqlalchemy import text
        for table, column, col_type in new_columns:
            try:
                await conn.execute(text(
                    f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {col_type}"
                ))
            except Exception:
                pass  # Column already exists

    log.info("Database tables ready")

    await redis_manager.connect()
    log.info("Redis connected (metrics only, no agents)")

    yield

    # ── SHUTDOWN ──
    for task in _agent_tasks:
        task.cancel()
    await redis_manager.disconnect()
    log.info("SYSAI shutting down")