import unittest

from pydantic import ValidationError

from backend.schemas import ReportCreate

# Make class for testing
class ReportCreateTests(unittest.TestCase):
    def test_rejects_end_date_before_start_date(self):
        with self.assertRaises(ValidationError):
            ReportCreate(
                title="Invalid report",
                reporting_period_start="2026-07-31",
                reporting_period_end="2026-07-01",
            )

    def test_rejects_whitespace_only_title(self):
        with self.assertRaises(ValidationError):
            ReportCreate(
                title="   ",
                reporting_period_start="2026-07-01",
                reporting_period_end="2026-07-31",
            )


if __name__ == "__main__":
    unittest.main()
