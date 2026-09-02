"""Coalesce by authority into a single ReconciledSpec, with explicit status.

Decision order for an attribute with one or more candidate values:
  1. no candidates           → NA (value null).
  2. comparable disagreement → CONFLICT (winner + alternatives preserved).
  3. anomaly                 → ANOMALY.
  4. low confidence          → LOW_CONFIDENCE.
  5. otherwise               → OK.

The winner is the highest-authority value (lowest tier; ties broken by highest
confidence). "Comparable" disagreement means two values of the SAME tier differ
beyond tolerance — lower-authority disagreement is simply overridden by coalesce.
"""

from __future__ import annotations

from datetime import UTC, datetime

from specradar.logging import get_logger
from specradar.models import NormalizedValue, ReconciledSpec, SpecStatus, VehicleKey
from specradar.reconciliation.anomalies import check_anomaly
from specradar.reconciliation.conflicts import values_equal
from specradar.taxonomy.models import AttributeDef

log = get_logger("reconciliation")

# Confidence below this is reported as LOW_CONFIDENCE.
_LOW_CONFIDENCE_THRESHOLD = 0.5


def _na(vehicle: VehicleKey, attr: AttributeDef, now: datetime) -> ReconciledSpec:
    return ReconciledSpec(
        vehicle_key=vehicle,
        attribute_id=attr.id,
        value_raw=None,
        value_norm=None,
        unit=None,
        status=SpecStatus.NA,
        confidence=0.0,
        source_url=None,
        source_tier=None,
        evidence_snippet=None,
        reconciled_at=now,
    )


def reconcile_attribute(
    vehicle: VehicleKey,
    attr: AttributeDef,
    candidates: list[NormalizedValue],
    *,
    now: datetime | None = None,
) -> ReconciledSpec:
    """Reduce all candidate values for one attribute to a single reconciled spec."""
    now = now or datetime.now(UTC)

    if not candidates:
        return _na(vehicle, attr, now)

    # Highest authority first; break ties by confidence.
    ordered = sorted(candidates, key=lambda v: (v.source_tier, -v.confidence))
    winner = ordered[0]

    # Comparable disagreement: same tier as winner, value differs beyond tolerance.
    comparable = [v for v in ordered if v.source_tier == winner.source_tier]
    conflicting = [v for v in comparable if not values_equal(attr, v.value_norm, winner.value_norm)]

    status = SpecStatus.OK
    note: str | None = None
    alternatives: list[NormalizedValue] = []

    if conflicting:
        status = SpecStatus.CONFLICT
        alternatives = conflicting
        note = "sources of comparable authority disagree"
        log.warning(
            "conflict",
            vehicle_key=vehicle.slug(),
            attribute_id=attr.id,
            winner=str(winner.value_norm),
            others=[str(v.value_norm) for v in conflicting],
        )
    else:
        anomaly = check_anomaly(attr, winner.value_norm)
        if anomaly.is_anomaly:
            status = SpecStatus.ANOMALY
            note = anomaly.reason
            log.warning(
                "anomaly",
                vehicle_key=vehicle.slug(),
                attribute_id=attr.id,
                value=str(winner.value_norm),
                reason=anomaly.reason,
            )
        elif winner.confidence < _LOW_CONFIDENCE_THRESHOLD:
            status = SpecStatus.LOW_CONFIDENCE
            note = f"confidence {winner.confidence:.2f} below threshold"

    return ReconciledSpec(
        vehicle_key=vehicle,
        attribute_id=attr.id,
        value_raw=winner.value_raw,
        value_norm=winner.value_norm,
        unit=winner.unit,
        status=status,
        confidence=winner.confidence,
        source_url=winner.source_url,
        source_tier=winner.source_tier,
        evidence_snippet=winner.evidence_snippet,
        reconciled_at=now,
        alternatives=alternatives,
        note=note,
    )
