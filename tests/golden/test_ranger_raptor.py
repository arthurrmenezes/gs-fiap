"""Golden acceptance test — Ford Ranger Raptor. Merge gate (CLAUDE.md §8, §12).

Runs the pipeline (stages [3]–[5]) fully offline against the bundled fixture and
compares the result, field by field, to `ranger_raptor_truth.yaml`. Validates:
the 5 hard data types, identical output format, price flagged ANOMALY, absent
field as explicit NA, and the hallucinated torque discarded by the verifier.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from specradar.models import ReconciledSpec, SpecStatus, VehicleKey
from specradar.pipeline.fixtures import FixtureLLMClient, load_fixture
from specradar.pipeline.orchestrate import run_extraction_pipeline
from specradar.taxonomy.loader import Taxonomy

pytestmark = pytest.mark.golden

TRUTH_PATH = Path(__file__).resolve().parent / "ranger_raptor_truth.yaml"


@pytest.fixture(scope="module")
def truth() -> dict[str, Any]:
    return yaml.safe_load(TRUTH_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def specs_by_id(
    taxonomy: Taxonomy, raptor_fixture_dir: Path, truth: dict[str, Any]
) -> dict[str, ReconciledSpec]:
    v = truth["vehicle"]
    vehicle = VehicleKey(
        make=v["make"], model=v["model"], version=v["version"], model_year=v["year"]
    )
    documents, responses = load_fixture(raptor_fixture_dir)
    specs = run_extraction_pipeline(
        vehicle, documents, FixtureLLMClient(responses), taxonomy=taxonomy
    )
    return {s.attribute_id: s for s in specs}


def _assert_value_equals(expected: Any, actual: Any) -> None:
    if isinstance(expected, float):
        assert actual == pytest.approx(expected), f"{actual!r} != {expected!r}"
    elif isinstance(expected, dict):
        assert isinstance(actual, dict)
        for k, v in expected.items():
            _assert_value_equals(v, actual.get(k))
    else:
        assert actual == expected, f"{actual!r} != {expected!r}"


def test_output_format_is_complete_and_stable(
    taxonomy: Taxonomy, specs_by_id: dict[str, ReconciledSpec]
) -> None:
    """The sheet covers EVERY taxonomy attribute — same format for any vehicle."""
    assert set(specs_by_id) == {a.id for a in taxonomy.all_attributes()}


@pytest.mark.parametrize(
    "attribute_id", yaml.safe_load(TRUTH_PATH.read_text(encoding="utf-8"))["expected"].keys()
)
def test_attribute_matches_truth(
    attribute_id: str, truth: dict[str, Any], specs_by_id: dict[str, ReconciledSpec]
) -> None:
    expected = truth["expected"][attribute_id]
    spec = specs_by_id[attribute_id]

    assert spec.status is SpecStatus(expected["status"]), (
        f"{attribute_id}: status {spec.status} != {expected['status']}"
    )
    _assert_value_equals(expected["value"], spec.value_norm)
    if "unit" in expected:
        assert spec.unit == expected["unit"]


def test_price_anomaly_is_flagged(specs_by_id: dict[str, ReconciledSpec]) -> None:
    """The planted R$ 499 must be auto-flagged, never silently accepted."""
    assert specs_by_id["price.brl"].status is SpecStatus.ANOMALY


def test_absent_attribute_is_explicit_na(specs_by_id: dict[str, ReconciledSpec]) -> None:
    spec = specs_by_id["emissions.co2_gkm"]
    assert spec.status is SpecStatus.NA
    assert spec.value_norm is None


def test_hallucinated_torque_discarded(specs_by_id: dict[str, ReconciledSpec]) -> None:
    """iCarros' 600 Nm (no real evidence) is dropped; Ford's verified 583 wins."""
    assert specs_by_id["engine.torque_nm"].value_norm == pytest.approx(583.0)
