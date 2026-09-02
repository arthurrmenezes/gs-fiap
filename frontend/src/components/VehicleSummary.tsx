import { AlertTriangle, CircleAlert, Database, FileCheck2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import type { SpecSheet } from "@/types";

export function VehicleSummary({ sheet }: { sheet: SpecSheet }) {
  const total = sheet.fields.length;
  const found = sheet.fields.filter((f) => f.status !== "NA").length;
  const conflicts = sheet.fields.filter((f) => f.status === "CONFLICT").length;
  const anomalies = sheet.fields.filter((f) => f.status === "ANOMALY").length;
  const completeness = total ? Math.round((found / total) * 100) : 0;

  const generated = new Date(sheet.generated_at).toLocaleString("pt-BR", {
    dateStyle: "medium",
    timeStyle: "short",
  });

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-col gap-6 p-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-ford-600">
            <span className="rounded bg-ford-50 px-2 py-0.5">{sheet.make}</span>
            <span className="text-graphite-300">/</span>
            <span className="text-graphite-500">{sheet.market}</span>
          </div>
          <h1 className="mt-1.5 truncate text-2xl font-extrabold tracking-brand text-graphite-900">
            {sheet.model}
          </h1>
          <p className="mt-0.5 text-sm text-graphite-500">
            {sheet.version}
            {sheet.year ? ` · ${sheet.year}` : ""} · ficha gerada {generated}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-graphite-200 bg-graphite-200 sm:grid-cols-4">
          <Kpi icon={Database} label="Fontes" value={sheet.source_count} tone="neutral" />
          <Kpi icon={FileCheck2} label="Cobertura" value={`${completeness}%`} tone="ford" />
          <Kpi
            icon={CircleAlert}
            label="Conflitos"
            value={conflicts}
            tone={conflicts ? "conflict" : "neutral"}
          />
          <Kpi
            icon={AlertTriangle}
            label="Anomalias"
            value={anomalies}
            tone={anomalies ? "anomaly" : "neutral"}
          />
        </div>
      </div>
    </Card>
  );
}

const TONE = {
  neutral: { icon: "text-graphite-400", value: "text-graphite-900" },
  ford: { icon: "text-ford-500", value: "text-ford-700" },
  conflict: { icon: "text-signal-conflict", value: "text-signal-conflict" },
  anomaly: { icon: "text-signal-anomaly", value: "text-signal-anomaly" },
} as const;

function Kpi({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: typeof Database;
  label: string;
  value: string | number;
  tone: keyof typeof TONE;
}) {
  const t = TONE[tone];
  return (
    <div className="flex min-w-[120px] flex-col gap-1 bg-white px-4 py-3.5">
      <div className="flex items-center gap-1.5 text-xs font-medium text-graphite-500">
        <Icon className={cn("h-3.5 w-3.5", t.icon)} />
        {label}
      </div>
      <div className={cn("tnum text-2xl font-bold leading-none", t.value)}>{value}</div>
    </div>
  );
}
