from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SpecStatus(StrEnum):
    OK = "OK"
    CONFLICT = "CONFLICT"
    ANOMALY = "ANOMALY"
    NA = "NA"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"


class VehicleKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    make: str
    model: str
    version: str
    model_year: int | None = None
    market: str = "BR"

    def slug(self) -> str:
        parts = [self.make, self.model, self.version]
        if self.model_year is not None:
            parts.append(str(self.model_year))
        return "::".join(p.strip() for p in parts)


class Document(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    domain: str
    source_tier: int
    clean_text: str
    content_hash: str
    fetched_at: datetime


class ExtractedValue(BaseModel):
    attribute_id: str
    value_raw: str | None
    evidence_snippet: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    found: bool

    evidence_verified: bool = False


class NormalizedValue(BaseModel):
    attribute_id: str
    value_raw: str | None
    value_norm: Any
    unit: str | None
    confidence: float
    evidence_snippet: str | None
    evidence_verified: bool

    source_url: str
    source_tier: int
    extracted_at: datetime


class ReconciledSpec(BaseModel):
    vehicle_key: VehicleKey
    attribute_id: str
    value_raw: str | None
    value_norm: Any
    unit: str | None
    status: SpecStatus
    confidence: float
    source_url: str | None
    source_tier: int | None
    evidence_snippet: str | None
    reconciled_at: datetime
    alternatives: list[NormalizedValue] = Field(default_factory=list)
    note: str | None = None
