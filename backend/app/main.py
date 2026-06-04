from fastapi import FastAPI
from app.core.config import get_settings
from app.core.events import lifespan
from app.api.v1 import health, monitoring, stream        # ← add monitoring

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.settings = settings

app.include_router(health.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")  
app.include_router(stream.router)