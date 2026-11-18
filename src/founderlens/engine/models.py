from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from founderlens.engine.accounts import Account
from founderlens.engine.types import Money, UTCDateTime


class Event(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    event_id: str
    type: str
    category: str
    description: str
    raw_text: str
    amount: Money = Field(gt=0)
    occurred_at: UTCDateTime


class Line(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    account: Account
    debit: Money
    credit: Money

    @model_validator(mode="after")
    def validate_posting(self):
        if self.debit < 0 or self.credit < 0:
            raise ValueError("debit and credit must be nonnegative")

        if (self.debit > 0) == (self.credit > 0):
            raise ValueError(
                "exactly one of debit or credit must be positive"
            )

        return self


class JournalEntry(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    event_id: str
    lines: tuple[Line, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_balanced_entry(self):
        total_debits = sum(
            (line.debit for line in self.lines),
            Decimal("0"),
        )

        total_credits = sum(
            (line.credit for line in self.lines),
            Decimal("0"),
        )

        if total_debits != total_credits:
            raise ValueError("journal entry must be balanced")

        return self


class Confidence(StrEnum):
    LOW = "LOW"
    HIGH = "HIGH"


class Stage(StrEnum):
    PRE_REVENUE = "PRE_REVENUE"
    EARLY_REVENUE = "EARLY_REVENUE"
    GROWING = "GROWING"
    SCALING = "SCALING"

class MetricsSnapshot(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    as_of: UTCDateTime
    cash: Money
    net_burn_30d: Money
    runway_months: Decimal | None = None
    confidence: Confidence
    stage: Stage
    data_days: int = Field(ge=0)