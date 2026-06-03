import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

try:
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # Allows seed scripts and core tests before dependency install.
    BaseSettings = object
    SettingsConfigDict = None

    def Field(default, **_: object):  # type: ignore
        return default


@dataclass
class _FallbackSettings:
    app_name: str = os.getenv("APP_NAME", "Enterprise AI Text-to-SQL Platform")
    app_env: str = os.getenv("APP_ENV", "local")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "datasets/enterprise_demo.db")
    database_dialect: str = os.getenv("DATABASE_DIALECT", "sqlite")
    read_only_mode: bool = os.getenv("READ_ONLY_MODE", "true").lower() == "true"
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or None
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    enable_llm: bool = os.getenv("ENABLE_LLM", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    audit_log_path: str = os.getenv("AUDIT_LOG_PATH", "monitoring/audit.log")
    max_result_rows: int = int(os.getenv("MAX_RESULT_ROWS", "500"))

    @property
    def sqlite_path(self) -> Path:
        return Path(self.sqlite_db_path)

    @property
    def audit_path(self) -> Path:
        return Path(self.audit_log_path)


class Settings(BaseSettings):  # type: ignore[misc]
    """Runtime settings loaded from environment variables and .env files."""

    if SettingsConfigDict:
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Enterprise AI Text-to-SQL Platform"
    app_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    sqlite_db_path: str = "datasets/enterprise_demo.db"
    database_dialect: str = "sqlite"
    read_only_mode: bool = True
    redis_url: str = "redis://localhost:6379/0"
    llm_provider: str = "gemini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    enable_llm: bool = False
    log_level: str = "INFO"
    audit_log_path: str = "monitoring/audit.log"
    max_result_rows: int = Field(default=500, ge=1, le=5000)

    @property
    def sqlite_path(self) -> Path:
        return Path(self.sqlite_db_path)

    @property
    def audit_path(self) -> Path:
        return Path(self.audit_log_path)


@lru_cache(maxsize=1)
def get_settings() -> Settings | _FallbackSettings:
    if BaseSettings is object:
        return _FallbackSettings()
    return Settings()
