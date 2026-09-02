import type { SpecField } from "@/types";

const nf = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });

/** Format a number in pt-BR, trimming pointless trailing zeros (397, 5,8, 9,55). */
export function formatNumber(value: number): string {
  return nf.format(value);
}

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

/** Tire-shaped DIMENSIONAL value → "285/70 R17". */
function formatTire(v: Record<string, unknown>): string | null {
  const { width, aspect_ratio, rim_diameter_in } = v;
  if (width != null && aspect_ratio != null && rim_diameter_in != null) {
    return `${width}/${aspect_ratio} R${rim_diameter_in}`;
  }
  return null;
}

/** Engine-shaped COMPOSITE value → "V6 · 3.0 L · Biturbo". */
function formatEngine(v: Record<string, unknown>): string | null {
  if (!("cylinders" in v || "displacement_l" in v || "aspiration" in v)) return null;
  const parts: string[] = [];
  if (v.layout && v.cylinders) parts.push(`${v.layout}${v.cylinders}`);
  else if (v.cylinders) parts.push(`${v.cylinders} cil.`);
  if (typeof v.displacement_l === "number") parts.push(`${formatNumber(v.displacement_l)} L`);
  if (v.aspiration) parts.push(String(v.aspiration));
  return parts.length ? parts.join(" · ") : null;
}

/** Transmission-shaped COMPOSITE value → "Automática · 10 marchas · Paddle shifters". */
function formatTransmission(v: Record<string, unknown>): string | null {
  if (!("gears" in v || "type" in v)) return null;
  const parts: string[] = [];
  if (v.type) parts.push(String(v.type));
  if (v.gears != null) parts.push(`${v.gears} marchas`);
  if (v.paddle_shifters === true) parts.push("Paddle shifters");
  return parts.length ? parts.join(" · ") : null;
}

function formatRecord(v: Record<string, unknown>): string {
  return (
    formatTire(v) ??
    formatEngine(v) ??
    formatTransmission(v) ??
    Object.values(v)
      .filter((x) => x !== null && x !== false && x !== "")
      .map((x) => (typeof x === "number" ? formatNumber(x) : String(x)))
      .join(" · ")
  );
}

/**
 * Render a field's normalized value as a display string. ENUM_LIST is handled
 * separately by the UI (rendered as chips); here it falls back to a join.
 */
export function formatValue(field: SpecField): string {
  const { value, data_type, unit } = field;

  if (value === null || value === undefined) return "—";

  switch (data_type) {
    case "SCALAR_UNIT": {
      const n = typeof value === "number" ? formatNumber(value) : String(value);
      return unit ? `${n} ${unit}` : n;
    }
    case "BOOLEAN":
      return value ? "Sim" : "Não";
    case "ENUM_LIST":
      return Array.isArray(value) ? value.join(", ") : String(value);
    case "COMPOSITE":
    case "DIMENSIONAL":
      return isRecord(value) ? formatRecord(value) : String(value);
    default:
      return String(value);
  }
}

/** True when a field carries a list to render as chips. */
export function asList(field: SpecField): string[] | null {
  return field.data_type === "ENUM_LIST" && Array.isArray(field.value)
    ? (field.value as string[])
    : null;
}

const tierNames: Record<number, string> = {
  1: "Montadora",
  2: "Referência oficial",
  3: "Agregador",
  4: "Editorial",
};

export function sourceTierLabel(tier: number | null): string {
  if (tier === null) return "—";
  return tierNames[tier] ?? `Tier ${tier}`;
}

export function hostnameOf(url: string | null): string | null {
  if (!url) return null;
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}
