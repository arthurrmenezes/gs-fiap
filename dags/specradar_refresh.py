"""Airflow DAG: weekly refresh of the monitored portfolio (roadmap, CLAUDE.md §13).

Re-extracts the monitored vehicles, diffs against the previous curated version,
and alerts when a competitor changes a spec or price. The diff/alert logic is on
the roadmap (out of MVP) — this DAG is the scaffold that turns a point-in-time
query into continuous monitoring. It is intentionally minimal.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from airflow.decorators import dag, task

# Portfolio to monitor weekly. In production this comes from a config table.
MONITORED: list[dict[str, Any]] = [
    {"make": "Ford", "model": "Ranger Raptor", "version": "Raptor 3.0 V6", "year": 2026},
    {"make": "Toyota", "model": "Hilux", "version": "GR-Sport", "year": 2026},
    {"make": "Chevrolet", "model": "S10", "version": "High Country", "year": 2026},
]

DEFAULT_ARGS = {"owner": "specradar", "retries": 1, "retry_delay": timedelta(minutes=5)}


@dag(
    dag_id="specradar_refresh",
    schedule="@weekly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["specradar", "refresh", "roadmap"],
)
def specradar_refresh() -> None:
    @task
    def list_portfolio() -> list[dict[str, Any]]:
        return MONITORED

    @task
    def refresh_vehicle(vehicle: dict[str, Any]) -> dict[str, Any]:
        """Re-extract one vehicle and (roadmap) diff vs the previous curated row."""
        # Reuses the on-demand pipeline; diff + alerting is the roadmap extension.
        return {"vehicle": vehicle, "status": "refresh_stub"}

    refresh_vehicle.expand(vehicle=list_portfolio())


specradar_refresh()
