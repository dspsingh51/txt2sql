from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ColumnDefinition:
    name: str
    type: str
    description: str
    sensitivity: str = "standard"


@dataclass(frozen=True)
class TableDefinition:
    name: str
    description: str
    business_domain: str
    columns: tuple[ColumnDefinition, ...]

    def to_prompt_context(self) -> str:
        columns = "\n".join(
            f"  - {column.name} ({column.type}): {column.description} [{column.sensitivity}]"
            for column in self.columns
        )
        return f"Table: {self.name}\nDomain: {self.business_domain}\nDescription: {self.description}\nColumns:\n{columns}"


SCHEMA_CATALOG: dict[str, TableDefinition] = {
    "sales": TableDefinition(
        name="sales",
        business_domain="revenue",
        description="Regional product sales transactions with revenue, units, margin, and monthly periods.",
        columns=(
            ColumnDefinition("sale_id", "INTEGER", "Unique sale record identifier"),
            ColumnDefinition("sale_date", "DATE", "Transaction date"),
            ColumnDefinition("month", "TEXT", "Month in YYYY-MM format"),
            ColumnDefinition("quarter", "TEXT", "Fiscal quarter label"),
            ColumnDefinition("region", "TEXT", "Sales region"),
            ColumnDefinition("product", "TEXT", "Product line"),
            ColumnDefinition("customer_segment", "TEXT", "Customer segment"),
            ColumnDefinition("units_sold", "INTEGER", "Units sold"),
            ColumnDefinition("revenue", "REAL", "Gross revenue"),
            ColumnDefinition("gross_margin", "REAL", "Gross margin amount"),
        ),
    ),
    "finance": TableDefinition(
        name="finance",
        business_domain="finance",
        description="Monthly department-level financial performance including budget, actual spend, and variance.",
        columns=(
            ColumnDefinition("finance_id", "INTEGER", "Unique finance record identifier"),
            ColumnDefinition("month", "TEXT", "Month in YYYY-MM format"),
            ColumnDefinition("quarter", "TEXT", "Fiscal quarter label"),
            ColumnDefinition("department", "TEXT", "Business department"),
            ColumnDefinition("cost_center", "TEXT", "Internal cost center"),
            ColumnDefinition("budget", "REAL", "Planned budget"),
            ColumnDefinition("actual_cost", "REAL", "Actual spend"),
            ColumnDefinition("variance", "REAL", "Actual cost minus budget"),
        ),
    ),
    "operations": TableDefinition(
        name="operations",
        business_domain="operations",
        description="Operational metrics for fulfillment, support load, incident counts, and service performance.",
        columns=(
            ColumnDefinition("operation_id", "INTEGER", "Unique operations record identifier"),
            ColumnDefinition("month", "TEXT", "Month in YYYY-MM format"),
            ColumnDefinition("region", "TEXT", "Operating region"),
            ColumnDefinition("service_line", "TEXT", "Operational service line"),
            ColumnDefinition("tickets", "INTEGER", "Support or operations tickets"),
            ColumnDefinition("incidents", "INTEGER", "Incident count"),
            ColumnDefinition("avg_resolution_hours", "REAL", "Average resolution time in hours"),
            ColumnDefinition("operational_expense", "REAL", "Monthly operational expense"),
        ),
    ),
    "customer_analytics": TableDefinition(
        name="customer_analytics",
        business_domain="customer",
        description="Customer growth, churn, satisfaction, and recurring revenue metrics by segment and region.",
        columns=(
            ColumnDefinition("customer_metric_id", "INTEGER", "Unique customer metric identifier"),
            ColumnDefinition("month", "TEXT", "Month in YYYY-MM format"),
            ColumnDefinition("region", "TEXT", "Customer region"),
            ColumnDefinition("segment", "TEXT", "Customer segment"),
            ColumnDefinition("active_customers", "INTEGER", "Active customers"),
            ColumnDefinition("new_customers", "INTEGER", "New customers"),
            ColumnDefinition("churned_customers", "INTEGER", "Churned customers"),
            ColumnDefinition("churn_rate", "REAL", "Monthly churn rate"),
            ColumnDefinition("nps", "REAL", "Net promoter score"),
            ColumnDefinition("arr", "REAL", "Annual recurring revenue"),
            ColumnDefinition("account_owner_email", "TEXT", "Internal account owner email", "restricted"),
        ),
    ),
}


KEYWORD_TO_TABLES: dict[str, list[str]] = {
    "revenue": ["sales", "customer_analytics"],
    "sales": ["sales"],
    "region": ["sales", "operations", "customer_analytics"],
    "product": ["sales"],
    "margin": ["sales"],
    "cost": ["finance", "operations"],
    "budget": ["finance"],
    "variance": ["finance"],
    "expense": ["finance", "operations"],
    "operations": ["operations"],
    "incident": ["operations"],
    "ticket": ["operations"],
    "resolution": ["operations"],
    "churn": ["customer_analytics"],
    "customer": ["customer_analytics"],
    "nps": ["customer_analytics"],
    "arr": ["customer_analytics"],
    "kpi": ["sales", "finance", "operations", "customer_analytics"],
    "summary": ["sales", "finance", "operations", "customer_analytics"],
}


def rank_schema(question: str, limit: int = 3) -> list[TableDefinition]:
    normalized = question.lower()
    scores: dict[str, int] = {name: 0 for name in SCHEMA_CATALOG}
    for keyword, table_names in KEYWORD_TO_TABLES.items():
        if keyword in normalized:
            for table_name in table_names:
                scores[table_name] += 2
    for table_name, table in SCHEMA_CATALOG.items():
        if table_name.replace("_", " ") in normalized:
            scores[table_name] += 4
        for column in table.columns:
            if column.name.replace("_", " ") in normalized:
                scores[table_name] += 1
    ranked = sorted(SCHEMA_CATALOG.values(), key=lambda item: scores[item.name], reverse=True)
    selected = [table for table in ranked if scores[table.name] > 0]
    return (selected or ranked)[:limit]


def schema_as_dict() -> dict[str, Any]:
    return {
        name: {
            "description": table.description,
            "business_domain": table.business_domain,
            "columns": [column.__dict__ for column in table.columns],
        }
        for name, table in SCHEMA_CATALOG.items()
    }
