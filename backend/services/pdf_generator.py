from decimal import Decimal
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend import schemas


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


def generate_report_pdf(report: schemas.ReportRead) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title=report.title,
    )

    styles = getSampleStyleSheet()

    income_table, income_total = build_line_item_table(
        report.income
    )
    expense_table, expense_total = build_line_item_table(
        report.expenses
    )
    net_balance = income_total - expense_total

    notes = escape(report.notes or "No notes provided.").replace(
        "\n",
        "<br/>",
    )

    content = [
        Paragraph(escape(report.title), styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            (
                f"Reporting period: "
                f"{report.reporting_period_start} to "
                f"{report.reporting_period_end}"
            ),
            styles["BodyText"],
        ),
        Spacer(1, 20),
        Paragraph("Income", styles["Heading2"]),
        income_table,
        Spacer(1, 20),
        Paragraph("Expenses", styles["Heading2"]),
        expense_table,
        Spacer(1, 20),
        Paragraph(
            f"Net balance: {format_currency(net_balance)}",
            styles["Heading2"],
        ),
        Spacer(1, 20),
        Paragraph("Notes", styles["Heading2"]),
        Paragraph(notes, styles["BodyText"]),
    ]

    document.build(content)

    return buffer.getvalue()
