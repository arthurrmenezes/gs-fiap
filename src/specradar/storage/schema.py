"""BigQuery table schemas (medallion) + row serialization for fact_spec.

Long format: one row per (vehicle × attribute × source). A new attribute does not
change the physical schema (CLAUDE.md §6). Schemas are expressed as plain dicts
so this module imports cleanly without google-cloud-bigquery installed; the
client converts them to SchemaField objects.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from specradar.models import ReconciledSpec

# field := (name, type, mode)
SchemaTriple = tuple[str, str, str]

DIM_VEHICLE_SCHEMA: list[SchemaTriple] = [
    ("vehicle_id", "STRING", "REQUIRED"),
    ("make", "STRING", "REQUIRED"),
    ("model", "STRING", "REQUIRED"),
    ("version", "STRING", "REQUIRED"),
    ("model_year", "INTEGER", "NULLABLE"),
    ("market", "STRING", "REQUIRED"),
]

DIM_ATTRIBUTE_SCHEMA: list[SchemaTriple] = [
    ("attribute_id", "STRING", "REQUIRED"),
    ("name", "STRING", "REQUIRED"),
    ("group", "STRING", "REQUIRED"),
    ("data_type", "STRING", "REQUIRED"),
    ("canonical_unit", "STRING", "NULLABLE"),
    ("value_set", "STRING", "REPEATED"),
]

DIM_SOURCE_SCHEMA: list[SchemaTriple] = [
    ("source_id", "STRING", "REQUIRED"),
    ("domain", "STRING", "REQUIRED"),
    ("authority_tier", "INTEGER", "REQUIRED"),
    ("kind", "STRING", "REQUIRED"),
]

FACT_SPEC_SCHEMA: list[SchemaTriple] = [
    ("vehicle_id", "STRING", "REQUIRED"),
    ("attribute_id", "STRING", "REQUIRED"),
    ("value_raw", "STRING", "NULLABLE"),
    ("value_norm", "STRING", "NULLABLE"),  # JSON-encoded (number/str/list/dict)
    ("unit", "STRING", "NULLABLE"),
    ("source_url", "STRING", "NULLABLE"),
    ("source_tier", "INTEGER", "NULLABLE"),
    ("confidence", "FLOAT", "NULLABLE"),
    ("status", "STRING", "REQUIRED"),
    ("evidence_snippet", "STRING", "NULLABLE"),
    ("note", "STRING", "NULLABLE"),
    ("reconciled_at", "TIMESTAMP", "REQUIRED"),
]


def vehicle_id(make: str, model: str, version: str, model_year: int | None) -> str:
    """Stable surrogate id for a vehicle version."""
    key = f"{make}|{model}|{version}|{model_year or ''}".lower()
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def _json_norm(value_norm: Any) -> str | None:
    if value_norm is None:
        return None
    return json.dumps(value_norm, ensure_ascii=False, sort_keys=True)


def fact_spec_rows(specs: list[ReconciledSpec]) -> list[dict[str, Any]]:
    """Serialize reconciled specs into BigQuery-ready fact_spec rows (long format)."""
    rows: list[dict[str, Any]] = []
    for spec in specs:
        vk = spec.vehicle_key
        rows.append(
            {
                "vehicle_id": vehicle_id(vk.make, vk.model, vk.version, vk.model_year),
                "attribute_id": spec.attribute_id,
                "value_raw": spec.value_raw,
                "value_norm": _json_norm(spec.value_norm),
                "unit": spec.unit,
                "source_url": spec.source_url,
                "source_tier": spec.source_tier,
                "confidence": spec.confidence,
                "status": spec.status.value,
                "evidence_snippet": spec.evidence_snippet,
                "note": spec.note,
                "reconciled_at": spec.reconciled_at.isoformat(),
            }
        )
    return rows
