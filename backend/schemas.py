from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


# For a journal entry
class LineItem(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, decimal_places=2)


# Everything a user must submit
class ReportCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    reporting_period_start: date
    reporting_period_end: date
    income: list[LineItem] = Field(default_factory=list)
    expenses: list[LineItem] = Field(default_factory=list)
    notes: str | None = None
