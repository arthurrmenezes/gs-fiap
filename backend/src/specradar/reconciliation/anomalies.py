from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from specradar.taxonomy.models import AttributeDef, DataType


@dataclass(frozen=True)
class AnomalyResult:
    is_anomaly: bool
    reason: str | None = None


def _numeric_for_check(attr: AttributeDef, value_norm: Any) -> float | None:
    if attr.data_type is DataType.SCALAR_UNIT and isinstance(value_norm, int | float):
        return float(value_norm)
    if attr.data_type is DataType.DIMENSIONAL and isinstance(value_norm, dict):
        rim = value_norm.get("rim_diameter_in")
        if isinstance(rim, int | float):
            return float(rim)
    return None


def check_anomaly(attr: AttributeDef, value_norm: Any) -> AnomalyResult:
    if attr.sanity is None:
        return AnomalyResult(False)
    number = _numeric_for_check(attr, value_norm)
    if number is None:
        return AnomalyResult(False)
    lo, hi = attr.sanity.min, attr.sanity.max
    if number < lo or number > hi:
        return AnomalyResult(
            True,
            f"{attr.id}={number:g} outside sane range [{lo:g}, {hi:g}]",
        )
    return AnomalyResult(False)
