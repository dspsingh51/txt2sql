from typing import Any

from agents.base import BaseAgent
from memory.store import MemoryStore


class MemoryAgent(BaseAgent):
    name = "memory_agent"

    def __init__(self) -> None:
        self.store = MemoryStore()

    def history(self, session_id: str) -> list[dict[str, Any]]:
        return self.store.get_history(session_id)

    def remember(self, session_id: str, event: dict[str, Any]) -> dict[str, object]:
        self.store.append(session_id, event)
        return {"session_id": session_id, "history_count": len(self.store.get_history(session_id))}
