export type SpecStatus = 'OK' | 'CONFLICT' | 'ANOMALY' | 'NA' | 'LOW_CONFIDENCE';

export type SpecValue = string | number | boolean | string[] | Record<string, unknown> | null;

export interface SpecField {
  attribute_id: string;
  name: string;
  group: string;
  data_type: string;
  value: SpecValue;
  value_raw: string | null;
  unit: string | null;
  status: SpecStatus;
  confidence: number;
  source_url: string | null;
  source_tier: number | null;
  evidence_snippet: string | null;
  note: string | null;
  alternatives: SpecValue[];
}

export type SheetMode = 'live' | 'demo' | 'offline';

export interface SpecSheet {
  make: string;
  model: string;
  version: string;
  year: number | null;
  market: string;
  generated_at: string;
  source_count: number;
  mode: SheetMode;
  unknown_attributes: string[];
  fields: SpecField[];
}

export interface SpecRequest {
  make: string;
  model: string;
  version: string;
  year: number | null;
  attributes: string[];
}

export interface HistoryEntry {
  id: string;
  createdAt: string;
  request: SpecRequest;
  sheet: SpecSheet;
  notice?: string;
}

export interface AppSettings {
  useApi: boolean;
  apiUrl: string;
}

export interface TaxonomyAttribute {
  id: string;
  name: string;
  group: string;
  data_type: string;
  canonical_unit: string | null;
  synonyms: string[];
}
