from schemas import ReportCreate
import database

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

    database.initialize_database()

    report_id = database.create_report(report)

    print(f"Saved report with ID {report_id}")

    saved_report = database.get_report(report_id)

    if saved_report is None:
        print("Report not found")
    else:
        print("Retrieved report:")
        print(saved_report)

    report_summaries = database.list_reports()

    print("All reports:")
    for summary in report_summaries:
        print(summary)

    was_deleted = database.delete_report(report_id)
    print(f"Deleted: {was_deleted}")

    deleted_report = database.get_report(report_id)
    print(f"Report after deletion: {deleted_report}")

