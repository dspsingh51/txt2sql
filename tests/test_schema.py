from sql_engine.schema import rank_schema


def test_rank_schema_revenue_region() -> None:
    tables = rank_schema("Show top revenue by region")
    names = [table.name for table in tables]
    assert "sales" in names


def test_rank_schema_churn() -> None:
    tables = rank_schema("Find customer churn trends")
    assert tables[0].name == "customer_analytics"
