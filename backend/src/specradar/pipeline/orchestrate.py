from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime

from specradar.config import get_settings
from specradar.extraction.extractor import LLMClient, extract_attributes
from specradar.logging import configure_logging, get_logger
from specradar.models import Document, NormalizedValue, ReconciledSpec, VehicleKey
from specradar.normalization.dispatch import normalize_value
from specradar.reconciliation.coalesce import reconcile_attribute
from specradar.sources.cleaner import clean_text
from specradar.sources.fetcher import Fetcher
from specradar.sources.resolver import SearchClient, resolve_sources
from specradar.taxonomy.loader import Taxonomy, get_taxonomy
from specradar.taxonomy.models import AttributeDef

log = get_logger("pipeline")


@dataclass
class PipelineResult:
    vehicle: VehicleKey
    specs: list[ReconciledSpec]
    document_count: int
    documents: list[Document] = field(default_factory=list)


def gather_documents(
    vehicle: VehicleKey,
    taxonomy: Taxonomy,
    search_client: SearchClient,
    fetcher: Fetcher,
    *,
    now: datetime | None = None,
) -> list[Document]:
    now = now or datetime.now(UTC)
    candidates = resolve_sources(vehicle, taxonomy, search_client)
    documents: list[Document] = []
    for cand in candidates:
        try:
            fetched = fetcher.fetch(cand.url)
            text = clean_text(fetched.content, fetched.content_type)
        except Exception as exc:
            log.warning("fetch_or_clean_failed", url=cand.url, error=str(exc))
            continue
        documents.append(
            Document(
                url=cand.url,
                domain=cand.domain,
                source_tier=cand.authority_tier,
                clean_text=text,
                content_hash=fetched.content_hash,
                fetched_at=now,
            )
        )
    return documents


def extract_and_normalize(
    documents: list[Document],
    attributes: list[AttributeDef],
    llm_client: LLMClient,
    taxonomy: Taxonomy,
) -> dict[str, list[NormalizedValue]]:
    by_id = {a.id: a for a in attributes}
    grouped: dict[str, list[NormalizedValue]] = defaultdict(list)
    for doc in documents:
        extracted = extract_attributes(llm_client, attributes, doc)
        for ev in extracted:
            if not (ev.found and ev.evidence_verified):
                continue
            attr = by_id[ev.attribute_id]
            normalized = normalize_value(ev, attr, doc, taxonomy)
            if normalized is not None:
                grouped[ev.attribute_id].append(normalized)
    return grouped


def reconcile_specs(
    vehicle: VehicleKey,
    attributes: list[AttributeDef],
    grouped: dict[str, list[NormalizedValue]],
    *,
    now: datetime | None = None,
) -> list[ReconciledSpec]:
    now = now or datetime.now(UTC)
    return [
        reconcile_attribute(vehicle, attr, grouped.get(attr.id, []), now=now) for attr in attributes
    ]


def run_extraction_pipeline(
    vehicle: VehicleKey,
    documents: list[Document],
    llm_client: LLMClient,
    *,
    taxonomy: Taxonomy | None = None,
    attributes: list[AttributeDef] | None = None,
    now: datetime | None = None,
) -> list[ReconciledSpec]:
    taxonomy = taxonomy or get_taxonomy()
    attributes = attributes if attributes is not None else taxonomy.all_attributes()
    grouped = extract_and_normalize(documents, attributes, llm_client, taxonomy)
    return reconcile_specs(vehicle, attributes, grouped, now=now)


def run(
    vehicle: VehicleKey,
    documents: list[Document],
    llm_client: LLMClient,
    *,
    taxonomy: Taxonomy | None = None,
    attribute_ids: list[str] | None = None,
    now: datetime | None = None,
) -> PipelineResult:
    taxonomy = taxonomy or get_taxonomy()
    if attribute_ids is None:
        attributes = taxonomy.all_attributes()
    else:
        wanted = set(attribute_ids)
        attributes = [a for a in taxonomy.all_attributes() if a.id in wanted]

    specs = run_extraction_pipeline(
        vehicle, documents, llm_client, taxonomy=taxonomy, attributes=attributes, now=now
    )
    return PipelineResult(
        vehicle=vehicle,
        specs=specs,
        document_count=len(documents),
        documents=documents,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the SpecRadar pipeline for one vehicle.")
    parser.add_argument("--make", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--version", default="")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument(
        "--fixture",
        default=None,
        help="Path to an offline fixture dir (documents/ + extraction.json). "
        "Defaults to the bundled Ranger Raptor demo.",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    configure_logging(settings.log_level)

    vehicle = VehicleKey(
        make=args.make, model=args.model, version=args.version or args.model, model_year=args.year
    )

    from specradar.pipeline.fixtures import FixtureLLMClient, load_fixture

    fixture_dir = args.fixture
    if fixture_dir is None:
        from specradar.config import REPO_ROOT

        fixture_dir = str(REPO_ROOT / "examples" / "ranger_raptor")
    try:
        documents, responses = load_fixture(fixture_dir)
    except FileNotFoundError as exc:
        print(f"No fixture available ({exc}). Provide --fixture or live clients.", file=sys.stderr)
        return 2

    result = run(vehicle, documents, FixtureLLMClient(responses))

    print(f"\nSpecRadar — {vehicle.slug()}  ({result.document_count} sources)\n")
    for spec in result.specs:
        if spec.status.value == "NA":
            continue
        print(f"  {spec.attribute_id:32} {spec.value_norm!s:40} [{spec.status.value}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
