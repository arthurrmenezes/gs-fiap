"""Core domain models flowing through the 6-stage pipeline.

These are Pydantic v2 models (CLAUDE.md §11). Each stage consumes the previous
stage's output type:

    Document  --extract-->  ExtractedValue  --normalize-->  NormalizedValue
              --reconcile-->  ReconciledSpec  --pivot-->  SpecSheet
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SpecStatus(StrEnum):
    """Status of a reconciled spec value. Absence and conflict are explicit."""

    OK = "OK"
    CONFLICT = "CONFLICT"
    ANOMALY = "ANOMALY"
    NA = "NA"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"


class VehicleKey(BaseModel):
    """Identity of a vehicle version. Model year matters — drift is real."""

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
    """A fetched + cleaned source document. Lives in the raw/staging trail."""

    model_config = ConfigDict(frozen=True)

    url: str
    domain: str
    source_tier: int
    clean_text: str
    content_hash: str
    fetched_at: datetime


class ExtractedValue(BaseModel):
    """LLM output for one attribute on one document. The LLM stops here.

    The LLM never converts, reconciles, or decides conflicts. It only reads and
    cites. `evidence_snippet` MUST be a literal substring of the source document;
    the verifier enforces this downstream.
    """

    attribute_id: str
    value_raw: str | None
    evidence_snippet: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    found: bool

    # populated by the verifier
    evidence_verified: bool = False


class NormalizedValue(BaseModel):
    """An extracted value after deterministic normalization.

    `value_norm` holds the canonical, comparable representation. For SCALAR_UNIT
    it is a float in the canonical unit; for COMPOSITE/DIMENSIONAL it is a dict of
    sub-fields; for ENUM_LIST a list; for CATEGORICAL/BOOLEAN/TEXT a string/bool.
    """

    attribute_id: str
    value_raw: str | None
    value_norm: Any
    unit: str | None
    confidence: float
    evidence_snippet: str | None
    evidence_verified: bool

    # provenance
    source_url: str
    source_tier: int
    extracted_at: datetime


class ReconciledSpec(BaseModel):
    """The final, single value for an attribute on a vehicle, with provenance.

    On CONFLICT both candidate values are preserved in `alternatives`.
    """

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
