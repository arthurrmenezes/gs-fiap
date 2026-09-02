import { STATUS } from "@/lib/domain";
import { cn } from "@/lib/utils";
import type { SpecStatus } from "@/types";

export function StatusBadge({
  status,
  className,
}: {
  status: SpecStatus;
  className?: string;
}) {
  const meta = STATUS[status];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold",
        meta.bg,
        meta.text,
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", meta.dot)} />
      {meta.label}
    </span>
  );
}
