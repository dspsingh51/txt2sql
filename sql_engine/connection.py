from pathlib import Path

from configs.settings import get_settings


def get_database_path() -> Path:
    settings = get_settings()
    return settings.sqlite_path


def describe_connection() -> dict[str, str]:
    settings = get_settings()
    return {
        "dialect": settings.database_dialect,
        "mode": "read-only" if settings.read_only_mode else "read-write",
        "sqlite_db_path": str(settings.sqlite_path),
    }
