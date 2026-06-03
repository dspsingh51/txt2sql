from statistics import mean
from typing import Any

from agents.base import BaseAgent


class AnalyticsInsightAgent(BaseAgent):
    name = "analytics_insight_agent"

    def summarize(self, question: str, sql: str, results: list[dict[str, Any]]) -> dict[str, object]:
        if not results:
            return {
                "summary": "No rows were returned for this question.",
                "explanation": "The generated query executed successfully but did not match any records in the demo dataset.",
                "recommendations": ["Broaden the time range or remove restrictive filters."],
            }

        numeric_columns = self._numeric_columns(results)
        headline = self._headline(results, numeric_columns)
        summary = f"Returned {len(results)} row(s). {headline}"
        explanation = self._explain(question, results, numeric_columns)
        recommendations = self._recommend(question, numeric_columns)
        return {
            "summary": summary,
            "explanation": explanation,
            "recommendations": recommendations,
        }

    def _numeric_columns(self, results: list[dict[str, Any]]) -> list[str]:
        columns = []
        for column, value in results[0].items():
            if isinstance(value, (int, float)):
                columns.append(column)
        return columns

    def _headline(self, results: list[dict[str, Any]], numeric_columns: list[str]) -> str:
        if not numeric_columns:
            return "The result is categorical and ready for review."
        column = numeric_columns[-1]
        values = [row[column] for row in results if isinstance(row.get(column), (int, float))]
        if not values:
            return "Numeric metrics were not available for ranking."
        return f"The primary metric '{column}' totals {round(sum(values), 2)} with an average of {round(mean(values), 2)}."

    def _explain(self, question: str, results: list[dict[str, Any]], numeric_columns: list[str]) -> str:
        first = results[0]
        if numeric_columns:
            metric = numeric_columns[-1]
            return (
                f"The query answers '{question}' by grouping or ranking the relevant enterprise records. "
                f"The leading row is {first}, making '{metric}' the main measure to review for business action."
            )
        return f"The query answers '{question}' by returning the most relevant enterprise records for inspection."

    def _recommend(self, question: str, numeric_columns: list[str]) -> list[str]:
        recommendations = [
            "Review the generated SQL against the business definition of the KPI.",
            "Compare this output with the previous period before making operational decisions.",
        ]
        if "decline" in question.lower() or "anomal" in question.lower():
            recommendations.append("Segment the result by region, product, or department to isolate root causes.")
        if numeric_columns:
            recommendations.append(f"Create a threshold alert for unusual movements in '{numeric_columns[-1]}'.")
        return recommendations
