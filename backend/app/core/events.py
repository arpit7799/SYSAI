import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logger import setup_logging, log
from app.core.redis_manager import redis_manager
from app.db.base import Base
from app.db.session import engine
from app.services.db_writer import DBWriter
from app.agents.monitoring_agent import MonitoringAgent
from app.agents.prediction_agent import PredictionAgent
from app.agents.anomaly_agent import AnomalyAgent
from app.agents.optimizer_agent import OptimizerAgent

_monitor = MonitoringAgent()
_prediction = PredictionAgent()
_anomaly = AnomalyAgent()
_optimizer = OptimizerAgent()

_writer = DBWriter()
_agent_tasks = []


async def _background_db_writer():
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

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Database tables ready")

    # Connect Redis
    await redis_manager.connect()

    # Start agent loops
    task_db = asyncio.create_task(_background_db_writer())
    task_monitoring = asyncio.create_task(_monitor.run_loop())
    task_prediction = asyncio.create_task(_prediction.run_loop())
    task_anomaly = asyncio.create_task(_anomaly.run_loop())
    task_optimizer = asyncio.create_task(_optimizer.run_loop())

    _agent_tasks.extend([
        task_db, task_monitoring, task_prediction, task_anomaly, task_optimizer
    ])

    yield

    # ── SHUTDOWN ──
    for task in _agent_tasks:
        task.cancel()
    await redis_manager.disconnect()
    log.info("SYSAI shutting down")