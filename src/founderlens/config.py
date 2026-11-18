"""Load and validate FounderLens YAML configuration."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class MoneyConfig(StrictModel):
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    decimal_places: int = Field(ge=0, le=6)
    rounding: Literal["ROUND_HALF_EVEN", "ROUND_HALF_UP", "ROUND_DOWN", "ROUND_UP"]


class BurnConfig(StrictModel):
    window_days: int = Field(gt=0)
    low_confidence_below_days: int = Field(ge=0)


class RunwayConfig(StrictModel):
    undefined_when_net_burn_lte: float


class ChurnConfig(StrictModel):
    undefined_when_start_customers: int = Field(ge=0)


class RevenueConfig(StrictModel):
    recognition: Literal["monthly_billing_no_deferral"]


class DecisionsConfig(StrictModel):
    schema_version: Literal[1]
    money: MoneyConfig
    burn: BurnConfig
    runway: RunwayConfig
    churn: ChurnConfig
    revenue: RevenueConfig

    @model_validator(mode="after")
    def confidence_window_fits(self) -> DecisionsConfig:
        if self.burn.low_confidence_below_days > self.burn.window_days:
            raise ValueError("low_confidence_below_days cannot exceed window_days")
        return self


class MonthlyRevenueThresholds(StrictModel):
    pre_revenue_max: float = Field(ge=0)
    early_revenue_max: float = Field(gt=0)
    growing_max: float = Field(gt=0)

    @model_validator(mode="after")
    def cutoffs_increase(self) -> MonthlyRevenueThresholds:
        if not self.pre_revenue_max < self.early_revenue_max < self.growing_max:
            raise ValueError("monthly revenue thresholds must increase")
        return self


class ThresholdsConfig(StrictModel):
    schema_version: Literal[1]
    monthly_revenue: MonthlyRevenueThresholds


def _config_dir() -> Path:
    override = os.environ.get("FOUNDERLENS_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    return Path(__file__).resolve().parents[2] / "config"


def _load_yaml(filename: str) -> object:
    path = _config_dir() / filename
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


@lru_cache(maxsize=1)
def load_decisions() -> DecisionsConfig:
    """Load the decision configuration, caching the validated result."""
    return DecisionsConfig.model_validate(_load_yaml("decisions.yaml"))


@lru_cache(maxsize=1)
def load_thresholds() -> ThresholdsConfig:
    """Load the tunable thresholds, caching the validated result."""
    return ThresholdsConfig.model_validate(_load_yaml("thresholds.yaml"))
