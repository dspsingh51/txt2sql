from agents.base import BaseAgent
from sql_engine.executor import QueryExecutor


class QueryExecutionAgent(BaseAgent):
    name = "query_execution_agent"

    def __init__(self) -> None:
        self.executor = QueryExecutor()

    def execute(self, sql: str) -> dict[str, object]:
        records, metrics = self.executor.execute(sql)
        return {"results": records, "execution_metrics": metrics}
