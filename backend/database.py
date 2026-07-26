import sqlite3
from pathlib import Path
import schemas

DATABASE_PATH = Path(__file__).with_name("reports.db")

# Open data for connections
def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    print("[status] connection established")
    return connection

def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                reporting_period_start TEXT NOT NULL,
                reporting_period_end TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS line_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                item_type TEXT NOT NULL CHECK (item_type IN ('income', 'expense')),
                description TEXT NOT NULL,
                amount TEXT NOT NULL,
                FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
            )
            """
        )

    print("[status] database initialized")

def create_report(report: schemas.ReportCreate) -> int:
    with get_connection() as connection: 
        cursor = connection.execute(
            """
            INSERT INTO reports (
                title,
                reporting_period_start,
                reporting_period_end,
                notes
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                report.title,
                report.reporting_period_start.isoformat(),
                report.reporting_period_end.isoformat(),
                report.notes,
            ),
        )

        report_id = cursor.lastrowid

        # If none, report runtime
        if report_id is None:
            raise RuntimeError("Database did not return a report ID")
        
        line_items = [
            (
                report_id,
                "income",
                item.description,
                str(item.amount),
            )
            for item in report.income
        ]

        line_items.extend(
            (
                report_id,
                "expense",
                item.description,
                str(item.amount),
            )
            for item in report.expenses
        )

        if line_items:
            connection.executemany(
                """
                INSERT INTO line_items (
                    report_id,
                    item_type,
                    description,
                    amount
                )
                VALUES (?, ?, ?, ?)
                """,
                line_items,
            )
        
        print(line_items)
        return report_id