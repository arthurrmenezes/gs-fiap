"""Resolve a vehicle query to candidate source URLs, restricted to the allowlist.

Discovery uses a search client (SerpAPI / Google CSE) when configured; results
are filtered to allowlisted domains and ordered by authority tier. A URL whose
domain is not allowlisted is never returned.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse

from specradar.logging import get_logger
from specradar.models import VehicleKey
from specradar.taxonomy.loader import Taxonomy

log = get_logger("resolver")


@dataclass(frozen=True)
class SourceCandidate:
    url: str
    domain: str
    authority_tier: int
    kind: str


class SearchClient(Protocol):
    """Returns candidate URLs for a query string (most relevant first)."""

    def search(self, query: str, *, num: int = 10) -> list[str]: ...


def build_query(vehicle: VehicleKey) -> str:
    """Build the discovery query for a vehicle version."""
    parts = [vehicle.make, vehicle.model, vehicle.version, "ficha técnica especificações"]
    if vehicle.model_year is not None:
        parts.insert(3, str(vehicle.model_year))
    return " ".join(p for p in parts if p)


def _domain_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def resolve_sources(
    vehicle: VehicleKey,
    taxonomy: Taxonomy,
    search_client: SearchClient,
    *,
    max_candidates: int = 8,
) -> list[SourceCandidate]:
    """Discover candidate URLs and filter/rank them by allowlist authority.

    Deduplicates by domain (one best URL per domain), keeps only allowlisted
    domains, and sorts by authority tier (tier 1 first).
    """
    query = build_query(vehicle)
    urls = search_client.search(query, num=max_candidates * 3)

    best_per_domain: dict[str, SourceCandidate] = {}
    for url in urls:
        domain = _domain_of(url)
        source = taxonomy.source_for_domain(domain)
        if source is None:
            log.info("rejected_offlist", url=url, domain=domain)
            continue
        if source.domain in best_per_domain:
            continue  # keep the first (most relevant) URL for that domain
        best_per_domain[source.domain] = SourceCandidate(
            url=url,
            domain=source.domain,
            authority_tier=source.authority_tier,
            kind=source.kind,
        )

    candidates = sorted(best_per_domain.values(), key=lambda c: c.authority_tier)
    log.info("resolved_sources", vehicle=vehicle.slug(), count=len(candidates))
    return candidates[:max_candidates]
