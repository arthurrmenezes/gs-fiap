import { ExternalLink, Quote, ShieldQuestion } from "lucide-react";
import { ConfidenceMeter } from "@/components/ConfidenceMeter";
import { StatusBadge } from "@/components/StatusBadge";
import { Popover } from "@/components/ui/Popover";
import { asList, formatValue, hostnameOf, sourceTierLabel } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { SpecField } from "@/types";

export function SpecRow({ field }: { field: SpecField }) {
  const isNA = field.status === "NA";
  const list = asList(field);
  const host = hostnameOf(field.source_url);
  const isHttp = !!field.source_url?.startsWith("http");

  return (
    <div
      className={cn(
        "grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-2 px-6 py-3.5 sm:grid-cols-[minmax(0,1.1fr)_minmax(0,1.3fr)_auto]",
        isNA && "opacity-60",
      )}
    >
      {/* Attribute name */}
      <div className="min-w-0">
        <div className="truncate text-sm font-semibold text-graphite-800">{field.name}</div>
        {field.note ? (
          <div className="mt-0.5 truncate text-xs text-graphite-400">{field.note}</div>
        ) : (
          <div className="mt-0.5 font-mono text-[11px] text-graphite-400">{field.attribute_id}</div>
        )}
      </div>

      {/* Value */}
      <div className="col-span-2 sm:col-span-1 sm:order-none order-3">
        {isNA ? (
          <span className="text-sm text-graphite-400">Não informado</span>
        ) : list ? (
          <div className="flex flex-wrap gap-1.5">
            {list.map((item) => (
              <span
                key={item}
                className="rounded-md bg-graphite-100 px-2 py-0.5 text-xs font-medium text-graphite-700"
              >
                {item}
              </span>
            ))}
          </div>
        ) : (
          <span className="tnum text-[15px] font-semibold text-graphite-900">
            {formatValue(field)}
          </span>
        )}
      </div>

      {/* Meta: status + confidence + provenance */}
      <div className="flex items-center justify-end gap-3">
        {!isNA && <ConfidenceMeter value={field.confidence} />}
        <StatusBadge status={field.status} />
        {!isNA && (field.evidence_snippet || field.source_url) ? (
          <Provenance field={field} host={host} isHttp={isHttp} />
        ) : (
          <span className="h-7 w-7" />
        )}
      </div>
    </div>
  );
}

function Provenance({
  field,
  host,
  isHttp,
}: {
  field: SpecField;
  host: string | null;
  isHttp: boolean;
}) {
  return (
    <Popover
      trigger={
        <button
          className="flex h-7 w-7 items-center justify-center rounded-md text-graphite-400 transition-colors hover:bg-graphite-100 hover:text-ford-600"
          aria-label="Ver proveniência e evidência"
        >
          <Quote className="h-4 w-4" />
        </button>
      }
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wide text-graphite-500">
            Proveniência
          </span>
          <span className="rounded-full bg-ford-50 px-2 py-0.5 text-[11px] font-semibold text-ford-700">
            {sourceTierLabel(field.source_tier)}
          </span>
        </div>

        {field.evidence_snippet ? (
          <figure className="rounded-lg border border-graphite-200 bg-graphite-50 p-3">
            <figcaption className="mb-1 flex items-center gap-1 text-[11px] font-medium text-graphite-400">
              <ShieldQuestion className="h-3.5 w-3.5" /> Evidência verificada na fonte
            </figcaption>
            <blockquote className="text-xs leading-relaxed text-graphite-700">
              “{field.evidence_snippet}”
            </blockquote>
          </figure>
        ) : null}

        {field.value_raw ? (
          <div className="flex items-center justify-between text-xs">
            <span className="text-graphite-400">Valor bruto</span>
            <span className="font-mono text-graphite-700">{field.value_raw}</span>
          </div>
        ) : null}

        {host ? (
          <div className="flex items-center justify-between gap-2 border-t border-graphite-100 pt-3">
            <span className="truncate text-xs text-graphite-500">{host}</span>
            {isHttp ? (
              <a
                href={field.source_url!}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs font-semibold text-ford-600 hover:text-ford-700"
              >
                Abrir fonte <ExternalLink className="h-3.5 w-3.5" />
              </a>
            ) : null}
          </div>
        ) : null}
      </div>
    </Popover>
  );
}
