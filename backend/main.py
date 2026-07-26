from schemas import ReportCreate


# Temporary example until the API entry point is implemented.
if __name__ == "__main__":
    report = ReportCreate(
        title="July 2026 Report",
        reporting_period_start="2026-07-01",
        reporting_period_end="2026-07-31",
        income=[
            {"description": "Salary", "amount": "3000.00"},
        ],
        expenses=[
            {"description": "Rent", "amount": "1250.00"},
        ],
    )

    print(report)
    print(report.model_dump())
