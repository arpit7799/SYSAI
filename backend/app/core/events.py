from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logger import setup_logging, log


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Replaces deprecated @app.on_event("startup"/"shutdown").
    Everything before 'yield' runs on startup.
    Everything after 'yield' runs on shutdown.
    """
    # ── STARTUP ──
    setup_logging()
    log.info("SysAI-X starting", env=app.state.settings.app_env)

    # Future: DB connection pool, Redis client, ML model loading go here

    yield  # App runs here

    # ── SHUTDOWN ──
    log.info("SysAI-X shutting down")
    # Future: Close DB connections, flush queues