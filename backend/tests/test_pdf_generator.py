import unittest

from backend.schemas import ReportRead
from backend.services.pdf_generator import generate_report_pdf


class PdfGeneratorTests(unittest.TestCase):
    def test_generates_pdf_bytes(self):
        report = ReportRead(
            id=1,
            title="PDF test report",
            reporting_period_start="2026-07-01",
            reporting_period_end="2026-07-31",
            income=[
                {
                    "description": "Salary",
                    "amount": "3000.00",
                }
            ],
            expenses=[
                {
                    "description": "Rent",
                    "amount": "1250.00",
                }
            ],
            notes="PDF test",
            created_at="2026-07-31T12:00:00",
        )

        pdf_bytes = generate_report_pdf(report)

        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 100)


if __name__ == "__main__":
    unittest.main()
