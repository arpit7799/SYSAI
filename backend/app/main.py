from fastapi import FastAPI
from app.core.config import get_settings
from app.core.events import lifespan
from app.api.v1 import health

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc UI
    lifespan=lifespan,
)

# Store settings on app state so event handlers can access them
app.state.settings = settings

# Register routers
app.include_router(health.router, prefix="/api/v1")