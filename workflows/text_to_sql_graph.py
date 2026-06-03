import time
from typing import Any

from agents.execution import QueryExecutionAgent
from agents.insights import AnalyticsInsightAgent
from agents.intent import IntentUnderstandingAgent
from agents.memory_agent import MemoryAgent
from agents.schema_context import SchemaContextAgent
from agents.sql_generation import SQLGenerationAgent
from agents.sql_validation import SQLValidationAgent
from agents.visualization import VisualizationAgent
from configs.logging import audit_event
from sql_engine.governance import QueryGovernance
from sql_engine.validator import SqlValidationResult


class TextToSQLWorkflow:
    """LangGraph-inspired deterministic orchestration.

    The project keeps this runnable without external services while preserving
    node boundaries that map cleanly to LangGraph in production.
    """

    def __init__(self) -> None:
        self.intent_agent = IntentUnderstandingAgent()
        self.schema_agent = SchemaContextAgent()
        self.sql_agent = SQLGenerationAgent()
        self.validation_agent = SQLValidationAgent()
        self.execution_agent = QueryExecutionAgent()
        self.insight_agent = AnalyticsInsightAgent()
        self.visualization_agent = VisualizationAgent()
        self.memory_agent = MemoryAgent()
        self.governance = QueryGovernance()

    def run(self, question: str, role: str, session_id: str, require_approval: bool = False) -> dict[str, Any]:
        workflow_start = time.perf_counter()
        trace = []

        history, history_trace = self.memory_agent.run_with_trace(self.memory_agent.history, session_id)
        trace.append(history_trace.__dict__)

        intent, intent_trace = self.intent_agent.run_with_trace(self.intent_agent.analyze, question)
        trace.append(intent_trace.__dict__)

        schema_context, schema_trace = self.schema_agent.run_with_trace(self.schema_agent.retrieve, question)
        trace.append(schema_trace.__dict__)

        generation, generation_trace = self.sql_agent.run_with_trace(
            self.sql_agent.generate, question, role, schema_context, history
        )
        trace.append(generation_trace.__dict__)
        sql = generation["sql"]

        validation, validation_trace = self.validation_agent.run_with_trace(self.validation_agent.validate, sql, role)
        trace.append(validation_trace.__dict__)
        validation_result = SqlValidationResult(
            is_valid=bool(validation["is_valid"]),
            status=str(validation["status"]),
            reasons=list(validation["reasons"]),
            sanitized_sql=validation.get("sanitized_sql"),
            requires_approval=bool(validation["requires_approval"]),
            referenced_tables=set(validation.get("referenced_tables", [])),
        )

        governance = self.governance.decide(validation_result, require_approval=require_approval).__dict__
        results: list[dict[str, Any]] = []
        execution_metrics: dict[str, Any] = {"elapsed_ms": 0, "row_count": 0, "column_count": 0, "columns": []}
        if governance["allowed"] and validation_result.sanitized_sql:
            execution, execution_trace = self.execution_agent.run_with_trace(
                self.execution_agent.execute, validation_result.sanitized_sql
            )
            trace.append(execution_trace.__dict__)
            results = execution["results"]
            execution_metrics = execution["execution_metrics"]

        insights, insight_trace = self.insight_agent.run_with_trace(
            self.insight_agent.summarize, question, sql, results
        )
        trace.append(insight_trace.__dict__)

        visualization, visualization_trace = self.visualization_agent.run_with_trace(
            self.visualization_agent.recommend, results, intent
        )
        trace.append(visualization_trace.__dict__)

        total_elapsed_ms = round((time.perf_counter() - workflow_start) * 1000, 2)
        metrics = {
            "workflow_elapsed_ms": total_elapsed_ms,
            "execution": execution_metrics,
            "token_usage": self._estimate_token_usage(question, schema_context, sql),
            "generation_mode": generation["generation_mode"],
        }

        response = {
            "question": question,
            "role": role,
            "session_id": session_id,
            "intent": intent,
            "schema_context": schema_context,
            "sql": validation_result.sanitized_sql or sql,
            "validation": {
                "is_valid": validation_result.is_valid,
                "status": validation_result.status,
                "reasons": validation_result.reasons,
                "sanitized_sql": validation_result.sanitized_sql,
                "requires_approval": validation_result.requires_approval,
            },
            "governance": governance,
            "results": results,
            "summary": insights["summary"],
            "explanation": insights["explanation"],
            "visualization": visualization,
            "recommendations": insights["recommendations"],
            "trace": trace,
            "metrics": metrics,
        }

        self.memory_agent.remember(session_id, {
            "question": question,
            "sql": response["sql"],
            "summary": response["summary"],
            "governance_status": governance["status"],
            "row_count": execution_metrics.get("row_count", 0),
        })

        audit_event("text_to_sql_query", {
            "session_id": session_id,
            "role": role,
            "question": question,
            "validation_status": validation_result.status,
            "governance_status": governance["status"],
            "elapsed_ms": total_elapsed_ms,
        })
        return response

    def _estimate_token_usage(self, question: str, schema_context: dict[str, Any], sql: str) -> dict[str, int]:
        prompt_chars = len(question) + len(str(schema_context))
        completion_chars = len(sql)
        return {
            "prompt_tokens_estimate": max(1, prompt_chars // 4),
            "completion_tokens_estimate": max(1, completion_chars // 4),
            "total_tokens_estimate": max(1, (prompt_chars + completion_chars) // 4),
        }
