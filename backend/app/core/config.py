from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # App identity
    app_name: str = "SysAI-X"
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

    # Reads from .env file automatically
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache()  # instantiated once, reused everywhere
def get_settings() -> Settings:
    return Settings()