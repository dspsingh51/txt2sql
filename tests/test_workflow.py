from pathlib import Path

from configs.settings import get_settings
from sql_engine.seed import seed_sqlite, write_csvs
from workflows.text_to_sql_graph import TextToSQLWorkflow


def test_workflow_generates_valid_revenue_query() -> None:
    settings = get_settings()
    write_csvs(Path("datasets"))
    seed_sqlite(settings.sqlite_path)
    response = TextToSQLWorkflow().run(
        question="Show top 5 revenue generating regions",
        role="analyst",
        session_id="test-session",
    )
    assert response["validation"]["is_valid"]
    assert response["governance"]["status"] == "approved"
    assert response["results"]
    assert "sales" in response["sql"].lower()
