import {
  CircleDot,
  Cog,
  type LucideIcon,
  Gauge,
  Leaf,
  Lightbulb,
  MonitorSmartphone,
  Mountain,
  Ruler,
  ShieldCheck,
  SlidersHorizontal,
  Sofa,
  Tag,
  Timer,
  Wrench,
} from "lucide-react";
import type { SpecStatus } from "@/types";

export interface StatusMeta {
  label: string;
  text: string;
  bg: string;
  dot: string;
}

/** Visual + copy metadata per reconciliation status. */
export const STATUS: Record<SpecStatus, StatusMeta> = {
  OK: { label: "Confirmado", text: "text-signal-ok", bg: "bg-signal-okbg", dot: "bg-signal-ok" },
  CONFLICT: {
    label: "Conflito",
    text: "text-signal-conflict",
    bg: "bg-signal-conflictbg",
    dot: "bg-signal-conflict",
  },
  ANOMALY: {
    label: "Anomalia",
    text: "text-signal-anomaly",
    bg: "bg-signal-anomalybg",
    dot: "bg-signal-anomaly",
  },
  NA: { label: "Não encontrado", text: "text-signal-na", bg: "bg-signal-nabg", dot: "bg-signal-na" },
  LOW_CONFIDENCE: {
    label: "Baixa confiança",
    text: "text-signal-low",
    bg: "bg-signal-lowbg",
    dot: "bg-signal-low",
  },
};

export interface GroupMeta {
  label: string;
  order: number;
  icon: LucideIcon;
}

/** PT-BR labels, display order, and icon per taxonomy group. */
export const GROUPS: Record<string, GroupMeta> = {
  powertrain: { label: "Motorização", order: 1, icon: Cog },
  performance: { label: "Desempenho", order: 2, icon: Timer },
  dynamics: { label: "Dinâmica", order: 3, icon: SlidersHorizontal },
  efficiency: { label: "Eficiência", order: 4, icon: Leaf },
  chassis: { label: "Chassi e suspensão", order: 5, icon: Wrench },
  wheels: { label: "Rodas e pneus", order: 6, icon: CircleDot },
  dimensions: { label: "Dimensões e capacidade", order: 7, icon: Ruler },
  offroad: { label: "Off-road", order: 8, icon: Mountain },
  safety: { label: "Segurança", order: 9, icon: ShieldCheck },
  technology: { label: "Tecnologia e multimídia", order: 10, icon: MonitorSmartphone },
  lighting: { label: "Iluminação", order: 11, icon: Lightbulb },
  comfort: { label: "Conforto", order: 12, icon: Sofa },
  commercial: { label: "Comercial", order: 13, icon: Tag },
};

export function groupMeta(group: string): GroupMeta {
  return GROUPS[group] ?? { label: group, order: 99, icon: Gauge };
}
