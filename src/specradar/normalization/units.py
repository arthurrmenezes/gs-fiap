"""Deterministic unit conversion. Each converter is unit-tested in both directions.

Beware: cv (metric, = PS = cavalo-vapor) and hp (imperial) are NOT equal.
"""

from __future__ import annotations

import re

from specradar.errors import NormalizationError

# A number possibly in PT-BR formatting: "397", "3.0", "5,8", "2.283", "180.000,50".
_NUMBER_RE = re.compile(r"[-+]?\d[\d.,]*")
# A unit token: letters, slashes, degree, micro, etc. after the number.
_UNIT_RE = re.compile(r"[A-Za-zµ°%/]+(?:\s*[A-Za-z0-9/]+)?")


def parse_number(raw: str) -> float:
    """Parse a number that may use PT-BR or EN thousands/decimal separators.

    Rules (sources are PT-BR but EN appears too):
      - both '.' and ',' present → the rightmost is the decimal separator.
      - only ',' present → comma is the decimal separator (PT-BR).
      - only '.' present → a single dot with exactly 3 trailing digits is a
        thousands separator (e.g. "2.283" → 2283); otherwise it is decimal
        (e.g. "3.0" → 3.0). Multiple dots → all thousands separators.
    """
    m = _NUMBER_RE.search(raw)
    if not m:
        raise NormalizationError(f"no number found in {raw!r}")
    token = m.group(0)
    sign = -1.0 if token.startswith("-") else 1.0
    token = token.lstrip("+-")

    has_dot = "." in token
    has_comma = "," in token

    if has_dot and has_comma:
        if token.rfind(",") > token.rfind("."):
            cleaned = token.replace(".", "").replace(",", ".")
        else:
            cleaned = token.replace(",", "")
    elif has_comma:
        # PT-BR decimal; collapse any thousand dots already handled above.
        cleaned = token.replace(".", "").replace(",", ".")
    elif has_dot:
        dots = token.count(".")
        head, _, tail = token.rpartition(".")
        if dots == 1 and len(tail) == 3 and head.isdigit():
            cleaned = token.replace(".", "")  # thousands: 2.283 -> 2283
        elif dots > 1:
            cleaned = token.replace(".", "")  # 1.234.567 -> 1234567
        else:
            cleaned = token  # decimal: 3.0
    else:
        cleaned = token

    try:
        return sign * float(cleaned)
    except ValueError as exc:
        raise NormalizationError(f"cannot parse number from {raw!r}") from exc


def split_value_unit(raw: str) -> tuple[float, str | None]:
    """Split a raw scalar string into (number, unit_token | None)."""
    value = parse_number(raw)
    m = _NUMBER_RE.search(raw)
    assert m is not None  # parse_number would have raised
    rest = raw[m.end() :].strip()
    unit_match = _UNIT_RE.match(rest)
    unit = unit_match.group(0).strip() if unit_match else None
    return value, unit


# Conversion factors → canonical unit. Each maps a folded source-unit token to a
# multiplicative factor. The canonical unit itself maps to 1.0.
# Sources: 1 hp = 1.01387 PS(cv); 1 kW = 1.35962 cv; 1 kgfm = 9.80665 Nm;
#          1 lbft = 1.35582 Nm; 1 cc = 0.001 L; 1 mi = 1.60934 km.
_CONVERSIONS: dict[str, dict[str, float]] = {
    "cv": {"cv": 1.0, "ps": 1.0, "hp": 1.01387, "bhp": 1.01387, "kw": 1.35962},
    "Nm": {"nm": 1.0, "n.m": 1.0, "kgfm": 9.80665, "kgf.m": 9.80665, "lbft": 1.35582},
    "L": {"l": 1.0, "litros": 1.0, "cc": 0.001, "cm3": 0.001, "cm³": 0.001},
    "km/L": {"km/l": 1.0},
    "km/h": {"km/h": 1.0, "kmh": 1.0, "kph": 1.0, "mph": 1.60934},
    "mm": {"mm": 1.0, "cm": 10.0, "m": 1000.0},
    "kg": {"kg": 1.0, "t": 1000.0, "ton": 1000.0},
    "in": {"in": 1.0, '"': 1.0, "pol": 1.0, "”": 1.0},
    "s": {"s": 1.0, "seg": 1.0},
    "g/km": {"g/km": 1.0},
    "BRL": {"brl": 1.0, "r$": 1.0, "reais": 1.0},
    "years": {"years": 1.0, "anos": 1.0, "ano": 1.0},
    # Dimensionless counts — unit token is informational only.
    "gears": {},
    "airbags": {},
    "seats": {},
}

# Special-case: L/100km → km/L is reciprocal, not a factor.
_RECIPROCAL_TO_KML = {"l/100km", "l/100 km"}


def to_canonical(value: float, src_unit: str | None, canonical_unit: str) -> float:
    """Convert `value` (in `src_unit`) into `canonical_unit`.

    A missing src_unit is assumed to already be in the canonical unit. An unknown
    src_unit raises NormalizationError — silent wrong conversion is a fatal,
    invisible bug (CLAUDE.md §15).
    """
    table = _CONVERSIONS.get(canonical_unit)
    if table is None:
        raise NormalizationError(f"no conversion table for canonical unit {canonical_unit!r}")

    if src_unit is None:
        return value

    key = src_unit.lower().strip().rstrip(".")

    # consumption reciprocal handling
    if canonical_unit == "km/L" and key in _RECIPROCAL_TO_KML:
        if value == 0:
            raise NormalizationError("cannot convert 0 L/100km to km/L")
        return 100.0 / value

    if not table:  # dimensionless count; ignore the unit token
        return value
    if key in table:
        return value * table[key]
    raise NormalizationError(f"unknown unit {src_unit!r} for canonical unit {canonical_unit!r}")


def normalize_scalar(raw: str, canonical_unit: str) -> tuple[float, str]:
    """Normalize a raw scalar string to (value_in_canonical_unit, canonical_unit)."""
    value, src_unit = split_value_unit(raw)
    return to_canonical(value, src_unit, canonical_unit), canonical_unit
