from __future__ import annotations

from specradar.normalization.categorical import normalize_categorical, normalize_enum_list
from specradar.taxonomy.loader import Taxonomy


def test_drivetrain_synonyms(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("drivetrain")
    assert normalize_categorical(attr, "4x4", taxonomy) == "4WD"
    assert normalize_categorical(attr, "tração nas quatro rodas", taxonomy) == "4WD"
    assert normalize_categorical(attr, "AWD", taxonomy) == "AWD"


def test_categorical_direct_value_set_match(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("headlights")
    assert normalize_categorical(attr, "matrix led", taxonomy) == "Matrix LED"


def test_categorical_unmappable_returns_none(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("drivetrain")
    assert normalize_categorical(attr, "tração lunar", taxonomy) is None


def test_enum_list_drive_modes(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("drive_modes")
    result = normalize_enum_list(
        attr, "Normal, Sport, Slippery, Mud, Sand, Rock Crawl, Baja", taxonomy
    )
    assert result == ["Normal", "Sport", "Slippery", "Mud", "Sand", "Rock Crawl", "Baja"]


def test_enum_list_pt_tokens_and_dedup(taxonomy: Taxonomy) -> None:
    attr = taxonomy.get("drive_modes")
    result = normalize_enum_list(attr, "Normal, esportivo, areia, areia", taxonomy)
    assert result == ["Normal", "Sport", "Sand"]
