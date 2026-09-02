import { Radar } from "lucide-react";
import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto w-full max-w-[1240px] px-5 pb-24 pt-8 sm:px-8">{children}</main>
      <Footer />
    </div>
  );
}

function Header() {
  return (
    <header className="relative overflow-hidden bg-ford-header">
      <div className="absolute inset-0 bg-grid-faint [background-size:32px_32px] opacity-60" />
      <div
        className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full opacity-30 blur-3xl"
        style={{ background: "radial-gradient(circle, #2C56D6 0%, transparent 70%)" }}
      />
      <div className="relative mx-auto flex w-full max-w-[1240px] items-center justify-between px-5 py-5 sm:px-8">
        <div className="flex items-center gap-3.5">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/10 ring-1 ring-inset ring-white/20 backdrop-blur">
            <Radar className="h-6 w-6 text-white" strokeWidth={2} />
          </div>
          <div className="leading-tight">
            <div className="text-[19px] font-extrabold tracking-brand text-white">
              SpecRadar
            </div>
            <div className="text-xs font-medium text-ford-100/80">
              Ford · Inteligência Competitiva Automotiva
            </div>
          </div>
        </div>
        <nav className="hidden items-center gap-1 md:flex">
          <HeaderTab label="Consulta" active />
          <HeaderTab label="Portfólio monitorado" />
          <HeaderTab label="Taxonomia" />
        </nav>
        <div className="flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 ring-1 ring-inset ring-white/15">
          <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
          <span className="text-xs font-semibold text-white/90">Ambiente demo</span>
        </div>
      </div>
    </header>
  );
}

function HeaderTab({ label, active = false }: { label: string; active?: boolean }) {
  return (
    <button
      className={
        active
          ? "rounded-lg bg-white/12 px-3.5 py-2 text-sm font-semibold text-white ring-1 ring-inset ring-white/15"
          : "rounded-lg px-3.5 py-2 text-sm font-medium text-ford-100/70 transition-colors hover:bg-white/8 hover:text-white"
      }
    >
      {label}
    </button>
  );
}

function Footer() {
  return (
    <footer className="border-t border-graphite-200 bg-white">
      <div className="mx-auto flex w-full max-w-[1240px] flex-col items-start justify-between gap-2 px-5 py-6 text-xs text-graphite-400 sm:flex-row sm:items-center sm:px-8">
        <p>
          SpecRadar — pipeline de dados com extração ancorada em evidência. Cada valor é
          auditável: fonte, autoridade e confiança.
        </p>
        <p className="font-medium text-graphite-500">FIAP × Ford · MVP</p>
      </div>
    </footer>
  );
}
