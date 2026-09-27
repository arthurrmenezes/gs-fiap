// Funções de formatação usadas nas telas (valores, datas, grupos).
import type { SheetMode, SpecField, SpecSheet, SpecValue } from '../types';

export const NOT_AVAILABLE = 'Não disponível';

// Nome amigável de cada grupo da taxonomia.
const GROUP_LABELS: Record<string, string> = {
  powertrain: 'Motor e transmissão',
  dynamics: 'Modos de condução',
  performance: 'Desempenho',
  efficiency: 'Consumo e emissões',
  chassis: 'Suspensão e freios',
  wheels: 'Rodas e pneus',
  dimensions: 'Dimensões e capacidades',
  lighting: 'Iluminação',
  technology: 'Tecnologia',
  safety: 'Segurança',
  comfort: 'Conforto',
  offroad: 'Off-road',
  commercial: 'Preço e garantia',
};

// Como cada unidade canônica aparece na tela.
const UNIT_LABELS: Record<string, string> = {
  gears: 'marchas',
  seats: 'lugares',
  years: 'anos',
  airbags: 'airbags',
  in: '"',
};

// Nomes dos sub-campos dos tipos compostos (motor, câmbio, pneu).
export const SUBFIELD_LABELS: Record<string, string> = {
  layout: 'Arranjo',
  cylinders: 'Cilindros',
  displacement_l: 'Cilindrada (L)',
  aspiration: 'Aspiração',
  type: 'Tipo',
  gears: 'Marchas',
  paddle_shifters: 'Paddle shifters',
  width: 'Largura (mm)',
  aspect_ratio: 'Perfil (%)',
  rim_diameter_in: 'Aro (pol.)',
};

const TIER_LABELS: Record<number, string> = {
  1: 'Nível 1 · site oficial da montadora',
  2: 'Nível 2 · referência oficial (FIPE / Inmetro)',
  3: 'Nível 3 · portal agregador',
  4: 'Nível 4 · reportagem / review',
};

const MODE_LABELS: Record<SheetMode, string> = {
  live: 'Busca ao vivo (IA)',
  demo: 'Servidor · demonstração',
  offline: 'Offline · dados do app',
};

export function groupLabel(group: string): string {
  return GROUP_LABELS[group] ?? group;
}

export function tierLabel(tier: number | null): string {
  if (tier === null) return NOT_AVAILABLE;
  return TIER_LABELS[tier] ?? `Nível ${tier}`;
}

export function modeLabel(mode: SheetMode): string {
  return MODE_LABELS[mode] ?? mode;
}

// Formata número no padrão brasileiro: 1234.5 -> "1.234,5"
export function formatNumber(value: number): string {
  const rounded = Math.round(value * 100) / 100;
  const [intPart, decPart] = rounded.toFixed(2).replace(/0+$/, '').replace(/\.$/, '').split('.');
  const withDots = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return decPart ? `${withDots},${decPart}` : withDots;
}

function formatObject(obj: Record<string, unknown>): string {
  // Pneu: 285/70 R17
  if ('width' in obj && 'aspect_ratio' in obj && 'rim_diameter_in' in obj) {
    return `${obj.width}/${obj.aspect_ratio} R${obj.rim_diameter_in}`;
  }
  // Motor: V6 3.0 L Biturbo
  if ('cylinders' in obj) {
    const layout = obj.layout ? `${obj.layout}${obj.cylinders ?? ''}` : `${obj.cylinders} cil.`;
    const displacement =
      typeof obj.displacement_l === 'number' ? `${obj.displacement_l.toFixed(1)} L` : '';
    return [layout, displacement, obj.aspiration].filter(Boolean).join(' ');
  }
  // Câmbio: Automática · 10 marchas · paddle shifters
  if ('gears' in obj || 'type' in obj) {
    return [
      obj.type,
      obj.gears ? `${obj.gears} marchas` : null,
      obj.paddle_shifters ? 'paddle shifters' : null,
    ]
      .filter(Boolean)
      .join(' · ');
  }
  return Object.entries(obj)
    .map(([key, v]) => `${SUBFIELD_LABELS[key] ?? key}: ${String(v)}`)
    .join(' · ');
}

export function formatValue(value: SpecValue, unit: string | null): string {
  if (value === null || value === undefined) return NOT_AVAILABLE;
  if (typeof value === 'boolean') return value ? 'Sim' : 'Não';
  if (typeof value === 'number') {
    if (unit === 'BRL') return `R$ ${formatNumber(value)}`;
    if (!unit) return formatNumber(value);
    const label = UNIT_LABELS[unit] ?? unit;
    return label === '"' ? `${formatNumber(value)}"` : `${formatNumber(value)} ${label}`;
  }
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'object') return formatObject(value);
  return String(value);
}

export function formatField(field: SpecField): string {
  return formatValue(field.value, field.unit);
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function vehicleTitle(sheet: Pick<SpecSheet, 'make' | 'model'>): string {
  return `${sheet.make} ${sheet.model}`;
}

export function vehicleSubtitle(sheet: Pick<SpecSheet, 'version' | 'year'>): string {
  return sheet.year ? `${sheet.version} · ${sheet.year}` : sheet.version;
}

export function domainOf(url: string | null): string {
  if (!url) return NOT_AVAILABLE;
  const match = url.match(/^https?:\/\/(?:www\.)?([^/]+)/i);
  return match ? match[1] : url;
}

// Agrupa os campos pelo grupo, mantendo a ordem da taxonomia.
export function groupFields(fields: SpecField[]): { title: string; data: SpecField[] }[] {
  const sections: { title: string; data: SpecField[] }[] = [];
  const index = new Map<string, number>();
  for (const field of fields) {
    if (!index.has(field.group)) {
      index.set(field.group, sections.length);
      sections.push({ title: groupLabel(field.group), data: [] });
    }
    sections[index.get(field.group)!].data.push(field);
  }
  return sections;
}

export function countByStatus(fields: SpecField[]) {
  const found = fields.filter((f) => f.status === 'OK').length;
  const missing = fields.filter((f) => f.status === 'NA').length;
  return { found, missing, alerts: fields.length - found - missing, total: fields.length };
}

// Texto da ficha para compartilhar (WhatsApp, e-mail...).
export function sheetToText(sheet: SpecSheet): string {
  const lines = [
    `SpecRadar — ${vehicleTitle(sheet)} (${vehicleSubtitle(sheet)})`,
    `Gerado em ${formatDate(sheet.generated_at)} · ${sheet.source_count} fonte(s)`,
  ];
  for (const section of groupFields(sheet.fields)) {
    lines.push('', section.title.toUpperCase());
    for (const f of section.data) {
      const flag = f.status === 'OK' || f.status === 'NA' ? '' : ` [${f.status}]`;
      lines.push(`• ${f.name}: ${formatField(f)}${flag}`);
    }
  }
  return lines.join('\n');
}
