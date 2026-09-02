"""SQL for the pivoted spec-sheet view — the standardized output (CLAUDE.md §6).

The "always the same format" sheet is a VIEW, not a wide table. It pivots the
long `fact_spec` using the taxonomy (dim_attribute) as its spine, so a new
attribute never changes the physical schema. Gaps surface as explicit NA.
"""

from __future__ import annotations


def spec_sheet_view_sql(project: str, dataset: str) -> str:
    """DDL for `curated.v_spec_sheet`: one row per (vehicle × attribute), pivoted.

    The view is long-by-attribute (taxonomy-driven), so adding attributes to the
    taxonomy automatically extends the sheet with no DDL change. The Looker
    dashboard pivots vehicle→columns on top of this.
    """
    fq = f"`{project}.{dataset}`"
    return f"""\
CREATE OR REPLACE VIEW {fq}.v_spec_sheet AS
SELECT
  v.vehicle_id,
  v.make,
  v.model,
  v.version,
  v.model_year,
  v.market,
  a.attribute_id,
  a.name        AS attribute_name,
  a.`group`     AS attribute_group,
  a.data_type,
  a.canonical_unit,
  f.value_raw,
  f.value_norm,
  COALESCE(f.unit, a.canonical_unit) AS unit,
  -- Absence is explicit: an attribute with no fact row reads as NA, never omitted.
  COALESCE(f.status, 'NA')           AS status,
  f.confidence,
  f.source_url,
  f.source_tier,
  f.evidence_snippet,
  f.note,
  f.reconciled_at
FROM {fq}.dim_vehicle AS v
CROSS JOIN {fq}.dim_attribute AS a
LEFT JOIN {fq}.fact_spec AS f
  ON f.vehicle_id = v.vehicle_id
 AND f.attribute_id = a.attribute_id
ORDER BY v.vehicle_id, a.`group`, a.attribute_id;
"""


def spec_diff_view_sql(project: str, dataset: str, baseline_make: str = "Ford") -> str:
    """DDL for `curated.v_spec_diff`: each vehicle's specs side-by-side vs Ford.

    Powers the Looker "spec diff vs Ford" — highlights where a competitor leads
    or trails the Ford baseline for the same attribute.
    """
    fq = f"`{project}.{dataset}`"
    return f"""\
CREATE OR REPLACE VIEW {fq}.v_spec_diff AS
WITH sheet AS (
  SELECT * FROM {fq}.v_spec_sheet
),
ford AS (
  SELECT attribute_id, value_norm AS ford_value_norm, value_raw AS ford_value_raw
  FROM sheet
  WHERE make = '{baseline_make}'
)
SELECT
  s.make, s.model, s.version, s.model_year,
  s.attribute_id, s.attribute_name, s.attribute_group, s.data_type, s.unit,
  s.value_raw      AS competitor_value_raw,
  s.value_norm     AS competitor_value_norm,
  f.ford_value_raw,
  f.ford_value_norm,
  CASE
    WHEN f.ford_value_norm IS NULL THEN 'NO_FORD_BASELINE'
    WHEN s.value_norm = f.ford_value_norm THEN 'SAME'
    ELSE 'DIFF'
  END AS comparison
FROM sheet s
LEFT JOIN ford f USING (attribute_id)
WHERE s.make != '{baseline_make}'
ORDER BY s.make, s.model, s.attribute_group, s.attribute_id;
"""
