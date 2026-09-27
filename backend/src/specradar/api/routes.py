"""API routes: health, taxonomy introspection, and the spec-sheet endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from specradar.api.runner import run_for_request
from specradar.api.schemas import SpecRequest, SpecSheetResponse
from specradar.api.sheet import build_spec_sheet
from specradar.config import get_settings
from specradar.errors import UnknownAttributeError
from specradar.logging import get_logger
from specradar.taxonomy.loader import Taxonomy, get_taxonomy

router = APIRouter()
log = get_logger("api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/taxonomy")
def taxonomy() -> dict[str, object]:
    """Expose the canonical taxonomy (attributes + sources) for clients/tooling."""
    tax = get_taxonomy()
    return {
        "attributes": [a.model_dump(mode="json") for a in tax.all_attributes()],
        "sources": [s.model_dump(mode="json") for s in tax.all_sources()],
    }


def resolve_labels(labels: list[str], tax: Taxonomy) -> tuple[list[str] | None, list[str]]:
    """Split free labels into canonical ids and unrecognized labels.

    No labels → None (full sheet). Unknown labels are reported back to the
    client instead of failing the whole request.
    """
    cleaned = [lbl.strip() for lbl in labels if lbl.strip()]
    if not cleaned:
        return None, []
    ids: list[str] = []
    unknown: list[str] = []
    for label in cleaned:
        try:
            attr_id = tax.resolve_attribute(label)
        except UnknownAttributeError:
            unknown.append(label)
            continue
        if attr_id not in ids:
            ids.append(attr_id)
    return ids, unknown


@router.post("/spec", response_model=SpecSheetResponse)
def spec(request: SpecRequest) -> SpecSheetResponse:
    """Build the standardized spec sheet for a vehicle version."""
    tax = get_taxonomy()
    settings = get_settings()
    vehicle = request.to_vehicle_key()
    attribute_ids, unknown = resolve_labels(request.attributes, tax)
    log.info("spec_request", vehicle=vehicle.slug(), attributes=attribute_ids, unknown=unknown)

    run = run_for_request(vehicle, attribute_ids, settings, tax)
    return build_spec_sheet(
        vehicle,
        run.result.specs,
        tax,
        run.result.document_count,
        mode=run.mode,
        unknown_attributes=unknown,
    )
