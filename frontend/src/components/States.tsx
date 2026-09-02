import { FileSearch, ServerCrash, ShieldCheck, Workflow } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { ApiError } from "@/lib/api";

const PILLARS = [
  {
    icon: ShieldCheck,
    title: "A IA lê, nunca inventa",
    body: "Cada valor é ancorado em evidência literal, verificada programaticamente contra a fonte.",
  },
  {
    icon: Workflow,
    title: "Sempre o mesmo formato",
    body: "Marca, modelo e versão entram; sai uma ficha padronizada, comparável entre qualquer veículo.",
  },
  {
    icon: FileSearch,
    title: "Tudo auditável",
    body: "Proveniência completa: fonte, tier de autoridade e confiança em cada especificação.",
  },
];

export function InitialState() {
  return (
    <Card className="overflow-hidden">
      <div className="border-b border-graphite-100 px-6 py-5">
        <h2 className="text-base font-bold text-graphite-900">
          Inteligência competitiva, sem busca manual
        </h2>
        <p className="mt-1 max-w-2xl text-sm text-graphite-500">
          O que levava ~1 hora por versão — vasculhar sites, vídeos e concessionárias — vira uma
          ficha técnica padronizada e auditável. Comece com o exemplo{" "}
          <span className="font-semibold text-ford-700">Ford Ranger Raptor</span> acima.
        </p>
      </div>
      <div className="grid grid-cols-1 divide-y divide-graphite-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0">
        {PILLARS.map((p) => (
          <div key={p.title} className="flex flex-col gap-2 p-6">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-ford-50 text-ford-600">
              <p.icon className="h-5 w-5" />
            </span>
            <h3 className="mt-1 text-sm font-bold text-graphite-900">{p.title}</h3>
            <p className="text-xs leading-relaxed text-graphite-500">{p.body}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

export function LoadingState() {
  return (
    <div className="space-y-5">
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="skeleton h-7 w-56 rounded-md" />
            <div className="skeleton h-4 w-72 rounded" />
          </div>
          <div className="skeleton h-16 w-72 rounded-xl" />
        </div>
      </Card>
      {[0, 1].map((s) => (
        <Card key={s} className="overflow-hidden">
          <div className="skeleton h-11 w-full" />
          <div className="divide-y divide-graphite-100">
            {[0, 1, 2, 3].map((r) => (
              <div key={r} className="flex items-center justify-between px-6 py-4">
                <div className="skeleton h-4 w-40 rounded" />
                <div className="skeleton h-4 w-24 rounded" />
                <div className="skeleton h-6 w-28 rounded-full" />
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}

export function ErrorState({ error }: { error: unknown }) {
  const is503 = error instanceof ApiError && error.status === 503;
  const message = error instanceof Error ? error.message : "Erro inesperado.";

  return (
    <Card className="flex flex-col items-center gap-3 px-6 py-12 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-signal-anomalybg text-signal-anomaly">
        <ServerCrash className="h-6 w-6" />
      </span>
      <h3 className="text-base font-bold text-graphite-900">
        {is503 ? "Extração ao vivo não configurada" : "Não foi possível gerar a ficha"}
      </h3>
      <p className="max-w-md text-sm text-graphite-500">{message}</p>
      {is503 ? (
        <p className="max-w-md text-xs text-graphite-400">
          O ambiente demo roda offline apenas para o <strong>Ford Ranger Raptor</strong>. Para
          outros veículos, configure <code className="font-mono">ANTHROPIC_API_KEY</code> e a busca.
        </p>
      ) : null}
    </Card>
  );
}
