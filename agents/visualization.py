from typing import Any

from agents.base import BaseAgent


class VisualizationAgent(BaseAgent):
    name = "visualization_agent"

    def recommend(self, results: list[dict[str, Any]], intent: dict[str, Any]) -> dict[str, Any]:
        if not results:
            return {"type": "table", "title": "No Results", "x": None, "y": None}
        columns = list(results[0].keys())
        numeric_columns = [
            column for column in columns if isinstance(results[0].get(column), (int, float))
        ]
        categorical_columns = [column for column in columns if column not in numeric_columns]

        if intent.get("time_grain") and numeric_columns:
            x = "month" if "month" in columns else "quarter" if "quarter" in columns else categorical_columns[0]
            return {"type": "line", "title": "Trend Analysis", "x": x, "y": numeric_columns[-1]}
        if numeric_columns and categorical_columns:
            return {"type": "bar", "title": "Business Metric Comparison", "x": categorical_columns[0], "y": numeric_columns[-1]}
        return {"type": "table", "title": "Query Results", "x": None, "y": None}
