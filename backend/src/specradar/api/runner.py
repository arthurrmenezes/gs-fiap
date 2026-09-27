from __future__ import annotations

from dataclasses import dataclass

from specradar.config import REPO_ROOT, Settings
from specradar.models import VehicleKey
from specradar.pipeline import orchestrate
from specradar.pipeline.fixtures import FixtureLLMClient, load_fixture
from specradar.taxonomy.loader import Taxonomy

_OFFLINE_FIXTURES = {
    ("ford", "ranger raptor"): "ranger_raptor",
}


@dataclass
class RunOutcome:
    result: orchestrate.PipelineResult
    mode: str


def _fixture_for(vehicle: VehicleKey) -> str | None:
    key = (vehicle.make.strip().lower(), vehicle.model.strip().lower())
    return _OFFLINE_FIXTURES.get(key)


def run_for_request(
    vehicle: VehicleKey,
    attribute_ids: list[str] | None,
    settings: Settings,
    taxonomy: Taxonomy,
) -> RunOutcome:
    if settings.anthropic_api_key and settings.search_api_key:
        return RunOutcome(_run_live(vehicle, attribute_ids, settings, taxonomy), "live")

    fixture_name = _fixture_for(vehicle)
    if fixture_name is None:
        result = orchestrate.run(
            vehicle, [], FixtureLLMClient([]), taxonomy=taxonomy, attribute_ids=attribute_ids
        )
        return RunOutcome(result, "demo")

    documents, responses = load_fixture(REPO_ROOT / "examples" / fixture_name)
    result = orchestrate.run(
        vehicle,
        documents,
        FixtureLLMClient(responses),
        taxonomy=taxonomy,
        attribute_ids=attribute_ids,
    )
    return RunOutcome(result, "demo")


def _run_live(
    vehicle: VehicleKey,
    attribute_ids: list[str] | None,
    settings: Settings,
    taxonomy: Taxonomy,
) -> orchestrate.PipelineResult:
    from specradar.extraction.extractor import AnthropicLLMClient
    from specradar.sources.fetcher import Fetcher
    from specradar.sources.search import build_search_client

    search_client = build_search_client(settings)
    fetcher = Fetcher()
    documents = orchestrate.gather_documents(vehicle, taxonomy, search_client, fetcher)
    llm = AnthropicLLMClient(settings.anthropic_api_key, settings.llm_model)
    return orchestrate.run(vehicle, documents, llm, taxonomy=taxonomy, attribute_ids=attribute_ids)
