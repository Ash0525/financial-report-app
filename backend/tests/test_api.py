import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend import database, main


# for testing report api
class ReportApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_database_path = database.DATABASE_PATH
        database.DATABASE_PATH = (
            Path(self.temporary_directory.name) / "test_reports.db"
        )

        self.client = TestClient(main.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        database.DATABASE_PATH = self.original_database_path
        self.temporary_directory.cleanup()

    def test_report_lifecycle(self):
        report_data = {
            "title": "API test report",
            "reporting_period_start": "2026-07-01",
            "reporting_period_end": "2026-07-31",
            "income": [
                {
                    "description": "Salary",
                    "amount": "3000.00",
                }
            ],
            "expenses": [
                {
                    "description": "Rent",
                    "amount": "1250.00",
                }
            ],
            "notes": "Created by an API test",
        }

        create_response = self.client.post(
            "/reports",
            json=report_data,
        )

        self.assertEqual(create_response.status_code, 201)
        report_id = create_response.json()["id"]

        get_response = self.client.get(f"/reports/{report_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(
            get_response.json()["title"],
            "API test report",
        )

        list_response = self.client.get("/reports")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        pdf_response = self.client.get(
            f"/reports/{report_id}/pdf"
        )
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(
            pdf_response.headers["content-type"],
            "application/pdf",
        )
        self.assertEqual(
            pdf_response.headers["content-disposition"],
            f'attachment; filename="report-{report_id}.pdf"',
        )
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

        delete_response = self.client.delete(
            f"/reports/{report_id}"
        )
        self.assertEqual(delete_response.status_code, 204)

        missing_response = self.client.get(
            f"/reports/{report_id}"
        )
        self.assertEqual(missing_response.status_code, 404)

    def test_rejects_invalid_report(self):
        response = self.client.post(
            "/reports",
            json={
                "title": "Invalid dates",
                "reporting_period_start": "2026-07-31",
                "reporting_period_end": "2026-07-01",
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_pdf_returns_not_found_for_unknown_report(self):
        response = self.client.get("/reports/999999/pdf")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
