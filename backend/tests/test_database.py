import tempfile
import unittest
from pathlib import Path

from backend import database
from backend.schemas import ReportCreate


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_database_path = database.DATABASE_PATH
        database.DATABASE_PATH = (
            Path(self.temporary_directory.name) / "test_reports.db"
        )
        database.initialize_database()

    def tearDown(self):
        database.DATABASE_PATH = self.original_database_path
        self.temporary_directory.cleanup()

    def test_create_and_retrieve_report(self):
        report = ReportCreate(
            title="Test report",
            reporting_period_start="2026-07-01",
            reporting_period_end="2026-07-31",
            income=[
                {"description": "Salary", "amount": "3000.00"},
            ],
            expenses=[
                {"description": "Rent", "amount": "1250.00"},
            ],
            notes="Database round-trip test",
        )

        report_id = database.create_report(report)
        saved_report = database.get_report(report_id)

        self.assertIsNotNone(saved_report)
        if saved_report is None:
            self.fail("The saved report could not be retrieved")

        self.assertEqual(saved_report.id, report_id)
        self.assertEqual(saved_report.title, report.title)
        self.assertEqual(
            saved_report.reporting_period_start,
            report.reporting_period_start,
        )
        self.assertEqual(
            saved_report.reporting_period_end,
            report.reporting_period_end,
        )
        self.assertEqual(saved_report.notes, report.notes)
        self.assertEqual(saved_report.income, report.income)
        self.assertEqual(saved_report.expenses, report.expenses)

    def test_get_report_returns_none_for_unknown_id(self):
        saved_report = database.get_report(999_999)

        self.assertIsNone(saved_report)

    def test_delete_report_cascades_to_line_items(self):
        report = ReportCreate(
            title="Report to delete",
            reporting_period_start="2026-07-01",
            reporting_period_end="2026-07-31",
            income=[
                {"description": "Salary", "amount": "3000.00"},
            ],
        )
        report_id = database.create_report(report)

        self.assertTrue(database.delete_report(report_id))
        self.assertIsNone(database.get_report(report_id))

        with database.connection_scope() as connection:
            item_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM line_items
                WHERE report_id = ?
                """,
                (report_id,),
            ).fetchone()[0]

        self.assertEqual(item_count, 0)


if __name__ == "__main__":
    unittest.main()
