from __future__ import annotations

from typing import Any

from specradar.taxonomy.models import AttributeDef

SYSTEM_PROMPT = """\
You are a meticulous automotive spec extractor. You READ source documents and \
CITE them. You NEVER invent, infer, calculate, or guess a value.

Hard rules:
1. For every requested attribute, return an object with exactly:
   attribute_id, value_raw, evidence_snippet, confidence (0..1), found (bool).
2. `evidence_snippet` MUST be copied VERBATIM from the document — a literal, \
contiguous substring. Do not paraphrase, translate, fix typos, or merge lines.
3. If the attribute is not stated in the document, set found=false, \
value_raw=null, evidence_snippet=null. Do NOT infer from related facts.
4. `value_raw` is the raw value as written in the source (keep its units/words). \
Do NOT convert units, normalize synonyms, or reconcile — that happens downstream.
5. Lower your confidence when the wording is ambiguous or indirect.
"""

_TOOL_NAME = "report_specs"


def build_tool_schema(attributes: list[AttributeDef]) -> dict[str, Any]:
    allowed_ids = [a.id for a in attributes]
    item_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["attribute_id", "value_raw", "evidence_snippet", "confidence", "found"],
        "properties": {
            "attribute_id": {"type": "string", "enum": allowed_ids},
            "value_raw": {"type": ["string", "null"]},
            "evidence_snippet": {"type": ["string", "null"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "found": {"type": "boolean"},
        },
    }
    return {
        "name": _TOOL_NAME,
        "description": "Report the extracted spec values, one entry per requested attribute.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["values"],
            "properties": {"values": {"type": "array", "items": item_schema}},
        },
    }


def tool_name() -> str:
    return _TOOL_NAME


def build_user_prompt(attributes: list[AttributeDef], document_text: str) -> str:
    lines = ["Extract these attributes from the document below.\n", "Attributes:"]
    for a in attributes:
        hint = f" (unit: {a.canonical_unit})" if a.canonical_unit else ""
        allowed = f" allowed: {list(a.value_set)}" if a.value_set else ""
        lines.append(f"- {a.id} — {a.name} [{a.data_type.value}]{hint}{allowed}")
    lines.append("\n--- DOCUMENT START ---")
    lines.append(document_text)
    lines.append("--- DOCUMENT END ---")
    return "\n".join(lines)
