// Modo offline: monta a ficha usando os dados embarcados no app.
// Segue as mesmas regras do backend: mesma lista de campos (ordem da taxonomia),
// atributo sem dado vira "NA" explícito e atributo desconhecido é informado.
import raptorSheet from '../data/raptor-sheet.json';
import taxonomyData from '../data/taxonomy.json';
import type { SpecField, SpecRequest, SpecSheet, TaxonomyAttribute } from '../types';

export const taxonomy: TaxonomyAttribute[] = taxonomyData.attributes;

// Igual ao fold() do backend: minúsculas, sem acento, espaços simples.
export function fold(text: string): string {
  return text
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ');
}

// Converte os rótulos livres digitados pelo usuário em ids da taxonomia.
export function resolveLabels(labels: string[]): { ids: string[] | null; unknown: string[] } {
  const cleaned = labels.map((l) => l.trim()).filter(Boolean);
  if (cleaned.length === 0) return { ids: null, unknown: [] }; // vazio = ficha completa

  const ids: string[] = [];
  const unknown: string[] = [];
  for (const label of cleaned) {
    const key = fold(label);
    const attr = taxonomy.find(
      (a) => a.id === label || a.synonyms.includes(key) || fold(a.name) === key,
    );
    if (!attr) unknown.push(label);
    else if (!ids.includes(attr.id)) ids.push(attr.id);
  }
  return { ids, unknown };
}

function emptyField(attr: TaxonomyAttribute): SpecField {
  return {
    attribute_id: attr.id,
    name: attr.name,
    group: attr.group,
    data_type: attr.data_type,
    value: null,
    value_raw: null,
    unit: null,
    status: 'NA',
    confidence: 0,
    source_url: null,
    source_tier: null,
    evidence_snippet: null,
    note: null,
    alternatives: [],
  };
}

function isRaptor(request: SpecRequest): boolean {
  return fold(request.make) === 'ford' && fold(request.model) === 'ranger raptor';
}

export function buildOfflineSheet(request: SpecRequest): SpecSheet {
  const { ids, unknown } = resolveLabels(request.attributes);
  const hasData = isRaptor(request);
  const known = new Map<string, SpecField>();
  if (hasData) {
    for (const f of raptorSheet.fields as SpecField[]) known.set(f.attribute_id, f);
  }

  const attributes = ids === null ? taxonomy : taxonomy.filter((a) => ids.includes(a.id));
  return {
    make: request.make.trim(),
    model: request.model.trim(),
    version: request.version.trim(),
    year: request.year,
    market: 'BR',
    generated_at: new Date().toISOString(),
    source_count: hasData ? raptorSheet.source_count : 0,
    mode: 'offline',
    unknown_attributes: unknown,
    fields: attributes.map((a) => known.get(a.id) ?? emptyField(a)),
  };
}
