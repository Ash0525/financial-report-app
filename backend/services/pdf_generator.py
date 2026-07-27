from io import BytesIO
from decimal import Decimal
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.units import inch

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

def format_currency(amount: Decimal) -> str:
    return f"${amount:,.2f}"

def build_line_item_table(
    items: list[schemas.LineItem],
) -> tuple[Table, Decimal]:
    total = sum(
        (item.amount for item in items),
        start=Decimal("0"),
    )

    rows = [
        ["Description", "Amount"],
    ]

    for item in items:
        rows.append(
            [
                item.description,
                format_currency(item.amount),
            ]
        )

    rows.append(
        [
            "Total",
            format_currency(total),
        ]
    )

    table = Table(
        rows,
        colWidths=[4.5 * inch, 1.5 * inch],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    return table, total

