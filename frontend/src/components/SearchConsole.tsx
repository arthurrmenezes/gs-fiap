import { ArrowRight, Search, Sparkle } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { cn } from "@/lib/utils";
import type { SpecRequest } from "@/types";

interface Example {
  label: string;
  req: SpecRequest;
  demo?: boolean;
}

const EXAMPLES: Example[] = [
  {
    label: "Ford Ranger Raptor",
    req: { make: "Ford", model: "Ranger Raptor", version: "Raptor 3.0 V6", year: 2026 },
    demo: true,
  },
  {
    label: "Toyota Hilux GR-Sport",
    req: { make: "Toyota", model: "Hilux", version: "GR-Sport", year: 2026 },
  },
  {
    label: "Chevrolet S10 High Country",
    req: { make: "Chevrolet", model: "S10", version: "High Country", year: 2026 },
  },
];

interface Props {
  onSubmit: (req: SpecRequest) => void;
  loading: boolean;
}

export function SearchConsole({ onSubmit, loading }: Props) {
  const [form, setForm] = useState<SpecRequest>({
    make: "Ford",
    model: "Ranger Raptor",
    version: "Raptor 3.0 V6",
    year: 2026,
  });

  const set = (key: keyof SpecRequest) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.make.trim() || !form.model.trim()) return;
    onSubmit({ ...form, version: form.version || form.model });
  };

  const canSubmit = form.make.trim() && form.model.trim() && !loading;

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center gap-3 border-b border-graphite-100 px-6 py-4">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-ford-50 text-ford-600">
          <Search className="h-[18px] w-[18px]" />
        </span>
        <div>
          <h2 className="text-[15px] font-bold text-graphite-900">Consultar ficha técnica</h2>
          <p className="text-xs text-graphite-500">
            Marca, modelo e versão — a ficha volta sempre no mesmo formato, comparável e auditável.
          </p>
        </div>
      </div>

      <form onSubmit={submit} className="p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-[1fr_1.2fr_1.2fr_0.7fr]">
          <Input label="Marca" name="make" value={form.make} onChange={set("make")} placeholder="Ford" />
          <Input
            label="Modelo"
            name="model"
            value={form.model}
            onChange={set("model")}
            placeholder="Ranger Raptor"
          />
          <Input
            label="Versão"
            name="version"
            value={form.version}
            onChange={set("version")}
            placeholder="Raptor 3.0 V6"
          />
          <Input
            label="Ano-modelo"
            name="year"
            type="number"
            value={form.year ?? ""}
            onChange={(e) =>
              setForm((f) => ({ ...f, year: e.target.value ? Number(e.target.value) : null }))
            }
            placeholder="2026"
          />
        </div>

        <div className="mt-5 flex flex-col items-stretch justify-between gap-4 sm:flex-row sm:items-center">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-graphite-400">
              <Sparkle className="h-3.5 w-3.5" /> Exemplos
            </span>
            {EXAMPLES.map((ex) => (
              <button
                key={ex.label}
                type="button"
                onClick={() => setForm(ex.req)}
                className={cn(
                  "group inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
                  ex.demo
                    ? "border-ford-200 bg-ford-50 text-ford-700 hover:bg-ford-100"
                    : "border-graphite-200 bg-white text-graphite-600 hover:border-graphite-300 hover:bg-graphite-50",
                )}
              >
                {ex.label}
                {ex.demo ? (
                  <span className="rounded bg-ford-600 px-1.5 py-0.5 text-[10px] font-bold text-white">
                    DEMO
                  </span>
                ) : null}
              </button>
            ))}
          </div>

          <Button type="submit" variant="accent" size="lg" disabled={!canSubmit} className="sm:min-w-[190px]">
            {loading ? (
              <>
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                Analisando…
              </>
            ) : (
              <>
                Gerar ficha
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </form>
    </Card>
  );
}
