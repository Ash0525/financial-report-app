from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, model_validator

ShortText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]


class LineItem(BaseModel):
    """A single income or expense entry."""

    description: ShortText
    amount: Decimal = Field(gt=0, decimal_places=2)


class ReportCreate(BaseModel):
    """Validated input required to create a financial report."""

    title: ShortText
    reporting_period_start: date
    reporting_period_end: date
    income: list[LineItem] = Field(default_factory=list)
    expenses: list[LineItem] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=5_000)

    @model_validator(mode="after")
    def validate_reporting_period(self) -> "ReportCreate":
        if self.reporting_period_end < self.reporting_period_start:
            raise ValueError(
                "Reporting period end date cannot be before the start date"
            )

        return self


class ReportRead(ReportCreate):
    """A complete report returned from persistent storage."""

    id: int
    created_at: datetime


class ReportSummary(BaseModel):
    """The lightweight report representation used in list views."""

    id: int
    title: str
    reporting_period_start: date
    reporting_period_end: date
    created_at: datetime
