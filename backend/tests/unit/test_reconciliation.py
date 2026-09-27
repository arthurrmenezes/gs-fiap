from __future__ import annotations

from datetime import UTC, datetime

from specradar.models import NormalizedValue, SpecStatus, VehicleKey
from specradar.reconciliation.anomalies import check_anomaly
from specradar.reconciliation.coalesce import reconcile_attribute
from specradar.taxonomy.loader import Taxonomy

NOW = datetime(2026, 1, 1, tzinfo=UTC)
VEHICLE = VehicleKey(make="Ford", model="Ranger Raptor", version="Raptor 3.0 V6", model_year=2026)


def _nv(
    attr_id: str, value: object, tier: int, *, conf: float = 0.9, unit: str | None = None
) -> NormalizedValue:
    return NormalizedValue(
        attribute_id=attr_id,
        value_raw=str(value),
        value_norm=value,
        unit=unit,
        confidence=conf,
        evidence_snippet="evidence",
        evidence_verified=True,
        source_url=f"https://tier{tier}.example/x",
        source_tier=tier,
        extracted_at=NOW,
    )


def test_no_candidates_is_na(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("emissions.co2_gkm")
    spec = reconcile_attribute(VEHICLE, attr, [], now=NOW)
    assert spec.status is SpecStatus.NA
    assert spec.value_norm is None


def test_coalesce_prefers_higher_authority(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("engine.power_cv")
    cands = [
        _nv("engine.power_cv", 390.0, tier=3, unit="cv"),
        _nv("engine.power_cv", 397.0, tier=1, unit="cv"),
    ]
    spec = reconcile_attribute(VEHICLE, attr, cands, now=NOW)
    assert spec.status is SpecStatus.OK
    assert spec.value_norm == 397.0
    assert spec.source_tier == 1


def test_comparable_disagreement_is_conflict(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("engine.power_cv")
    cands = [
        _nv("engine.power_cv", 397.0, tier=1, unit="cv"),
        _nv("engine.power_cv", 420.0, tier=1, unit="cv"),
    ]
    spec = reconcile_attribute(VEHICLE, attr, cands, now=NOW)
    assert spec.status is SpecStatus.CONFLICT
    assert len(spec.alternatives) == 1


def test_within_tolerance_is_not_conflict(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("engine.power_cv")
    cands = [
        _nv("engine.power_cv", 397.0, tier=1, unit="cv"),
        _nv("engine.power_cv", 398.0, tier=1, unit="cv"),
    ]
    spec = reconcile_attribute(VEHICLE, attr, cands, now=NOW)
    assert spec.status is SpecStatus.OK


def test_price_499_is_anomaly(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("price.brl")
    spec = reconcile_attribute(
        VEHICLE, attr, [_nv("price.brl", 499.0, tier=3, unit="BRL")], now=NOW
    )
    assert spec.status is SpecStatus.ANOMALY


def test_low_confidence_flagged(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("engine.power_cv")
    spec = reconcile_attribute(
        VEHICLE, attr, [_nv("engine.power_cv", 397.0, tier=2, conf=0.3, unit="cv")], now=NOW
    )
    assert spec.status is SpecStatus.LOW_CONFIDENCE


def test_check_anomaly_in_range(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("price.brl")
    assert check_anomaly(attr, 350000.0).is_anomaly is False
    assert check_anomaly(attr, 499.0).is_anomaly is True
