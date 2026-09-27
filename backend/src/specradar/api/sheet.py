"""Build the standardized SpecSheetResponse from reconciled specs + taxonomy."""

from __future__ import annotations

from datetime import UTC, datetime

from specradar.api.schemas import SpecSheetResponse, spec_to_field
from specradar.models import ReconciledSpec, VehicleKey
from specradar.taxonomy.loader import Taxonomy


def build_spec_sheet(
    vehicle: VehicleKey,
    specs: list[ReconciledSpec],
    taxonomy: Taxonomy,
    source_count: int,
    *,
    generated_at: datetime | None = None,
) -> SpecSheetResponse:
    """Project reconciled specs into the always-same-format sheet, grouped order."""
    fields = []
    for spec in specs:
        attr = taxonomy.get(spec.attribute_id)
        fields.append(spec_to_field(spec, attr.name, attr.group, attr.data_type.value))
    return SpecSheetResponse(
        make=vehicle.make,
        model=vehicle.model,
        version=vehicle.version,
        year=vehicle.model_year,
        market=vehicle.market,
        generated_at=generated_at or datetime.now(UTC),
        source_count=source_count,
        fields=fields,
    )
