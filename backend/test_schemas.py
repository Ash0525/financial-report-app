import unittest

from pydantic import ValidationError
from schemas import ReportCreate

# Make class for testing
class ReportCreateTests(unittest.TestCase):
    # If end date is before start date
    def test_rejects_end_date_before_start_date(self):
        
        with self.assertRaises(ValidationError):
            ReportCreate(
                title="Invalid report",
                reporting_period_start="2026-07-31",
                reporting_period_end="2026-07-01",
            )

if __name__ == "__main__":
    unittest.main()