from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from backend import schemas

def generate_report_pdf(report: schemas.ReportRead) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title=report.title,
    )

    styles = getSampleStyleSheet()

    content = [
        Paragraph(report.title, styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            (
                f"Reporting period: "
                f"{report.reporting_period_start} to "
                f"{report.reporting_period_end}"
            ),
            styles["BodyText"],
        ),
    ]

    document.build(content)

    return buffer.getvalue()