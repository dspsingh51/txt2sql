import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from configs.settings import get_settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_fields"):
            payload.update(record.extra_fields)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    settings = get_settings()
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(settings.log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)

    settings.audit_path.parent.mkdir(parents=True, exist_ok=True)


def audit_event(event_type: str, payload: dict[str, Any]) -> None:
    settings = get_settings()
    settings.audit_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": event_type,
        **payload,
    }
    with Path(settings.audit_path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, default=str) + "\n")
