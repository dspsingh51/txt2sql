import sqlite3
import time
from pathlib import Path
from typing import Any

from configs.settings import get_settings


class QueryExecutor:
    def __init__(self, db_path: str | Path | None = None) -> None:
        settings = get_settings()
        self.db_path = Path(db_path or settings.sqlite_db_path)
        self.max_rows = settings.max_result_rows

    def execute(self, sql: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        start = time.perf_counter()
        try:
            with sqlite3.connect(self.db_path) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.execute(sql)
                rows = cursor.fetchmany(self.max_rows)
                columns = [description[0] for description in cursor.description or []]
        except sqlite3.Error as e:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            return [], {
                "elapsed_ms": elapsed_ms,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "error": str(e)
            }
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        records = [
            {
                column: row[column]
                for column in columns
            }
            for row in rows
        ]
        return records, {
            "elapsed_ms": elapsed_ms,
            "row_count": len(records),
            "column_count": len(columns),
            "columns": columns,
        }
