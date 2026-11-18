# test_types.py
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import BaseModel, ValidationError

from founderlens.engine.types import Money, UTCDateTime


class Event(BaseModel):
    timestamp: UTCDateTime


def test_rejects_naive_datetime():
    """A datetime without timezone information should be rejected."""

    naive_datetime = datetime(2026, 11, 16, 12, 0, 0)

    with pytest.raises(ValidationError):
        Event(timestamp=naive_datetime)


def test_normalizes_non_utc_datetime():
    """A datetime with a non-UTC timezone should be converted to UTC."""

    non_utc_datetime = datetime(
        2026, 11, 16, 15, 0, 0,
        tzinfo=timezone(timedelta(hours=3))
    )

    event = Event(timestamp=non_utc_datetime)

    assert event.timestamp == datetime(
        2026, 11, 16, 12, 0, 0,
        tzinfo=UTC
    )

    assert event.timestamp.utcoffset() == timedelta(0)
   


class Payment(BaseModel):
    amount: Money


def test_rejects_too_many_decimal_places():
    with pytest.raises(ValidationError):
        Payment(amount=Decimal("0.001"))


def test_rejects_nan():
    with pytest.raises(ValidationError):
        Payment(amount=Decimal("NaN"))