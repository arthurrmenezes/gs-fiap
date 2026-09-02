"""Specific exception types. Never swallow exceptions silently (CLAUDE.md §11)."""

from __future__ import annotations


class SpecRadarError(Exception):
    """Base class for all SpecRadar errors."""


class TaxonomyError(SpecRadarError):
    """The taxonomy YAML is missing, malformed, or internally inconsistent."""


class UnknownAttributeError(SpecRadarError):
    """A free attribute label could not be mapped to a canonical attribute id."""


class NormalizationError(SpecRadarError):
    """A deterministic conversion or parse failed (e.g. unknown unit)."""


class SourceNotAllowedError(SpecRadarError):
    """A URL/domain is not present in the source allowlist."""


class ExtractionError(SpecRadarError):
    """The LLM extraction call failed or returned a schema-invalid payload."""
