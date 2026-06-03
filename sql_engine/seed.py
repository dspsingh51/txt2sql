import csv
import sqlite3
from pathlib import Path

from configs.settings import get_settings


DATASETS = {
    "sales": [
        ["sale_id", "sale_date", "month", "quarter", "region", "product", "customer_segment", "units_sold", "revenue", "gross_margin"],
        [1, "2025-01-12", "2025-01", "Q1", "North America", "Cloud Analytics", "Enterprise", 42, 184000, 73600],
        [2, "2025-02-18", "2025-02", "Q1", "Europe", "Cloud Analytics", "Mid-Market", 28, 98000, 37240],
        [3, "2025-03-21", "2025-03", "Q1", "Asia Pacific", "AI Copilot", "Enterprise", 35, 171500, 72030],
        [4, "2025-04-09", "2025-04", "Q2", "North America", "AI Copilot", "Enterprise", 30, 151000, 58890],
        [5, "2025-05-15", "2025-05", "Q2", "Europe", "Data Governance", "Enterprise", 22, 118000, 50740],
        [6, "2025-06-22", "2025-06", "Q2", "Latin America", "Cloud Analytics", "SMB", 18, 54000, 17820],
        [7, "2025-07-07", "2025-07", "Q3", "Asia Pacific", "Data Governance", "Enterprise", 31, 167000, 68470],
        [8, "2025-08-19", "2025-08", "Q3", "North America", "Cloud Analytics", "Mid-Market", 47, 199000, 79600],
        [9, "2025-09-26", "2025-09", "Q3", "Europe", "AI Copilot", "Enterprise", 39, 188000, 80840],
        [10, "2025-10-11", "2025-10", "Q4", "Asia Pacific", "Cloud Analytics", "SMB", 26, 83000, 28220],
        [11, "2025-11-17", "2025-11", "Q4", "North America", "Data Governance", "Enterprise", 33, 176000, 75680],
        [12, "2025-12-05", "2025-12", "Q4", "Europe", "Cloud Analytics", "Enterprise", 44, 205000, 86100],
    ],
    "finance": [
        ["finance_id", "month", "quarter", "department", "cost_center", "budget", "actual_cost", "variance"],
        [1, "2025-01", "Q1", "Engineering", "ENG-101", 210000, 218000, 8000],
        [2, "2025-02", "Q1", "Sales", "SAL-201", 150000, 143000, -7000],
        [3, "2025-03", "Q1", "Operations", "OPS-301", 98000, 101500, 3500],
        [4, "2025-04", "Q2", "Engineering", "ENG-101", 215000, 229000, 14000],
        [5, "2025-05", "Q2", "Marketing", "MKT-401", 122000, 139000, 17000],
        [6, "2025-06", "Q2", "Operations", "OPS-301", 104000, 117000, 13000],
        [7, "2025-07", "Q3", "Sales", "SAL-201", 158000, 160500, 2500],
        [8, "2025-08", "Q3", "Engineering", "ENG-101", 220000, 219500, -500],
        [9, "2025-09", "Q3", "Customer Success", "CS-501", 93000, 97000, 4000],
        [10, "2025-10", "Q4", "Operations", "OPS-301", 109000, 112000, 3000],
        [11, "2025-11", "Q4", "Marketing", "MKT-401", 128000, 124000, -4000],
        [12, "2025-12", "Q4", "Engineering", "ENG-101", 225000, 232000, 7000],
    ],
    "operations": [
        ["operation_id", "month", "region", "service_line", "tickets", "incidents", "avg_resolution_hours", "operational_expense"],
        [1, "2025-01", "North America", "Cloud Support", 312, 12, 8.4, 72000],
        [2, "2025-02", "Europe", "Cloud Support", 244, 9, 7.9, 61000],
        [3, "2025-03", "Asia Pacific", "Implementation", 198, 7, 12.3, 68000],
        [4, "2025-04", "North America", "Implementation", 287, 15, 13.8, 82000],
        [5, "2025-05", "Europe", "Cloud Support", 265, 10, 8.1, 66000],
        [6, "2025-06", "Latin America", "Cloud Support", 176, 11, 10.5, 54000],
        [7, "2025-07", "Asia Pacific", "Implementation", 221, 8, 11.7, 70000],
        [8, "2025-08", "North America", "Cloud Support", 336, 14, 8.9, 76000],
        [9, "2025-09", "Europe", "Implementation", 208, 6, 10.2, 64000],
        [10, "2025-10", "Asia Pacific", "Cloud Support", 233, 9, 9.4, 69000],
        [11, "2025-11", "North America", "Implementation", 301, 16, 14.6, 85000],
        [12, "2025-12", "Europe", "Cloud Support", 278, 8, 7.6, 63000],
    ],
    "customer_analytics": [
        ["customer_metric_id", "month", "region", "segment", "active_customers", "new_customers", "churned_customers", "churn_rate", "nps", "arr", "account_owner_email"],
        [1, "2025-01", "North America", "Enterprise", 420, 24, 11, 0.026, 54, 8200000, "owner-na@example.com"],
        [2, "2025-02", "Europe", "Mid-Market", 310, 19, 12, 0.039, 47, 4100000, "owner-eu@example.com"],
        [3, "2025-03", "Asia Pacific", "Enterprise", 235, 17, 8, 0.034, 51, 3600000, "owner-apac@example.com"],
        [4, "2025-04", "North America", "Enterprise", 433, 20, 18, 0.042, 49, 8350000, "owner-na@example.com"],
        [5, "2025-05", "Europe", "Enterprise", 298, 16, 15, 0.050, 44, 4300000, "owner-eu@example.com"],
        [6, "2025-06", "Latin America", "SMB", 188, 14, 13, 0.069, 39, 1200000, "owner-latam@example.com"],
        [7, "2025-07", "Asia Pacific", "Enterprise", 246, 21, 9, 0.037, 52, 3850000, "owner-apac@example.com"],
        [8, "2025-08", "North America", "Mid-Market", 451, 31, 10, 0.022, 58, 8700000, "owner-na@example.com"],
        [9, "2025-09", "Europe", "Enterprise", 316, 22, 11, 0.035, 55, 4560000, "owner-eu@example.com"],
        [10, "2025-10", "Asia Pacific", "SMB", 259, 20, 13, 0.050, 46, 2100000, "owner-apac@example.com"],
        [11, "2025-11", "North America", "Enterprise", 468, 29, 14, 0.030, 57, 9100000, "owner-na@example.com"],
        [12, "2025-12", "Europe", "Enterprise", 332, 25, 9, 0.027, 60, 4920000, "owner-eu@example.com"],
    ],
}


def write_csvs(dataset_dir: Path) -> None:
    dataset_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in DATASETS.items():
        with (dataset_dir / f"{name}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)


def seed_sqlite(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        for name, rows in DATASETS.items():
            header = rows[0]
            connection.execute(f"DROP TABLE IF EXISTS {name}")
            column_defs = ", ".join(_column_definition(column) for column in header)
            connection.execute(f"CREATE TABLE {name} ({column_defs})")
            placeholders = ", ".join("?" for _ in header)
            connection.executemany(f"INSERT INTO {name} VALUES ({placeholders})", rows[1:])
        connection.commit()


def _column_definition(column: str) -> str:
    if column.endswith("_id"):
        return f"{column} INTEGER"
    if column in {"units_sold", "tickets", "incidents", "active_customers", "new_customers", "churned_customers"}:
        return f"{column} INTEGER"
    if column in {"revenue", "gross_margin", "budget", "actual_cost", "variance", "avg_resolution_hours", "operational_expense", "churn_rate", "nps", "arr"}:
        return f"{column} REAL"
    return f"{column} TEXT"


def main() -> None:
    settings = get_settings()
    dataset_dir = Path("datasets")
    write_csvs(dataset_dir)
    seed_sqlite(settings.sqlite_path)
    print(f"Seeded {settings.sqlite_path} and CSV datasets in {dataset_dir}")


if __name__ == "__main__":
    main()
