from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from founderlens.engine.accounts import Account
from founderlens.engine.models import (
    Confidence,
    Event,
    JournalEntry,
    Line,
    MetricsSnapshot,
    Stage,
)

# Shared valid event: each rejection test changes only one field.
VALID_EVENT = {
    "event_id": "EVT-001",
    "type": "transaction",
    "category": "sales",
    "description": "Customer payment",
    "raw_text": "Received 250.00 from customer",
    "amount": Decimal("250.00"),
    "occurred_at": datetime(
        2026, 11, 16, 12, 0, 0, tzinfo=UTC
    ),
}


def test_event_accepts_valid_data():
    event = Event(**VALID_EVENT)

    assert event.event_id == "EVT-001"
    assert event.amount == Decimal("250.00")
    assert event.occurred_at.tzinfo is not None


def test_event_rejects_zero_amount():
    data = VALID_EVENT.copy()
    data["amount"] = Decimal("0")

    with pytest.raises(ValidationError):
        Event(**data)


def test_event_rejects_negative_amount():
    data = VALID_EVENT.copy()
    data["amount"] = Decimal("-10.00")

    with pytest.raises(ValidationError):
        Event(**data)


def test_event_rejects_naive_timestamp():
    data = VALID_EVENT.copy()
    data["occurred_at"] = datetime(2026, 11, 16, 12, 0, 0)

    with pytest.raises(ValidationError):
        Event(**data)


def test_event_rejects_unexpected_field():
    data = VALID_EVENT.copy()
    data["customer_name"] = "John"

    with pytest.raises(ValidationError):
        Event(**data)



VALID_LINE = {
    "account": Account.CASH,
    "debit": Decimal("200.00"),
    "credit": Decimal("0.00"),
}


def test_line_accepts_valid_debit():
    line = Line(**VALID_LINE)

    assert line.account == Account.CASH
    assert line.debit == Decimal("200.00")
    assert line.credit == Decimal("0.00")


def test_line_accepts_valid_credit():
    data = VALID_LINE.copy()
    data["debit"] = Decimal("0.00")
    data["credit"] = Decimal("200.00")

    line = Line(**data)

    assert line.debit == Decimal("0.00")
    assert line.credit == Decimal("200.00")


def test_line_rejects_both_sides_positive():
    data = VALID_LINE.copy()
    data["credit"] = Decimal("200.00")

    with pytest.raises(ValidationError):
        Line(**data)


def test_line_rejects_both_sides_zero():
    data = VALID_LINE.copy()
    data["debit"] = Decimal("0.00")

    with pytest.raises(ValidationError):
        Line(**data)


def test_line_rejects_negative_debit():
    data = VALID_LINE.copy()
    data["debit"] = Decimal("-10.00")

    with pytest.raises(ValidationError):
        Line(**data)


def test_line_rejects_negative_credit():
    data = VALID_LINE.copy()
    data["debit"] = Decimal("0.00")
    data["credit"] = Decimal("-10.00")

    with pytest.raises(ValidationError):
        Line(**data)


def test_line_rejects_unknown_account():
    data = VALID_LINE.copy()
    data["account"] = "9999"

    with pytest.raises(ValidationError):
        Line(**data)




def test_journal_entry_accepts_balanced_entry():
    entry = JournalEntry(
        event_id="EVT-001",
        lines=[
            Line(
                account=Account.CASH,
                debit=Decimal("200.00"),
                credit=Decimal("0.00"),
            ),
            Line(
                account=Account.REVENUE,
                debit=Decimal("0.00"),
                credit=Decimal("200.00"),
            ),
        ],
    )

    assert entry.event_id == "EVT-001"
    assert len(entry.lines) == 2
    assert isinstance(entry.lines, tuple)


def test_journal_entry_rejects_unbalanced_entry():
    with pytest.raises(ValidationError):
        JournalEntry(
            event_id="EVT-002",
            lines=[
                Line(
                    account=Account.CASH,
                    debit=Decimal("200.00"),
                    credit=Decimal("0.00"),
                ),
                Line(
                    account=Account.REVENUE,
                    debit=Decimal("0.00"),
                    credit=Decimal("150.00"),
                ),
            ],
        )


def test_journal_entry_rejects_single_line():
    with pytest.raises(ValidationError):
        JournalEntry(
            event_id="EVT-003",
            lines=[
                Line(
                    account=Account.CASH,
                    debit=Decimal("200.00"),
                    credit=Decimal("0.00"),
                ),
            ],
        )

def test_metrics_snapshot_accepts_valid_data():
    snapshot = MetricsSnapshot(
        as_of=datetime(2026, 11, 18, 12, 0, tzinfo=UTC),
        cash=Decimal("10000.00"),
        net_burn_30d=Decimal("2000.00"),
        runway_months=Decimal("5.00"),
        confidence=Confidence.HIGH,
        stage=Stage.EARLY_REVENUE,
        data_days=30,
    )

    assert snapshot.cash == Decimal("10000.00")
    assert snapshot.confidence == Confidence.HIGH
    assert snapshot.stage == Stage.EARLY_REVENUE


def test_metrics_snapshot_rejects_negative_data_days():
    with pytest.raises(ValidationError):
        MetricsSnapshot(
            as_of=datetime(2026, 11, 18, 12, 0, tzinfo=UTC),
            cash=Decimal("10000.00"),
            net_burn_30d=Decimal("2000.00"),
            confidence=Confidence.HIGH,
            stage=Stage.EARLY_REVENUE,
            data_days=-1,
        )


def test_metrics_snapshot_rejects_naive_timestamp():
    with pytest.raises(ValidationError):
        MetricsSnapshot(
            as_of=datetime(2026, 11, 18, 12, 0),
            cash=Decimal("10000.00"),
            net_burn_30d=Decimal("2000.00"),
            confidence=Confidence.HIGH,
            stage=Stage.EARLY_REVENUE,
            data_days=30,
        )


def test_metrics_snapshot_rejects_invalid_confidence():
    with pytest.raises(ValidationError):
        MetricsSnapshot(
            as_of=datetime(2026, 11, 18, 12, 0, tzinfo=UTC),
            cash=Decimal("10000.00"),
            net_burn_30d=Decimal("2000.00"),
            confidence="MEDIUM",
            stage=Stage.EARLY_REVENUE,
            data_days=30,
        )


def test_metrics_snapshot_rejects_invalid_stage():
    with pytest.raises(ValidationError):
        MetricsSnapshot(
            as_of=datetime(2026, 11, 18, 12, 0, tzinfo=UTC),
            cash=Decimal("10000.00"),
            net_burn_30d=Decimal("2000.00"),
            confidence=Confidence.HIGH,
            stage="MATURE",
            data_days=30,
        )


def test_metrics_snapshot_allows_undefined_runway():
    snapshot = MetricsSnapshot(
        as_of=datetime(2026, 11, 18, 12, 0, tzinfo=UTC),
        cash=Decimal("10000.00"),
        net_burn_30d=Decimal("0.00"),
        confidence=Confidence.HIGH,
        stage=Stage.PRE_REVENUE,
        data_days=30,
    )

    assert snapshot.runway_months is None