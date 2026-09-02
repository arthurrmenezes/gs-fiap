// Mirrors the FastAPI contract (specradar.api.schemas).

export type SpecStatus = "OK" | "CONFLICT" | "ANOMALY" | "NA" | "LOW_CONFIDENCE";

export type DataType =
  | "SCALAR_UNIT"
  | "CATEGORICAL"
  | "COMPOSITE"
  | "DIMENSIONAL"
  | "ENUM_LIST"
  | "BOOLEAN"
  | "TEXT";

export interface SpecField {
  attribute_id: string;
  name: string;
  group: string;
  data_type: DataType;
  value: unknown; // number | string | boolean | string[] | Record<string, unknown> | null
  value_raw: string | null;
  unit: string | null;
  status: SpecStatus;
  confidence: number;
  source_url: string | null;
  source_tier: number | null;
  evidence_snippet: string | null;
  note: string | null;
  alternatives: unknown[];
}

export interface SpecSheet {
  make: string;
  model: string;
  version: string;
  year: number | null;
  market: string;
  generated_at: string;
  source_count: number;
  fields: SpecField[];
}

export interface SpecRequest {
  make: string;
  model: string;
  version: string;
  year?: number | null;
  market?: string;
  attributes?: string[];
}

export interface AttributeDef {
  id: string;
  name: string;
  group: string;
  data_type: DataType;
  canonical_unit: string | null;
  value_set: string[] | null;
}

export interface SourceDef {
  domain: string;
  authority_tier: number;
  kind: string;
}

export interface TaxonomyResponse {
  attributes: AttributeDef[];
  sources: SourceDef[];
}
