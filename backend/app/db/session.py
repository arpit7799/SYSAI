from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import get_settings

settings = get_settings()

# Engine — one per application lifetime
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,      # logs SQL queries in debug mode
    pool_size=10,
    max_overflow=20,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # keep objects usable after commit
)


async def get_db() -> AsyncSession:
    """
    FastAPI dependency — injects a DB session into route handlers.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise