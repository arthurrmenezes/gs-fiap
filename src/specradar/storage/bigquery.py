"""BigQuery read/write client + an in-memory writer for offline runs and tests.

Both implement the StorageWriter Protocol so the pipeline is storage-agnostic.
"""

from __future__ import annotations

from typing import Any, Protocol

from specradar.logging import get_logger
from specradar.models import ReconciledSpec
from specradar.storage.schema import (
    DIM_ATTRIBUTE_SCHEMA,
    DIM_SOURCE_SCHEMA,
    DIM_VEHICLE_SCHEMA,
    FACT_SPEC_SCHEMA,
    fact_spec_rows,
)
from specradar.storage.views import spec_diff_view_sql, spec_sheet_view_sql

log = get_logger("storage")


class StorageWriter(Protocol):
    def write_specs(self, specs: list[ReconciledSpec]) -> int: ...


class InMemoryWriter:
    """Collects fact rows in memory. Used by offline pipeline runs and the golden test."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def write_specs(self, specs: list[ReconciledSpec]) -> int:
        rows = fact_spec_rows(specs)
        self.rows.extend(rows)
        log.info("wrote_specs_memory", count=len(rows))
        return len(rows)


class BigQueryWriter:
    """Writes to the curated medallion layer in BigQuery."""

    def __init__(self, project: str, dataset: str = "specradar") -> None:
        if not project:
            raise ValueError("GOOGLE_CLOUD_PROJECT is required for BigQueryWriter")
        from google.cloud import bigquery  # lazy import

        self._bq = bigquery
        self._client = bigquery.Client(project=project)
        self._project = project
        self._dataset = dataset

    def _table_id(self, table: str) -> str:
        return f"{self._project}.{self._dataset}.{table}"

    def _schema(self, triples: list[tuple[str, str, str]]) -> list[Any]:
        return [self._bq.SchemaField(n, t, mode=m) for (n, t, m) in triples]

    def ensure_tables(self) -> None:
        """Create curated tables if missing; partition + cluster fact_spec."""
        self._client.create_dataset(self._dataset, exists_ok=True)
        specs = {
            "dim_vehicle": DIM_VEHICLE_SCHEMA,
            "dim_attribute": DIM_ATTRIBUTE_SCHEMA,
            "dim_source": DIM_SOURCE_SCHEMA,
            "fact_spec": FACT_SPEC_SCHEMA,
        }
        for name, triples in specs.items():
            table = self._bq.Table(self._table_id(name), schema=self._schema(triples))
            if name == "fact_spec":
                table.time_partitioning = self._bq.TimePartitioning(field="reconciled_at")
                table.clustering_fields = ["vehicle_id"]
            self._client.create_table(table, exists_ok=True)

    def create_views(self) -> None:
        """(Re)create the pivoted spec-sheet and spec-diff views."""
        for sql in (
            spec_sheet_view_sql(self._project, self._dataset),
            spec_diff_view_sql(self._project, self._dataset),
        ):
            self._client.query(sql).result()

    def write_specs(self, specs: list[ReconciledSpec]) -> int:
        rows = fact_spec_rows(specs)
        if not rows:
            return 0
        errors = self._client.insert_rows_json(self._table_id("fact_spec"), rows)
        if errors:
            raise RuntimeError(f"BigQuery insert errors: {errors}")
        log.info("wrote_specs_bq", count=len(rows))
        return len(rows)
