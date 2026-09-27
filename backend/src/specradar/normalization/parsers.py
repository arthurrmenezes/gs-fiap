"""Deterministic parsers for COMPOSITE and DIMENSIONAL attributes.

Each returns a plain dict of sub-fields. Pure functions, unit-tested.
"""

from __future__ import annotations

import re
from typing import Any

from specradar.errors import NormalizationError
from specradar.normalization.units import parse_number
from specradar.textutil import fold

# ---------------------------------------------------------------- tire (DIMENSIONAL)
# 285/70 R17  ·  285/70R17  ·  265/65 R 18
_TIRE_RE = re.compile(r"(\d{3})\s*/\s*(\d{2,3})\s*[rR]?\s*(\d{2})")


def parse_tire(raw: str) -> dict[str, int]:
    """Parse a tire size string into width / aspect_ratio / rim_diameter_in.

    '285/70 R17 AT' → {'width': 285, 'aspect_ratio': 70, 'rim_diameter_in': 17}
    """
    m = _TIRE_RE.search(raw)
    if not m:
        raise NormalizationError(f"cannot parse tire size from {raw!r}")
    return {
        "width": int(m.group(1)),
        "aspect_ratio": int(m.group(2)),
        "rim_diameter_in": int(m.group(3)),
    }


# ---------------------------------------------------------------- engine (COMPOSITE)
_LAYOUT_RE = re.compile(r"\b([VWLIviwl])\s?(\d{1,2})\b")  # V6, L4, I3...
_CYL_WORD_RE = re.compile(r"(\d{1,2})\s*cilindros?", re.IGNORECASE)
# Displacement: prefer an explicit unit (3.0 L / 3.0 litros); fall back to a bare
# decimal like "2.0" common in engine strings ("2.0 turbo", "V6 3.0").
_DISPLACEMENT_UNIT_RE = re.compile(r"(\d(?:[.,]\d)?)\s*(?:[lL]\b|litros?)", re.IGNORECASE)
_DISPLACEMENT_BARE_RE = re.compile(r"\b(\d[.,]\d)\b")

_ASPIRATION_TERMS: list[tuple[str, str]] = [
    ("biturbo", "Biturbo"),
    ("bi-turbo", "Biturbo"),
    ("twin-turbo", "Biturbo"),
    ("twin turbo", "Biturbo"),
    ("supercharged", "Supercharged"),
    ("turbo", "Turbo"),
    ("aspirado", "Naturalmente aspirado"),
]


def parse_engine(raw: str) -> dict[str, Any]:
    """Parse an engine configuration string into sub-fields.

    'V6 3.0L biturbo' →
        {'layout': 'V', 'cylinders': 6, 'displacement_l': 3.0, 'aspiration': 'Biturbo'}
    Sub-fields that cannot be determined are omitted (caller decides relevance).
    """
    folded = fold(raw)
    out: dict[str, Any] = {}

    layout = _LAYOUT_RE.search(raw)
    if layout:
        out["layout"] = layout.group(1).upper()
        out["cylinders"] = int(layout.group(2))
    else:
        cyl = _CYL_WORD_RE.search(raw)
        if cyl:
            out["cylinders"] = int(cyl.group(1))

    disp = _DISPLACEMENT_UNIT_RE.search(raw) or _DISPLACEMENT_BARE_RE.search(raw)
    if disp:
        out["displacement_l"] = parse_number(disp.group(1))

    for term, canonical in _ASPIRATION_TERMS:
        if term in folded:
            out["aspiration"] = canonical
            break

    if not out:
        raise NormalizationError(f"cannot parse engine configuration from {raw!r}")
    return out


# ---------------------------------------------------------------- transmission (COMPOSITE)
_GEARS_RE = re.compile(r"(\d{1,2})\s*(?:marchas?|velocidades?|speed)", re.IGNORECASE)
_TRANS_TYPES: list[tuple[str, str]] = [
    ("automatizada", "Automatizada"),
    ("dupla embreagem", "Automatizada de dupla embreagem"),
    ("dct", "Automatizada de dupla embreagem"),
    ("cvt", "CVT"),
    ("automatica", "Automática"),
    ("automatic", "Automática"),
    ("manual", "Manual"),
]
_PADDLE_TERMS = ("paddle", "borboleta", "aleta")


def parse_transmission(raw: str) -> dict[str, Any]:
    """Parse a transmission string into type / gears / paddle_shifters.

    'automática, 10 marchas, paddle shifters' →
        {'type': 'Automática', 'gears': 10, 'paddle_shifters': True}
    """
    folded = fold(raw)
    out: dict[str, Any] = {}

    for term, canonical in _TRANS_TYPES:
        if term in folded:
            out["type"] = canonical
            break

    gears = _GEARS_RE.search(raw)
    if gears:
        out["gears"] = int(gears.group(1))

    out["paddle_shifters"] = any(term in folded for term in _PADDLE_TERMS)

    if "type" not in out and "gears" not in out:
        raise NormalizationError(f"cannot parse transmission from {raw!r}")
    return out


# Registry consumed by the normalization dispatcher (keyed by AttributeDef.parser).
PARSERS = {
    "tire": parse_tire,
    "engine": parse_engine,
    "transmission": parse_transmission,
}
