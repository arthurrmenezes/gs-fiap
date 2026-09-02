"""Deterministic normalization — pure Python, never the LLM (CLAUDE.md §2)."""

from specradar.normalization.categorical import normalize_categorical, normalize_enum_list
from specradar.normalization.parsers import parse_engine, parse_tire, parse_transmission
from specradar.normalization.units import normalize_scalar, parse_number, to_canonical

__all__ = [
    "normalize_categorical",
    "normalize_enum_list",
    "normalize_scalar",
    "parse_engine",
    "parse_number",
    "parse_tire",
    "parse_transmission",
    "to_canonical",
]
