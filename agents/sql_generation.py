import re

from agents.base import BaseAgent
from agents.llm import GeminiCompatibleClient
from configs.settings import get_settings


class SQLGenerationAgent(BaseAgent):
    name = "sql_generation_agent"

    def __init__(self) -> None:
        self.llm = GeminiCompatibleClient()
        self.settings = get_settings()

    def generate(self, question: str, role: str, schema_context: dict[str, object], conversation_context: list[dict[str, object]] | None = None) -> dict[str, str]:
        prompt = self._build_prompt(question, role, schema_context, conversation_context or [])
        llm_sql = self.llm.generate_text(prompt)
        sql = self._clean_llm_sql(llm_sql)
        if not sql:
            raise ValueError("LLM failed to generate a SQL query.")
        return {
            "sql": sql,
            "generation_mode": "gemini",
            "prompt_preview": prompt[:1200],
        }

    def _build_prompt(self, question: str, role: str, schema_context: dict[str, object], conversation_context: list[dict[str, object]]) -> str:
        context = "\n".join(str(item.get("question", "")) for item in conversation_context[-3:])
        return f"""You are an enterprise text-to-SQL assistant.
Question: {question}
Role: {role}
Dialect: {self.settings.database_dialect}
Schema:
{schema_context.get("prompt_context", "")}
Conversation:
{context}
Return one read-only SQL statement only."""

    def _clean_llm_sql(self, text: str | None) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        cleaned = re.sub(r"^```sql|```$", "", cleaned, flags=re.I | re.M).strip()
        return cleaned

