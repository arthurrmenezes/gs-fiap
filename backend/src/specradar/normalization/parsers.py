from __future__ import annotations

import re
from typing import Any

from specradar.errors import NormalizationError
from specradar.normalization.units import parse_number
from specradar.textutil import fold

_TIRE_RE = re.compile(r"(\d{3})\s*/\s*(\d{2,3})\s*[rR]?\s*(\d{2})")


def parse_tire(raw: str) -> dict[str, int]:
    m = _TIRE_RE.search(raw)
    if not m:
        raise NormalizationError(f"cannot parse tire size from {raw!r}")
    return {
        "width": int(m.group(1)),
        "aspect_ratio": int(m.group(2)),
        "rim_diameter_in": int(m.group(3)),
    }


_LAYOUT_RE = re.compile(r"\b([VWLIviwl])\s?(\d{1,2})\b")
_CYL_WORD_RE = re.compile(r"(\d{1,2})\s*cilindros?", re.IGNORECASE)
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


PARSERS = {
    "tire": parse_tire,
    "engine": parse_engine,
    "transmission": parse_transmission,
}
