import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class AgentTrace:
    agent: str
    status: str
    elapsed_ms: float
    details: dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    name = "base_agent"

    def run_with_trace(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> tuple[Any, AgentTrace]:
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        details = result if isinstance(result, dict) else {}
        return result, AgentTrace(agent=self.name, status="completed", elapsed_ms=elapsed_ms, details=details)
