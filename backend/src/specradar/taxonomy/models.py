from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DataType(StrEnum):
    SCALAR_UNIT = "SCALAR_UNIT"
    CATEGORICAL = "CATEGORICAL"
    COMPOSITE = "COMPOSITE"
    DIMENSIONAL = "DIMENSIONAL"
    ENUM_LIST = "ENUM_LIST"
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"


class SanityBounds(BaseModel):
    model_config = ConfigDict(frozen=True)

    min: float
    max: float


class AttributeDef(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    group: str
    data_type: DataType
    canonical_unit: str | None = None
    value_set: tuple[str, ...] | None = None
    parser: str | None = None
    sanity: SanityBounds | None = None
    tolerance: float | None = None

    @model_validator(mode="after")
    def _check_consistency(self) -> AttributeDef:
        dt = self.data_type
        if dt is DataType.SCALAR_UNIT and not self.canonical_unit:
            raise ValueError(f"{self.id}: SCALAR_UNIT requires canonical_unit")
        if dt in (DataType.CATEGORICAL, DataType.ENUM_LIST) and not self.value_set:
            raise ValueError(f"{self.id}: {dt.value} requires value_set")
        if dt in (DataType.COMPOSITE, DataType.DIMENSIONAL) and not self.parser:
            raise ValueError(f"{self.id}: {dt.value} requires parser")
        return self


class SourceDef(BaseModel):
    model_config = ConfigDict(frozen=True)

    domain: str
    authority_tier: int = Field(ge=1, le=4)
    kind: str
