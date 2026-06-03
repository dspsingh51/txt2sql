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
        sql = self._clean_llm_sql(llm_sql) if llm_sql else self._deterministic_sql(question)
        return {
            "sql": sql,
            "generation_mode": "gemini" if llm_sql else "deterministic_enterprise_demo",
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

    def _deterministic_sql(self, question: str) -> str:
        q = question.lower()
        if "top" in q and "region" in q and ("revenue" in q or "sales" in q):
            return """SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC
LIMIT 5;"""
        if "product" in q and ("growth" in q or "revenue" in q):
            return """SELECT product, quarter, ROUND(SUM(revenue), 2) AS revenue, ROUND(SUM(gross_margin), 2) AS gross_margin
FROM sales
GROUP BY product, quarter
ORDER BY product, quarter;"""
        if "q2" in q and ("decline" in q or "sales" in q or "revenue" in q):
            return """SELECT quarter, ROUND(SUM(revenue), 2) AS revenue, ROUND(SUM(gross_margin), 2) AS gross_margin
FROM sales
GROUP BY quarter
ORDER BY quarter;"""
        if "cost" in q or "expense" in q or "budget" in q:
            if "operational" in q or "anomal" in q:
                return """SELECT month, region, service_line, operational_expense, incidents, avg_resolution_hours
FROM operations
ORDER BY operational_expense DESC
LIMIT 10;"""
            return """SELECT month, department, ROUND(SUM(actual_cost), 2) AS actual_cost, ROUND(SUM(budget), 2) AS budget, ROUND(SUM(variance), 2) AS variance
FROM finance
GROUP BY month, department
ORDER BY month, department;"""
        if "churn" in q:
            return """SELECT month, region, segment, ROUND(AVG(churn_rate), 4) AS avg_churn_rate, SUM(churned_customers) AS churned_customers
FROM customer_analytics
GROUP BY month, region, segment
ORDER BY month, avg_churn_rate DESC
LIMIT 25;"""
        if "kpi" in q or "summary" in q or "executive" in q:
            return """SELECT 'Revenue' AS kpi, ROUND(SUM(revenue), 2) AS value FROM sales
UNION ALL
SELECT 'Gross Margin' AS kpi, ROUND(SUM(gross_margin), 2) AS value FROM sales
UNION ALL
SELECT 'Actual Cost' AS kpi, ROUND(SUM(actual_cost), 2) AS value FROM finance
UNION ALL
SELECT 'Average Churn Rate' AS kpi, ROUND(AVG(churn_rate), 4) AS value FROM customer_analytics;"""
        if "incident" in q or "ticket" in q or "resolution" in q:
            return """SELECT region, service_line, SUM(tickets) AS tickets, SUM(incidents) AS incidents, ROUND(AVG(avg_resolution_hours), 2) AS avg_resolution_hours
FROM operations
GROUP BY region, service_line
ORDER BY incidents DESC;"""
        return """SELECT region, ROUND(SUM(revenue), 2) AS total_revenue, ROUND(SUM(gross_margin), 2) AS total_margin
FROM sales
GROUP BY region
ORDER BY total_revenue DESC
LIMIT 10;"""
