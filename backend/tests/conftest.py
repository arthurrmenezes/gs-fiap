"""Shared test fixtures. No network in unit tests (CLAUDE.md §11)."""

from __future__ import annotations

from pathlib import Path

import pytest

from specradar.taxonomy.loader import Taxonomy, load_taxonomy

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = REPO_ROOT / "examples"
GOLDEN_DIR = Path(__file__).resolve().parent / "golden"


@pytest.fixture(scope="session")
def taxonomy() -> Taxonomy:
    """The real project taxonomy (loaded from taxonomy/*.yaml)."""
    return load_taxonomy(REPO_ROOT / "taxonomy")


@pytest.fixture(scope="session")
def raptor_fixture_dir() -> Path:
    return EXAMPLES / "ranger_raptor"
