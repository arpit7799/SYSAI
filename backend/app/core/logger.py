import structlog
import logging
from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """
    Configure structlog for structured JSON logging.
    In development: pretty colored output.
    In production: JSON (machine-parseable by tools like Datadog/Loki).
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.app_env == "development":
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


# Module-level logger — import this in other modules
log = structlog.get_logger("sysai")