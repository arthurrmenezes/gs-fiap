from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from specradar.models import ReconciledSpec, SpecStatus, VehicleKey


class SpecRequest(BaseModel):
    make: str = Field(min_length=1, examples=["Ford"])
    model: str = Field(min_length=1, examples=["Ranger Raptor"])
    version: str = Field(min_length=1, examples=["Raptor 3.0 V6"])
    year: int | None = Field(default=None, ge=1990, le=2100, examples=[2026])
    market: str = Field(default="BR")
    attributes: list[str] = Field(default_factory=list)

    def to_vehicle_key(self) -> VehicleKey:
        return VehicleKey(
            make=self.make,
            model=self.model,
            version=self.version,
            model_year=self.year,
            market=self.market,
        )


class SpecField(BaseModel):
    attribute_id: str
    name: str
    group: str
    data_type: str
    value: Any = None
    value_raw: str | None = None
    unit: str | None = None
    status: SpecStatus
    confidence: float
    source_url: str | None = None
    source_tier: int | None = None
    evidence_snippet: str | None = None
    note: str | None = None
    alternatives: list[Any] = Field(default_factory=list)


class SpecSheetResponse(BaseModel):
    make: str
    model: str
    version: str
    year: int | None
    market: str
    generated_at: datetime
    source_count: int
    mode: str = "demo"
    unknown_attributes: list[str] = Field(default_factory=list)
    fields: list[SpecField]

    @property
    def has_conflicts(self) -> bool:
        return any(f.status is SpecStatus.CONFLICT for f in self.fields)


def spec_to_field(spec: ReconciledSpec, name: str, group: str, data_type: str) -> SpecField:
    return SpecField(
        attribute_id=spec.attribute_id,
        name=name,
        group=group,
        data_type=data_type,
        value=spec.value_norm,
        value_raw=spec.value_raw,
        unit=spec.unit,
        status=spec.status,
        confidence=spec.confidence,
        source_url=spec.source_url,
        source_tier=spec.source_tier,
        evidence_snippet=spec.evidence_snippet,
        note=spec.note,
        alternatives=[alt.value_norm for alt in spec.alternatives],
    )
