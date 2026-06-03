import json
from statistics import mean
from typing import Any

from agents.base import BaseAgent
from agents.llm import GeminiCompatibleClient


class AnalyticsInsightAgent(BaseAgent):
    name = "analytics_insight_agent"

    def __init__(self) -> None:
        self.llm = GeminiCompatibleClient()

    def summarize(self, question: str, sql: str, results: list[dict[str, Any]]) -> dict[str, object]:
        if not results:
            return {
                "summary": "No rows were returned for this question.",
                "explanation": "The generated query executed successfully but did not match any records in the demo dataset.",
                "recommendations": ["Broaden the time range or remove restrictive filters."],
            }

        prompt = f"""You are a data analyst. Analyze these query results and provide insights.
Question: {question}
SQL: {sql}
Results (first 5 rows): {results[:5]}

Respond EXACTLY in this JSON format:
{{
    "summary": "1-2 sentence high-level summary of the findings.",
    "explanation": "Brief explanation of how the data answers the question.",
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}}
"""
        llm_response = self.llm.generate_text(prompt)
        if llm_response:
            try:
                # Clean markdown JSON blocks if present
                cleaned = llm_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                elif cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                
                parsed = json.loads(cleaned.strip())
                return {
                    "summary": parsed.get("summary", "Analysis complete."),
                    "explanation": parsed.get("explanation", "Data retrieved successfully."),
                    "recommendations": parsed.get("recommendations", []),
                }
            except json.JSONDecodeError:
                pass

        # Fallback if LLM fails or is disabled
        return {
            "summary": f"Returned {len(results)} row(s).",
            "explanation": f"The query answers '{question}' by retrieving relevant records.",
            "recommendations": ["Review the generated SQL against business definitions."],
        }
