from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.events import lifespan
from app.api.v1 import (
    health,
    monitoring,
    stream,
    prediction,
    anomaly,
    optimization,
    auth,
    agents,
    ingest,
)

# Create app with lifespan
app = FastAPI(
    title="SYSAI",
    description="Autonomous AI OS Optimization Engine",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store settings in app state
app.state.settings = settings

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(stream.router, prefix="/api/v1")
app.include_router(prediction.router, prefix="/api/v1")
app.include_router(anomaly.router, prefix="/api/v1")
app.include_router(optimization.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(ingest.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "status": "ok",
        "app": "SYSAI",
        "version": "0.1.0",
        "docs": "/docs",
    }