import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from . import schemas

DATABASE_PATH = Path(__file__).with_name("reports.db")


def get_connection() -> sqlite3.Connection:
    """Open and configure a connection to the application database."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def connection_scope() -> Iterator[sqlite3.Connection]:
    """Commit or roll back a transaction and always close its connection."""

    connection = get_connection()
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database() -> None:
    """Create the application tables and indexes when they do not exist."""

    with connection_scope() as connection:
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

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_line_items_report_id
            ON line_items (report_id)
            """
        )


def create_report(report: schemas.ReportCreate) -> int:
    """Persist a report and all line items in one transaction."""

    with connection_scope() as connection:
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

        return report_id


def get_report(report_id: int) -> schemas.ReportRead | None:
    """Return one complete report, or None when its ID does not exist."""

    with connection_scope() as connection:
        report_row = connection.execute(
            """
            SELECT
                id,
                title,
                reporting_period_start,
                reporting_period_end,
                notes,
                created_at
            FROM reports
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()

        if report_row is None:
            return None

        item_rows = connection.execute(
            """
            SELECT
                item_type,
                description,
                amount
            FROM line_items
            WHERE report_id = ?
            ORDER BY id
            """,
            (report_id,),
        ).fetchall()

        income: list[dict[str, str]] = []
        expenses: list[dict[str, str]] = []

        for item_row in item_rows:
            line_item = {
                "description": item_row["description"],
                "amount": item_row["amount"],
            }

            if item_row["item_type"] == "income":
                income.append(line_item)
            else:
                expenses.append(line_item)

        return schemas.ReportRead(
            id=report_row["id"],
            title=report_row["title"],
            reporting_period_start=report_row["reporting_period_start"],
            reporting_period_end=report_row["reporting_period_end"],
            income=income,
            expenses=expenses,
            notes=report_row["notes"],
            created_at=report_row["created_at"],
        )


def list_reports() -> list[schemas.ReportSummary]:
    """Return lightweight summaries ordered newest first."""

    with connection_scope() as connection:
        report_rows = connection.execute(
            """
            SELECT
                id,
                title,
                reporting_period_start,
                reporting_period_end,
                created_at
            FROM reports
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

        return [
            schemas.ReportSummary(
                id=row["id"],
                title=row["title"],
                reporting_period_start=row["reporting_period_start"],
                reporting_period_end=row["reporting_period_end"],
                created_at=row["created_at"],
            )
            for row in report_rows
        ]


def delete_report(report_id: int) -> bool:
    """Delete a report and its line items, returning whether it existed."""

    with connection_scope() as connection:
        cursor = connection.execute(
            """
            DELETE FROM reports
            WHERE id = ?
            """,
            (report_id,),
        )

        return cursor.rowcount > 0


def delete_all_reports() -> int:
    """Delete every report and return the number deleted."""

    with connection_scope() as connection:
        cursor = connection.execute(
            """
            DELETE FROM reports
            """
        )

        return cursor.rowcount
