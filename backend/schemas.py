from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


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

    @model_validator(mode="after")
    def validate_reporting_period(self):
        # Data check 
        if self.reporting_period_end < self.reporting_period_start:
            raise ValueError(
                "Reporting period end date cannot be before the start date"
            )

        return self


# Object for reading the report
class ReportRead(ReportCreate):
    # ID is an integer
    id: int

    # Get the date time
    created_at: datetime

