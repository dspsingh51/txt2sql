import json
from collections import defaultdict
from typing import Any

from configs.settings import get_settings


class MemoryStore:
    _local_store: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    def __init__(self) -> None:
        self.settings = get_settings()
        self._redis = self._connect_redis()

    def append(self, session_id: str, event: dict[str, Any]) -> None:
        if self._redis:
            self._redis.rpush(self._key(session_id), json.dumps(event, default=str))
            self._redis.ltrim(self._key(session_id), -25, -1)
            return
        self._local_store[session_id].append(event)
        self._local_store[session_id] = self._local_store[session_id][-25:]

    def get_history(self, session_id: str) -> list[dict[str, Any]]:
        if self._redis:
            values = self._redis.lrange(self._key(session_id), 0, -1)
            return [json.loads(value) for value in values]
        return list(self._local_store[session_id])

    def _connect_redis(self):
        try:
            import redis
        except ImportError:
            return None
        try:
            client = redis.Redis.from_url(self.settings.redis_url, decode_responses=True)
            client.ping()
            return client
        except Exception:
            return None

    def _key(self, session_id: str) -> str:
        return f"text2sql:session:{session_id}"
