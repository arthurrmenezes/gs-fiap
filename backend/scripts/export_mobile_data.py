from __future__ import annotations

import json
from datetime import UTC, datetime

import yaml

from specradar.api.runner import run_for_request
from specradar.api.sheet import build_spec_sheet
from specradar.config import REPO_ROOT, Settings
from specradar.models import VehicleKey
from specradar.taxonomy.loader import load_taxonomy
from specradar.textutil import fold

OUT_DIR = REPO_ROOT.parent / "mobile" / "src" / "data"


def main() -> None:
    tax = load_taxonomy(REPO_ROOT / "taxonomy")

    synonyms_path = REPO_ROOT / "taxonomy" / "synonyms.yaml"
    raw_synonyms = yaml.safe_load(synonyms_path.read_text(encoding="utf-8"))["attributes"]
    labels: dict[str, list[str]] = {}
    for label, attr_id in raw_synonyms.items():
        labels.setdefault(str(attr_id), []).append(fold(str(label)))

    attributes = [
        {
            "id": a.id,
            "name": a.name,
            "group": a.group,
            "data_type": a.data_type.value,
            "canonical_unit": a.canonical_unit,
            "synonyms": labels.get(a.id, []),
        }
        for a in tax.all_attributes()
    ]

    vehicle = VehicleKey(
        make="Ford", model="Ranger Raptor", version="Raptor 3.0 V6", model_year=2026
    )
    run = run_for_request(vehicle, None, Settings(ANTHROPIC_API_KEY="", SEARCH_API_KEY=""), tax)
    sheet = build_spec_sheet(
        vehicle,
        run.result.specs,
        tax,
        run.result.document_count,
        mode="demo",
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "taxonomy.json").write_text(
        json.dumps({"attributes": attributes}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "raptor-sheet.json").write_text(
        sheet.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"exported {len(attributes)} attributes + Raptor sheet to {OUT_DIR}")


if __name__ == "__main__":
    main()
