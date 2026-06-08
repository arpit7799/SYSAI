import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logger import setup_logging, log
from app.db.base import Base
from app.db.session import engine
from app.services.db_writer import DBWriter
from app.agents.monitoring_agent import MonitoringAgent
from app.services.anomaly_service import run_anomaly_detection

_monitor = MonitoringAgent()
_writer = DBWriter()


async def _background_db_writer():
    log.info("Background DB writer started")
    while True:
        try:
            snapshot = _monitor.run()
            await _writer.save_snapshot(snapshot)
        except Exception as e:
            log.error("Background writer error", error=str(e))
        await asyncio.sleep(5)


async def _background_anomaly_detector():
    """
    Runs anomaly detection every 30 seconds.
    Waits 60 seconds on startup to let DB collect enough data.
    """
    log.info("Background anomaly detector started")
    await asyncio.sleep(60)  # wait for initial data
    while True:
        try:
            await run_anomaly_detection()
        except Exception as e:
            log.error("Anomaly detection error", error=str(e))
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──
    setup_logging()
    log.info("SYSAI starting", env=app.state.settings.app_env)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Database tables ready")

    task1 = asyncio.create_task(_background_db_writer())
    task2 = asyncio.create_task(_background_anomaly_detector())

    yield

    # ── SHUTDOWN ──
    task1.cancel()
    task2.cancel()
    log.info("SYSAI shutting down")