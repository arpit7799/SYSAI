from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.events import lifespan
from app.api.v1 import health, monitoring, stream, history, prediction, anomaly, optimization

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.settings = settings

app.include_router(health.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(stream.router)
app.include_router(history.router, prefix="/api/v1")
app.include_router(prediction.router, prefix="/api/v1")
app.include_router(anomaly.router, prefix="/api/v1")
app.include_router(optimization.router, prefix="/api/v1")