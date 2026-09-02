"""Ingestion of the provided Ford data sheet Excel into reconciled specs."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("openpyxl")

from specradar.ingest.ford_datasheet import DEFAULT_WORKBOOK, ingest_ford_datasheet
from specradar.models import SpecStatus
from specradar.taxonomy.loader import Taxonomy


@pytest.mark.skipif(not Path(DEFAULT_WORKBOOK).exists(), reason="Ford data sheet not present")
def test_ingest_ford_datasheet(taxonomy: Taxonomy) -> None:
    result = ingest_ford_datasheet(taxonomy=taxonomy)
    # Three versions in the BASE sheet: XLT, Limited, Limited+.
    assert len(result) == 3

    # Pick any version and check the known Ranger diesel numbers normalize.
    specs = next(iter(result.values()))
    by_id = {s.attribute_id: s for s in specs}
    assert by_id["engine.power_cv"].value_norm == pytest.approx(250.0)
    assert by_id["engine.torque_nm"].value_norm == pytest.approx(600.0)
    assert by_id["engine.fuel"].value_norm == "Diesel"
    assert by_id["drivetrain"].value_norm == "AWD"
    assert all(s.status is SpecStatus.OK for s in specs)
    assert all(s.source_tier == 1 for s in specs)
