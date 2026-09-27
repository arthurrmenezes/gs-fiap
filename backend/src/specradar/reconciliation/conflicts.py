from __future__ import annotations

from typing import Any

from specradar.taxonomy.models import AttributeDef, DataType
from specradar.textutil import fold

_DEFAULT_SCALAR_TOLERANCE = 0.02


def _scalar_equal(a: float, b: float, tolerance: float) -> bool:
    if a == b:
        return True
    denom = max(abs(a), abs(b))
    if denom == 0:
        return True
    return abs(a - b) / denom <= tolerance


def values_equal(attr: AttributeDef, a: Any, b: Any) -> bool:
    match attr.data_type:
        case DataType.SCALAR_UNIT:
            if not (isinstance(a, int | float) and isinstance(b, int | float)):
                return bool(a == b)
            tol = attr.tolerance if attr.tolerance is not None else _DEFAULT_SCALAR_TOLERANCE
            return _scalar_equal(float(a), float(b), tol)
        case DataType.ENUM_LIST:
            return isinstance(a, list) and isinstance(b, list) and set(a) == set(b)
        case DataType.COMPOSITE | DataType.DIMENSIONAL:
            return bool(a == b)
        case DataType.BOOLEAN:
            return bool(a) == bool(b)
        case _:
            return fold(str(a)) == fold(str(b))
