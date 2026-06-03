from sql_engine.validator import SQLValidator


def test_validator_allows_select() -> None:
    result = SQLValidator().validate("SELECT region, SUM(revenue) FROM sales GROUP BY region", "analyst")
    assert result.is_valid
    assert result.status == "approved"
    assert result.sanitized_sql is not None


def test_validator_blocks_drop() -> None:
    result = SQLValidator().validate("DROP TABLE sales", "analyst")
    assert not result.is_valid
    assert "DROP" in result.reasons[0]


def test_validator_blocks_multi_statement() -> None:
    result = SQLValidator().validate("SELECT * FROM sales; DELETE FROM sales;", "analyst")
    assert not result.is_valid
    assert any("Only one SQL statement" in reason for reason in result.reasons)


def test_role_restriction() -> None:
    result = SQLValidator().validate("SELECT * FROM finance", "support")
    assert not result.is_valid
    assert any("cannot query" in reason for reason in result.reasons)


def test_sensitive_column_requires_approval() -> None:
    result = SQLValidator().validate("SELECT account_owner_email FROM customer_analytics LIMIT 10", "analyst")
    assert not result.is_valid
    assert any("Restricted column" in reason for reason in result.reasons)
