"""Load and validate the taxonomy YAMLs into immutable in-memory objects."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from specradar.config import get_settings
from specradar.errors import TaxonomyError, UnknownAttributeError
from specradar.taxonomy.models import AttributeDef, SourceDef
from specradar.textutil import fold


class Taxonomy:
    """Validated, queryable view over attributes + synonyms + sources."""

    def __init__(
        self,
        attributes: list[AttributeDef],
        attribute_synonyms: dict[str, str],
        value_synonyms: dict[str, dict[str, str]],
        sources: list[SourceDef],
    ) -> None:
        self._attributes: dict[str, AttributeDef] = {a.id: a for a in attributes}
        self._names = {fold(a.name): a.id for a in attributes}  # fold(name) -> attribute_id
        self._attribute_synonyms = attribute_synonyms  # fold(label) -> attribute_id
        self._value_synonyms = value_synonyms  # attribute_id -> {fold(value): canonical}
        self._sources: dict[str, SourceDef] = {s.domain: s for s in sources}
        self._validate()

    # -- construction validation --------------------------------------------
    def _validate(self) -> None:
        for label, attr_id in self._attribute_synonyms.items():
            if attr_id not in self._attributes:
                raise TaxonomyError(
                    f"synonyms.yaml maps '{label}' to unknown attribute '{attr_id}'"
                )
        for attr_id in self._value_synonyms:
            if attr_id not in self._attributes:
                raise TaxonomyError(
                    f"synonyms.yaml has value map for unknown attribute '{attr_id}'"
                )

    # -- attribute access ----------------------------------------------------
    def all_attributes(self) -> list[AttributeDef]:
        """All attributes in taxonomy-declared order."""
        return list(self._attributes.values())

    def get(self, attribute_id: str) -> AttributeDef:
        """Look up an attribute by canonical id, raising if unknown."""
        try:
            return self._attributes[attribute_id]
        except KeyError as exc:
            raise UnknownAttributeError(f"unknown attribute id: {attribute_id}") from exc

    def has(self, attribute_id: str) -> bool:
        return attribute_id in self._attributes

    def resolve_attribute(self, free_label: str) -> str:
        """Map a free attribute label to a canonical attribute id.

        A label that is already a canonical id passes through. Otherwise it is
        looked up in the synonym map, then by display name (both case- and
        accent-insensitive). Unknown → raise.
        """
        if free_label in self._attributes:
            return free_label
        key = fold(free_label)
        if key in self._attribute_synonyms:
            return self._attribute_synonyms[key]
        if key in self._names:
            return self._names[key]
        raise UnknownAttributeError(
            f"cannot resolve attribute label '{free_label}' to the taxonomy"
        )

    def resolve_value(self, attribute_id: str, raw_value: str) -> str | None:
        """Map a source value token to its canonical value for an attribute.

        Returns the canonical value, or None if no synonym matches (caller decides
        whether the raw value is already canonical / acceptable).
        """
        per_attr = self._value_synonyms.get(attribute_id, {})
        return per_attr.get(fold(raw_value))

    # -- source access -------------------------------------------------------
    def all_sources(self) -> list[SourceDef]:
        return list(self._sources.values())

    def source_for_domain(self, domain: str) -> SourceDef | None:
        """Return the SourceDef whose domain matches (suffix-aware), else None."""
        domain = domain.lower().removeprefix("www.")
        if domain in self._sources:
            return self._sources[domain]
        # allow subdomains: news.ford.com.br matches ford.com.br
        for src_domain, src in self._sources.items():
            if domain == src_domain or domain.endswith("." + src_domain):
                return src
        return None

    def is_allowed(self, domain: str) -> bool:
        return self.source_for_domain(domain) is not None


# --- YAML loading -----------------------------------------------------------
def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise TaxonomyError(f"taxonomy file not found: {path}")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise TaxonomyError(f"taxonomy file must be a mapping: {path}")
    return data


def _load_attributes(taxonomy_dir: Path) -> list[AttributeDef]:
    data = _read_yaml(taxonomy_dir / "attributes.yaml")
    raw = data.get("attributes")
    if not isinstance(raw, list) or not raw:
        raise TaxonomyError("attributes.yaml: 'attributes' must be a non-empty list")
    attributes: list[AttributeDef] = []
    seen: set[str] = set()
    for item in raw:
        try:
            attr = AttributeDef.model_validate(item)
        except Exception as exc:
            raise TaxonomyError(f"invalid attribute entry {item!r}: {exc}") from exc
        if attr.id in seen:
            raise TaxonomyError(f"duplicate attribute id: {attr.id}")
        seen.add(attr.id)
        attributes.append(attr)
    return attributes


def _load_synonyms(taxonomy_dir: Path) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    data = _read_yaml(taxonomy_dir / "synonyms.yaml")
    attr_map_raw = data.get("attributes", {}) or {}
    val_map_raw = data.get("values", {}) or {}

    attribute_synonyms = {fold(str(label)): str(attr_id) for label, attr_id in attr_map_raw.items()}

    value_synonyms: dict[str, dict[str, str]] = {}
    for attr_id, mapping in val_map_raw.items():
        value_synonyms[str(attr_id)] = {
            fold(str(src)): str(canonical) for src, canonical in mapping.items()
        }
    return attribute_synonyms, value_synonyms


def _load_sources(taxonomy_dir: Path) -> list[SourceDef]:
    data = _read_yaml(taxonomy_dir / "sources.yaml")
    raw = data.get("sources")
    if not isinstance(raw, list) or not raw:
        raise TaxonomyError("sources.yaml: 'sources' must be a non-empty list")
    sources: list[SourceDef] = []
    for item in raw:
        try:
            sources.append(SourceDef.model_validate(item))
        except Exception as exc:
            raise TaxonomyError(f"invalid source entry {item!r}: {exc}") from exc
    return sources


def load_taxonomy(taxonomy_dir: Path | None = None) -> Taxonomy:
    """Load the taxonomy from disk. Defaults to the configured taxonomy dir."""
    taxonomy_dir = taxonomy_dir or get_settings().taxonomy_dir
    attributes = _load_attributes(taxonomy_dir)
    attribute_synonyms, value_synonyms = _load_synonyms(taxonomy_dir)
    sources = _load_sources(taxonomy_dir)
    return Taxonomy(attributes, attribute_synonyms, value_synonyms, sources)


@lru_cache(maxsize=1)
def get_taxonomy() -> Taxonomy:
    """Cached default taxonomy for app/runtime use."""
    return load_taxonomy()
