from fastapi import APIRouter

from api.schemas import HistoryResponse, QueryRequest, QueryResponse
from memory.store import MemoryStore
from sql_engine.connection import describe_connection
from sql_engine.schema import schema_as_dict
from workflows.text_to_sql_graph import TextToSQLWorkflow

router = APIRouter()
workflow = TextToSQLWorkflow()
memory_store = MemoryStore()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> dict:
    return workflow.run(
        question=request.question,
        role=request.role,
        session_id=request.session_id,
        require_approval=request.require_approval,
    )


@router.get("/schema")
def schema() -> dict:
    return schema_as_dict()


@router.get("/history/{session_id}", response_model=HistoryResponse)
def history(session_id: str) -> dict:
    return {"session_id": session_id, "history": memory_store.get_history(session_id)}


@router.get("/connection")
def connection() -> dict:
    return describe_connection()
