"""Airflow DAG: on-demand SpecRadar run for a single vehicle query.

Triggered with a config payload, e.g.:
    {"make": "Ford", "model": "Ranger Raptor", "version": "Raptor 3.0 V6", "year": 2026}

Mirrors the pipeline stages as tasks for observability. Heavy imports live inside
task callables so DAG parsing stays cheap.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from airflow.decorators import dag, task

DEFAULT_ARGS = {
    "owner": "specradar",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="specradar_on_demand",
    schedule=None,  # triggered manually / via API
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["specradar", "on-demand"],
)
def specradar_on_demand() -> None:
    @task
    def resolve_and_fetch(params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        from specradar.config import get_settings
        from specradar.models import VehicleKey
        from specradar.pipeline import gather_documents
        from specradar.sources.fetcher import Fetcher
        from specradar.sources.search import build_search_client
        from specradar.taxonomy.loader import get_taxonomy

        conf = params or {}
        vehicle = VehicleKey(
            make=conf["make"],
            model=conf["model"],
            version=conf.get("version", conf["model"]),
            model_year=conf.get("year"),
        )
        settings = get_settings()
        tax = get_taxonomy()
        docs = gather_documents(vehicle, tax, build_search_client(settings), Fetcher(settings))
        return [d.model_dump(mode="json") for d in docs]

    @task
    def extract_normalize_reconcile_persist(
        docs: list[dict[str, Any]], params: dict[str, Any] | None = None
    ) -> int:
        from specradar.config import get_settings
        from specradar.extraction.extractor import AnthropicLLMClient
        from specradar.models import Document, VehicleKey
        from specradar.pipeline import orchestrate
        from specradar.storage.bigquery import BigQueryWriter
        from specradar.taxonomy.loader import get_taxonomy

        conf = params or {}
        vehicle = VehicleKey(
            make=conf["make"],
            model=conf["model"],
            version=conf.get("version", conf["model"]),
            model_year=conf.get("year"),
        )
        settings = get_settings()
        tax = get_taxonomy()
        documents = [Document.model_validate(d) for d in docs]
        llm = AnthropicLLMClient(settings.anthropic_api_key, settings.llm_model)
        writer = BigQueryWriter(settings.google_cloud_project, settings.bq_dataset)
        writer.ensure_tables()
        result = orchestrate.run(vehicle, documents, llm, taxonomy=tax, writer=writer)
        writer.create_views()
        return result.rows_written

    docs = resolve_and_fetch()
    extract_normalize_reconcile_persist(docs)


specradar_on_demand()
