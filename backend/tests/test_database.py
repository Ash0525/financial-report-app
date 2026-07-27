import sqlite3
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

    def test_backup_contains_saved_reports(self):
        report = ReportCreate(
            title="Backed-up report",
            reporting_period_start="2026-07-01",
            reporting_period_end="2026-07-31",
        )
        database.create_report(report)

        backup_directory = (
            Path(self.temporary_directory.name) / "backups"
        )
        backup_path = database.create_database_backup(
            backup_directory=backup_directory
        )

        self.assertTrue(backup_path.exists())
        with sqlite3.connect(backup_path) as connection:
            saved_title = connection.execute(
                "SELECT title FROM reports"
            ).fetchone()[0]

        self.assertEqual(saved_title, "Backed-up report")

    def test_backup_retention_removes_oldest_backups(self):
        backup_directory = (
            Path(self.temporary_directory.name) / "backups"
        )

        for _ in range(3):
            database.create_database_backup(
                backup_directory=backup_directory,
                retention=2,
            )

        backup_paths = list(backup_directory.glob("reports-*.db"))
        self.assertEqual(len(backup_paths), 2)

    def test_backup_rejects_invalid_retention(self):
        with self.assertRaises(ValueError):
            database.create_database_backup(retention=0)


class DatabaseStorageTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        temporary_path = Path(self.temporary_directory.name)

        self.original_database_path = database.DATABASE_PATH
        self.original_default_database_path = database.DEFAULT_DATABASE_PATH
        self.original_legacy_database_path = database.LEGACY_DATABASE_PATH

        database.DEFAULT_DATABASE_PATH = temporary_path / "data" / "reports.db"
        database.DATABASE_PATH = database.DEFAULT_DATABASE_PATH
        database.LEGACY_DATABASE_PATH = (
            temporary_path / "legacy" / "reports.db"
        )

    def tearDown(self):
        database.DATABASE_PATH = self.original_database_path
        database.DEFAULT_DATABASE_PATH = self.original_default_database_path
        database.LEGACY_DATABASE_PATH = self.original_legacy_database_path
        self.temporary_directory.cleanup()

    def test_prepare_database_storage_creates_data_directory(self):
        database.prepare_database_storage()

        self.assertTrue(database.DATABASE_PATH.parent.is_dir())

    def test_prepare_database_storage_migrates_legacy_database(self):
        database.LEGACY_DATABASE_PATH.parent.mkdir(parents=True)
        with sqlite3.connect(database.LEGACY_DATABASE_PATH) as connection:
            connection.execute(
                "CREATE TABLE migration_check (value TEXT NOT NULL)"
            )
            connection.execute(
                "INSERT INTO migration_check (value) VALUES (?)",
                ("preserved",),
            )

        database.prepare_database_storage()

        with sqlite3.connect(database.DATABASE_PATH) as connection:
            migrated_value = connection.execute(
                "SELECT value FROM migration_check"
            ).fetchone()[0]

        self.assertEqual(migrated_value, "preserved")

    def test_prepare_database_storage_does_not_overwrite_database(self):
        database.DEFAULT_DATABASE_PATH.parent.mkdir(parents=True)
        with sqlite3.connect(database.DEFAULT_DATABASE_PATH) as connection:
            connection.execute(
                "CREATE TABLE destination (value TEXT NOT NULL)"
            )

        database.LEGACY_DATABASE_PATH.parent.mkdir(parents=True)
        with sqlite3.connect(database.LEGACY_DATABASE_PATH) as connection:
            connection.execute("CREATE TABLE legacy (value TEXT NOT NULL)")

        database.prepare_database_storage()

        with sqlite3.connect(database.DATABASE_PATH) as connection:
            destination_table = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'destination'
                """
            ).fetchone()
            legacy_table = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'legacy'
                """
            ).fetchone()

        self.assertIsNotNone(destination_table)
        self.assertIsNone(legacy_table)


if __name__ == "__main__":
    unittest.main()
