"""Stage [6]: persistence. Long format (vehicle × attribute × source) + pivot view."""

from specradar.storage.schema import (
    DIM_ATTRIBUTE_SCHEMA,
    DIM_SOURCE_SCHEMA,
    DIM_VEHICLE_SCHEMA,
    FACT_SPEC_SCHEMA,
    fact_spec_rows,
)
from specradar.storage.views import spec_sheet_view_sql

__all__ = [
    "DIM_ATTRIBUTE_SCHEMA",
    "DIM_SOURCE_SCHEMA",
    "DIM_VEHICLE_SCHEMA",
    "FACT_SPEC_SCHEMA",
    "fact_spec_rows",
    "spec_sheet_view_sql",
]
