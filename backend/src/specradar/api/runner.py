"""Resolve which pipeline clients to use for an API request.

Live mode requires Anthropic + search keys. When they are absent, the API falls
back to the bundled offline fixture for vehicles it has demo data for, so the
contract is demonstrable without secrets. Anything else returns a clear 503.
"""

from __future__ import annotations

from specradar.config import REPO_ROOT, Settings
from specradar.errors import SpecRadarError
from specradar.models import VehicleKey
from specradar.pipeline import orchestrate
from specradar.pipeline.fixtures import FixtureLLMClient, load_fixture
from specradar.taxonomy.loader import Taxonomy


class PipelineUnavailableError(SpecRadarError):
    """No live clients configured and no offline fixture matches the request."""


# Bundled offline demos: (make, model substring) → fixture dir name under examples/.
_OFFLINE_FIXTURES = {
    ("ford", "ranger raptor"): "ranger_raptor",
}


def _fixture_for(vehicle: VehicleKey) -> str | None:
    key = (vehicle.make.lower(), vehicle.model.lower())
    if key in _OFFLINE_FIXTURES:
        return _OFFLINE_FIXTURES[key]
    return None


def run_for_request(
    vehicle: VehicleKey,
    requested_labels: list[str],
    settings: Settings,
    taxonomy: Taxonomy,
) -> orchestrate.PipelineResult:
    """Run the pipeline for a request, choosing live or offline clients."""
    if settings.anthropic_api_key and settings.search_api_key:
        return _run_live(vehicle, requested_labels, settings, taxonomy)

    fixture_name = _fixture_for(vehicle)
    if fixture_name is None:
        raise PipelineUnavailableError(
            "live extraction is not configured (set ANTHROPIC_API_KEY and SEARCH_API_KEY) "
            "and no offline fixture exists for this vehicle"
        )
    fixture_dir = REPO_ROOT / "examples" / fixture_name
    documents, responses = load_fixture(fixture_dir)
    return orchestrate.run(
        vehicle,
        documents,
        FixtureLLMClient(responses),
        taxonomy=taxonomy,
        requested_labels=requested_labels,
    )


def _run_live(
    vehicle: VehicleKey,
    requested_labels: list[str],
    settings: Settings,
    taxonomy: Taxonomy,
) -> orchestrate.PipelineResult:
    from specradar.extraction.extractor import AnthropicLLMClient
    from specradar.sources.fetcher import Fetcher

    # A real SerpAPI/Google CSE client implements SearchClient; wiring it is a
    # deployment concern. Kept behind the live branch so offline use needs no deps.
    from specradar.sources.search import build_search_client

    search_client = build_search_client(settings)
    fetcher = Fetcher(settings)
    documents = orchestrate.gather_documents(vehicle, taxonomy, search_client, fetcher)
    llm = AnthropicLLMClient(settings.anthropic_api_key, settings.llm_model)
    return orchestrate.run(
        vehicle, documents, llm, taxonomy=taxonomy, requested_labels=requested_labels
    )
