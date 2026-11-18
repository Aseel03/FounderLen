from __future__ import annotations

import pytest

from founderlens.config import DecisionsConfig, ThresholdsConfig, load_decisions, load_thresholds


def test_default_configuration_loads() -> None:
    decisions = load_decisions()
    thresholds = load_thresholds()
    assert decisions.money.decimal_places == 2
    assert decisions.burn.window_days == 30
    assert thresholds.monthly_revenue.growing_max > thresholds.monthly_revenue.early_revenue_max


def test_decisions_reject_unknown_keys() -> None:
    data = {
        "schema_version": 1,
        "money": {
            "currency": "USD",
            "decimal_places": 2,
            "rounding": "ROUND_HALF_EVEN",
            "typo": True,
        },
        "burn": {"window_days": 30, "low_confidence_below_days": 14},
        "runway": {"undefined_when_net_burn_lte": 0},
        "churn": {"undefined_when_start_customers": 0},
        "revenue": {"recognition": "monthly_billing_no_deferral"},
    }
    with pytest.raises(ValueError):
        DecisionsConfig.model_validate(data)


def test_thresholds_reject_unknown_keys() -> None:
    data = {"schema_version": 1, "unexpected": 2, "monthly_revenue": {
        "pre_revenue_max": 0, "early_revenue_max": 1, "growing_max": 2,
    }}
    with pytest.raises(ValueError):
        ThresholdsConfig.model_validate(data)
