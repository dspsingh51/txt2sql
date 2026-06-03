from agents.base import BaseAgent


class IntentUnderstandingAgent(BaseAgent):
    name = "intent_understanding_agent"

    def analyze(self, question: str) -> dict[str, object]:
        normalized = question.lower()
        intent = "general_analytics"
        if any(term in normalized for term in ["why", "decline", "increase", "decrease", "anomaly"]):
            intent = "diagnostic_analysis"
        elif any(term in normalized for term in ["top", "rank", "highest", "lowest"]):
            intent = "ranking"
        elif any(term in normalized for term in ["trend", "monthly", "quarter", "compare"]):
            intent = "trend_analysis"
        elif any(term in normalized for term in ["summary", "executive", "kpi"]):
            intent = "executive_summary"

        metrics = []
        for keyword in ["revenue", "cost", "expense", "churn", "nps", "arr", "margin", "incidents", "tickets"]:
            if keyword in normalized:
                metrics.append(keyword)

        dimensions = []
        for keyword in ["region", "product", "department", "segment", "month", "quarter"]:
            if keyword in normalized:
                dimensions.append(keyword)

        return {
            "intent": intent,
            "metrics": metrics or ["business_kpi"],
            "dimensions": dimensions,
            "time_grain": "quarter" if "quarter" in normalized or "q2" in normalized else "month" if "monthly" in normalized or "trend" in normalized else None,
            "requires_visualization": any(term in normalized for term in ["show", "chart", "visualize", "trend", "compare", "top"]),
        }
