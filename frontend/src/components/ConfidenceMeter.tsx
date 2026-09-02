import { cn } from "@/lib/utils";

/** Compact 5-segment confidence meter. Reads as an instrument gauge, not a %. */
export function ConfidenceMeter({ value }: { value: number }) {
  const filled = Math.round(value * 5);
  const tone =
    value >= 0.8 ? "bg-signal-ok" : value >= 0.5 ? "bg-ford-500" : "bg-signal-conflict";

  return (
    <div className="flex items-center gap-2" title={`Confiança ${Math.round(value * 100)}%`}>
      <div className="flex gap-0.5">
        {Array.from({ length: 5 }).map((_, i) => (
          <span
            key={i}
            className={cn(
              "h-3.5 w-1 rounded-sm",
              i < filled ? tone : "bg-graphite-200",
            )}
          />
        ))}
      </div>
      <span className="tnum text-xs font-medium text-graphite-500">
        {Math.round(value * 100)}%
      </span>
    </div>
  );
}
