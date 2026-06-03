from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3)
    role: str = Field(default="analyst")
    session_id: str = Field(default="demo-session")
    database: str = Field(default="sqlite")
    require_approval: bool = Field(default=False)


class ValidationReport(BaseModel):
    is_valid: bool
    status: str
    reasons: list[str] = Field(default_factory=list)
    sanitized_sql: str | None = None
    requires_approval: bool = False


class WorkflowTraceEvent(BaseModel):
    agent: str
    status: str
    elapsed_ms: float
    details: dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    question: str
    role: str
    session_id: str
    intent: dict[str, Any]
    schema_context: dict[str, Any]
    sql: str
    validation: ValidationReport
    governance: dict[str, Any]
    results: list[dict[str, Any]]
    summary: str
    explanation: str
    visualization: dict[str, Any]
    recommendations: list[str]
    trace: list[WorkflowTraceEvent]
    metrics: dict[str, Any]


class HistoryResponse(BaseModel):
    session_id: str
    history: list[dict[str, Any]]
