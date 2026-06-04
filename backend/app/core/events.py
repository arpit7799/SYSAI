import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logger import setup_logging, log
from app.db.base import Base
from app.db.session import engine
from app.services.db_writer import DBWriter
from app.agents.monitoring_agent import MonitoringAgent

_monitor = MonitoringAgent()
_writer = DBWriter()


async def _background_db_writer():
    """
    Background task — collects a snapshot every 5 seconds and saves to DB.
    Runs for the entire lifetime of the application.
    """
    log.info("Background DB writer started")
    while True:
        try:
            snapshot = _monitor.run()
            await _writer.save_snapshot(snapshot)
        except Exception as e:
            log.error("Background writer error", error=str(e))
        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──
    setup_logging()
    log.info("SYSAI starting", env=app.state.settings.app_env)

    # Create all tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Database tables ready")

    # Start background snapshot writer
    task = asyncio.create_task(_background_db_writer())

    yield  # app runs here

    # ── SHUTDOWN ──
    task.cancel()
    log.info("SYSAI shutting down")