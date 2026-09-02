"""Ingest the Ford internal equipment data sheet as a tier-1 Ford baseline.

The provided workbook (`FIAP-Ford - Data sheet_Desafio_01_v02.xlsx`, sheet BASE)
is the official Ford Ranger equipment matrix: one column per version (XLT,
Limited, Limited+) and one row per equipment/spec. It is exactly the Ford
baseline the spec-diff dashboard compares competitors against (CLAUDE.md §13,
glossary "spec diff").

This is a STRUCTURED first-party source, so it bypasses LLM extraction: the
values are read directly and run through the same deterministic normalization +
reconciliation as web-extracted data, then persisted with full provenance
(tier 1, status OK). It is NOT a web scrape — confidence is high by construction.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from specradar.config import REPO_ROOT
from specradar.logging import get_logger
from specradar.models import NormalizedValue, ReconciledSpec, VehicleKey
from specradar.normalization.units import to_canonical
from specradar.reconciliation.coalesce import reconcile_attribute
from specradar.taxonomy.loader import Taxonomy, get_taxonomy
from specradar.textutil import fold

log = get_logger("ingest.ford")

DEFAULT_SHEET = "BASE"
DEFAULT_WORKBOOK = REPO_ROOT / "FIAP-Ford - Data sheet_Desafio_01_v02.xlsx"
SOURCE_URL = "internal://ford/data-sheet/ranger-26my"
SOURCE_TIER = 1  # official OEM
MODEL_YEAR = 2026  # "26MY"

# A cell value meaning "equipped" for boolean-style rows.
_TRUE = "x"


def _scalar(unit: str | None = None) -> Callable[[Any], Any]:
    """Numeric cell → float in canonical unit (the sheet already uses canon units)."""

    def fn(cell: Any) -> float | None:
        if cell is None or cell == 0 or str(cell).strip() == "":
            return None
        try:
            value = float(str(cell).replace(",", "."))
        except ValueError:
            return None
        return to_canonical(value, unit, unit) if unit else value

    return fn


def _const_if_true(value: str) -> Callable[[Any], Any]:
    """Boolean 'X' cell → a fixed canonical value, else None."""

    def fn(cell: Any) -> str | None:
        return value if fold(cell or "") == _TRUE else None

    return fn


# Folded row label → (attribute_id, cell→value_norm). Only rows that map to the
# canonical taxonomy are ingested; the sheet's many marketing booleans are skipped.
ROW_MAP: dict[str, tuple[str, Callable[[Any], Any]]] = {
    "potencia": ("engine.power_cv", _scalar("cv")),
    "torque": ("engine.torque_nm", _scalar("Nm")),
    "cilindrada": ("engine.displacement_l", _scalar("L")),
    "quantidade de marchas": ("transmission.gears", _scalar("gears")),
    "economia de combustivel": ("fuel.consumption_city_kml", _scalar("km/L")),
    "polegadas": ("wheels.rim_diameter_in", _scalar("in")),
    "airbag (cada)": ("safety.airbags", _scalar("airbags")),
    "anos de garantia": ("warranty.years", _scalar("years")),
    "peso em ordem de marchas": ("capacity.curb_weight_kg", _scalar("kg")),
    "motor diesel": ("engine.fuel", _const_if_true("Diesel")),
    "tracao integral (awd)": ("drivetrain", _const_if_true("AWD")),
    "farois full led": ("headlights", _const_if_true("Full LED")),
}


def _read_sheet(workbook: Path, sheet: str) -> tuple[list[str], list[tuple[str, list[Any]]]]:
    import openpyxl  # lazy — only needed for this ingestion path

    wb = openpyxl.load_workbook(workbook, read_only=True, data_only=True)
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    versions = [str(c).strip() for c in header[1:] if c is not None]
    data: list[tuple[str, list[Any]]] = []
    for r in rows[1:]:
        label = r[0]
        if label is None:
            continue
        cells = list(r[1 : 1 + len(versions)])
        data.append((str(label), cells))
    return versions, data


def ingest_ford_datasheet(
    workbook: Path | None = None,
    *,
    sheet: str = DEFAULT_SHEET,
    taxonomy: Taxonomy | None = None,
    now: datetime | None = None,
) -> dict[str, list[ReconciledSpec]]:
    """Read the Ford data sheet into reconciled specs, keyed by version slug.

    Each version becomes its own vehicle; values run through normalization +
    reconciliation so the Ford baseline lands in `fact_spec` like any other source.
    """
    workbook = workbook or DEFAULT_WORKBOOK
    taxonomy = taxonomy or get_taxonomy()
    now = now or datetime.now(UTC)

    versions, data = _read_sheet(workbook, sheet)
    # version label → {attribute_id: NormalizedValue}
    per_version: dict[str, dict[str, NormalizedValue]] = {v: {} for v in versions}

    for label, cells in data:
        mapping = ROW_MAP.get(fold(label))
        if mapping is None:
            continue
        attribute_id, transform = mapping
        attr = taxonomy.get(attribute_id)
        for version, cell in zip(versions, cells, strict=False):
            value_norm = transform(cell)
            if value_norm is None:
                continue
            per_version[version][attribute_id] = NormalizedValue(
                attribute_id=attribute_id,
                value_raw=str(cell),
                value_norm=value_norm,
                unit=attr.canonical_unit,
                confidence=1.0,
                evidence_snippet=f"{label}: {cell}",
                evidence_verified=True,
                source_url=SOURCE_URL,
                source_tier=SOURCE_TIER,
                extracted_at=now,
            )

    out: dict[str, list[ReconciledSpec]] = {}
    for version, attr_values in per_version.items():
        vehicle = VehicleKey(make="Ford", model="Ranger", version=version, model_year=MODEL_YEAR)
        specs = [
            reconcile_attribute(vehicle, taxonomy.get(aid), [nv], now=now)
            for aid, nv in attr_values.items()
        ]
        out[vehicle.slug()] = specs
        log.info("ingested_version", version=version, attributes=len(specs))
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse

    from specradar.logging import configure_logging

    parser = argparse.ArgumentParser(description="Ingest the Ford data sheet Excel.")
    parser.add_argument("--workbook", default=str(DEFAULT_WORKBOOK))
    parser.add_argument("--sheet", default=DEFAULT_SHEET)
    args = parser.parse_args(argv)

    configure_logging("INFO")
    result = ingest_ford_datasheet(Path(args.workbook), sheet=args.sheet)
    for slug, specs in result.items():
        print(f"\n{slug}")
        for spec in specs:
            print(f"  {spec.attribute_id:28} {spec.value_norm!s:24} [{spec.status.value}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
