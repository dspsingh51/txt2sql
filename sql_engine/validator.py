import re
from dataclasses import dataclass, field

try:
    import sqlparse
except ImportError:  # pragma: no cover - dependency included in requirements
    sqlparse = None


BLOCKED_KEYWORDS = {
    "ALTER",
    "CREATE",
    "DELETE",
    "DROP",
    "EXEC",
    "EXECUTE",
    "INSERT",
    "MERGE",
    "REPLACE",
    "TRUNCATE",
    "UPDATE",
    "VACUUM",
}

ROLE_TABLE_ALLOWLIST: dict[str, set[str]] = {
    "executive": {"sales", "finance", "operations", "customer_analytics"},
    "analyst": {"sales", "finance", "operations", "customer_analytics"},
    "finance": {"finance", "sales"},
    "support": {"customer_analytics", "operations"},
    "sales": {"sales", "customer_analytics"},
}

RESTRICTED_COLUMNS = {"account_owner_email"}


@dataclass
class SqlValidationResult:
    is_valid: bool
    status: str
    reasons: list[str] = field(default_factory=list)
    sanitized_sql: str | None = None
    requires_approval: bool = False
    referenced_tables: set[str] = field(default_factory=set)


class SQLValidator:
    def __init__(self, read_only: bool = True) -> None:
        self.read_only = read_only

    def validate(self, sql: str, role: str = "analyst") -> SqlValidationResult:
        reasons: list[str] = []
        sanitized_sql = self._normalize(sql)
        upper_sql = sanitized_sql.upper()

        if not sanitized_sql:
            reasons.append("SQL is empty.")

        if self._has_multiple_statements(sanitized_sql):
            reasons.append("Only one SQL statement is allowed.")

        if not upper_sql.startswith(("SELECT", "WITH")):
            reasons.append("Only read-only SELECT or WITH statements are allowed.")

        blocked = sorted(keyword for keyword in BLOCKED_KEYWORDS if re.search(rf"\b{keyword}\b", upper_sql))
        if blocked:
            reasons.append(f"Blocked destructive or unsafe keyword(s): {', '.join(blocked)}.")

        if "--" in sanitized_sql or "/*" in sanitized_sql or "*/" in sanitized_sql:
            reasons.append("SQL comments are not allowed in executable queries.")

        referenced_tables = self._extract_tables(sanitized_sql)
        allowed_tables = ROLE_TABLE_ALLOWLIST.get(role, ROLE_TABLE_ALLOWLIST["analyst"])
        disallowed_tables = sorted(table for table in referenced_tables if table not in allowed_tables)
        if disallowed_tables:
            reasons.append(f"Role '{role}' cannot query table(s): {', '.join(disallowed_tables)}.")

        restricted_columns = sorted(column for column in RESTRICTED_COLUMNS if re.search(rf"\b{column}\b", sanitized_sql, re.I))
        if restricted_columns:
            reasons.append(f"Restricted column(s) require elevated approval: {', '.join(restricted_columns)}.")

        requires_approval = self._requires_approval(sanitized_sql, referenced_tables, restricted_columns)
        status = "approved" if not reasons and not requires_approval else "needs_approval" if not reasons else "blocked"

        return SqlValidationResult(
            is_valid=not reasons,
            status=status,
            reasons=reasons,
            sanitized_sql=sanitized_sql if not reasons else None,
            requires_approval=requires_approval,
            referenced_tables=referenced_tables,
        )

    def _normalize(self, sql: str) -> str:
        stripped = sql.strip()
        if sqlparse:
            stripped = sqlparse.format(stripped, strip_comments=False, reindent=False, keyword_case="upper")
        return stripped.rstrip(";") + ";" if stripped else ""

    def _has_multiple_statements(self, sql: str) -> bool:
        if not sqlparse:
            return sql.count(";") > 1
        statements = [statement for statement in sqlparse.parse(sql) if statement.value.strip("; \n\t")]
        return len(statements) > 1

    def _extract_tables(self, sql: str) -> set[str]:
        candidates = set(re.findall(r"\bFROM\s+([a-zA-Z_][\w]*)|\bJOIN\s+([a-zA-Z_][\w]*)", sql, re.I))
        tables = {name.lower() for pair in candidates for name in pair if name}
        return tables

    def _requires_approval(self, sql: str, tables: set[str], restricted_columns: list[str]) -> bool:
        if restricted_columns:
            return True
        broad_customer_scan = "customer_analytics" in tables and "LIMIT" not in sql.upper()
        finance_detail_scan = "finance" in tables and re.search(r"\bSELECT\s+\*", sql, re.I) is not None
        return broad_customer_scan or finance_detail_scan
