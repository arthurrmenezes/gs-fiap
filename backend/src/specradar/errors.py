from __future__ import annotations


class SpecRadarError(Exception):
    pass


class TaxonomyError(SpecRadarError):
    pass


class UnknownAttributeError(SpecRadarError):
    pass


class NormalizationError(SpecRadarError):
    pass


class SourceNotAllowedError(SpecRadarError):
    pass


class ExtractionError(SpecRadarError):
    pass
