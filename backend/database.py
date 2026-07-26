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
    
# Use get_report to access the ReportRead
def get_report(report_id: int) -> schemas.ReportRead | None:

    # Get the connection with the SQL table
    with get_connection() as connection:

        # Get the report_row from the SQL table
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

        # If the report_row doesn't work
        if report_row is None:
            print("[error] report_row doesn't exist")
            return None

        # Get the item_rows from the SQL table
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

        # Initialize income and expenses lists
        income = []
        expenses = []

        # Iterate through item_rows, get each line_item
        for item_row in item_rows:
            line_item = {
                "description": item_row["description"],
                "amount": item_row["amount"],
            }
            
            # Separate the income from the expenses
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

# Get summary list report
def list_reports() -> list[schemas.ReportSummary]:
    with get_connection() as connection:
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

        reports = []

        for row in report_rows:
            report = schemas.ReportSummary(
                id=row["id"],
                title=row["title"],
                reporting_period_start=row["reporting_period_start"],
                reporting_period_end=row["reporting_period_end"],
                created_at=row["created_at"],
            )
            reports.append(report)
        
        return reports