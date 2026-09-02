"""Per-category sanity checks. Catches the planted R$ 499 price (CLAUDE.md §9).

A value that passes extraction + verification can still be wrong (e.g. a price of
R$ 499 for a mid-size pickup). Sanity bounds from the taxonomy flag these as
ANOMALY rather than letting them silently become a business decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from specradar.taxonomy.models import AttributeDef, DataType


@dataclass(frozen=True)
class AnomalyResult:
    is_anomaly: bool
    reason: str | None = None


def _numeric_for_check(attr: AttributeDef, value_norm: Any) -> float | None:
    """Extract the number the sanity bounds apply to, given the data type."""
    if attr.data_type is DataType.SCALAR_UNIT and isinstance(value_norm, int | float):
        return float(value_norm)
    # For tires the bounds are declared against rim diameter (inches).
    if attr.data_type is DataType.DIMENSIONAL and isinstance(value_norm, dict):
        rim = value_norm.get("rim_diameter_in")
        if isinstance(rim, int | float):
            return float(rim)
    return None


def check_anomaly(attr: AttributeDef, value_norm: Any) -> AnomalyResult:
    """Return whether a normalized value is out of its sane category range."""
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
