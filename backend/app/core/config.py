from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "SysAI"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Security
    secret_key: str = "changeme"

    # Logging
    log_level: str = "INFO"

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "sysai"
    postgres_user: str = "sysai"
    postgres_password: str = "sysai_secret"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""

    @property
    def database_url(self) -> str:
        """Async PostgreSQL URL for SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    return Settings()