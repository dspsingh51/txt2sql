from agents.base import BaseAgent
from sql_engine.validator import SQLValidator


class SQLValidationAgent(BaseAgent):
    name = "sql_validation_agent"

    def __init__(self) -> None:
        self.validator = SQLValidator(read_only=True)

    def validate(self, sql: str, role: str) -> dict[str, object]:
        result = self.validator.validate(sql, role)
        return {
            "is_valid": result.is_valid,
            "status": result.status,
            "reasons": result.reasons,
            "sanitized_sql": result.sanitized_sql,
            "requires_approval": result.requires_approval,
            "referenced_tables": sorted(result.referenced_tables),
        }
