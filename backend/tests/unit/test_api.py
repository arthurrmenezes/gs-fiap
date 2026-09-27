"""API contract test — offline path (no keys → bundled Raptor fixture)."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from specradar.api.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}


def test_taxonomy_endpoint(client: TestClient) -> None:
    data = client.get("/api/taxonomy").json()
    assert len(data["attributes"]) >= 35
    assert any(s["authority_tier"] == 1 for s in data["sources"])


def test_spec_sheet_offline_fixture(client: TestClient) -> None:
    resp = client.post(
        "/api/spec",
        json={"make": "Ford", "model": "Ranger Raptor", "version": "Raptor 3.0 V6", "year": 2026},
    )
    assert resp.status_code == 200
    body = resp.json()
    fields = {f["attribute_id"]: f for f in body["fields"]}
    assert fields["engine.power_cv"]["value"] == 397.0
    assert fields["price.brl"]["status"] == "ANOMALY"
    assert fields["emissions.co2_gkm"]["status"] == "NA"


def test_spec_sheet_unknown_vehicle_returns_same_format_all_na(client: TestClient) -> None:
    """A vehicle with no data still gets the full sheet, every field explicit NA."""
    raptor = client.post(
        "/api/spec", json={"make": "Ford", "model": "Ranger Raptor", "version": "Raptor"}
    ).json()
    resp = client.post("/api/spec", json={"make": "Tesla", "model": "Cybertruck", "version": "AWD"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["source_count"] == 0
    assert [f["attribute_id"] for f in body["fields"]] == [
        f["attribute_id"] for f in raptor["fields"]
    ]
    assert all(f["status"] == "NA" and f["value"] is None for f in body["fields"])


def test_spec_sheet_filters_attributes_and_reports_unknown(client: TestClient) -> None:
    resp = client.post(
        "/api/spec",
        json={
            "make": "Ford",
            "model": "Ranger Raptor",
            "version": "Raptor",
            "attributes": ["potência", "Tração", "cor do banco"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert [f["attribute_id"] for f in body["fields"]] == ["engine.power_cv", "drivetrain"]
    assert body["unknown_attributes"] == ["cor do banco"]
    assert body["mode"] == "demo"
