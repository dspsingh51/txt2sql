from agents.base import BaseAgent
from sql_engine.schema import rank_schema


class SchemaContextAgent(BaseAgent):
    name = "schema_context_agent"

    def retrieve(self, question: str) -> dict[str, object]:
        tables = rank_schema(question)
        return {
            "tables": [table.name for table in tables],
            "prompt_context": "\n\n".join(table.to_prompt_context() for table in tables),
            "columns": {
                table.name: [column.name for column in table.columns]
                for table in tables
            },
        }
