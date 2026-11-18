from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator

from founderlens.config import load_decisions


def _normalize_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must include a timezone")
    return value.astimezone(UTC)


UTCDateTime = Annotated[datetime, AfterValidator(_normalize_utc)]




def _to_decimal(value):
    """Convert floats to Decimal without inheriting binary approximation."""
    if isinstance(value, float):
        return Decimal(str(value))
    return value


def _validate_money(value: Decimal) -> Decimal:
    """Validate finiteness and allowed fractional digits."""

    if not value.is_finite():
        raise ValueError("money must be finite")

    decisions = load_decisions()
    decimal_places = decisions.money.decimal_places

    fractional_digits = max(0, -value.as_tuple().exponent)

    if fractional_digits > decimal_places:
        raise ValueError(
            f"money cannot have more than {decimal_places} decimal places"
        )

    return value


Money = Annotated[
    Decimal,
    BeforeValidator(_to_decimal),
    AfterValidator(_validate_money),
]