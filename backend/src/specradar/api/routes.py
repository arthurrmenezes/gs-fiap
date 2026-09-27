"""API routes: health, taxonomy introspection, and the spec-sheet endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from specradar.api.runner import PipelineUnavailableError, run_for_request
from specradar.api.schemas import SpecRequest, SpecSheetResponse
from specradar.api.sheet import build_spec_sheet
from specradar.config import get_settings
from specradar.errors import UnknownAttributeError
from specradar.logging import get_logger
from specradar.taxonomy.loader import get_taxonomy

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


@router.post("/spec", response_model=SpecSheetResponse)
def spec(request: SpecRequest) -> SpecSheetResponse:
    """Build the standardized spec sheet for a vehicle version."""
    tax = get_taxonomy()
    settings = get_settings()
    vehicle = request.to_vehicle_key()
    log.info("spec_request", vehicle=vehicle.slug(), attributes=request.attributes)

    try:
        result = run_for_request(vehicle, request.attributes, settings, tax)
    except UnknownAttributeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except PipelineUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return build_spec_sheet(vehicle, result.specs, tax, result.document_count)
