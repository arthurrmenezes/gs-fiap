# SpecRadar — Frontend

Console de inteligência competitiva da Ford. **Vite + React + TypeScript +
Tailwind CSS + Radix UI**, paleta Ford (azul profundo `#00095B`).

## Rodar em dev

Precisa do backend FastAPI rodando em `:8000` (o Vite faz proxy de `/api`):

```bash
# terminal 1 — backend (na raiz do repo)
uvicorn specradar.api.main:app --reload

# terminal 2 — frontend
cd frontend
pnpm install
pnpm dev            # http://localhost:5173
```

O ambiente demo funciona **offline** para o Ford Ranger Raptor (fixture embutida
no backend) — sem chaves de API.

## Build de produção

```bash
pnpm build          # gera frontend/dist
```

O backend serve `frontend/dist` automaticamente na raiz quando o build existe
(`specradar.api.main._mount_frontend`), então em produção é **single-origin**:
`uvicorn specradar.api.main:app` serve a SPA + a API em `/api`.

## Estrutura

```
src/
├── lib/        api client, formatters por data_type, domínio (status/grupos)
├── components/
│   ├── ui/     primitivos (Button, Card, Input, Tooltip, Popover)
│   ├── AppShell · SearchConsole · VehicleSummary
│   ├── SpecSheet · SpecRow (valor + status + confiança + proveniência)
│   └── States  (inicial / loading / erro)
├── types.ts    espelha o contrato da API (specradar.api.schemas)
└── App.tsx
```

## Design

- **Sem cara de IA**: layout de produto de dados — denso, numerais tabulares,
  azul Ford, hierarquia tipográfica forte (Inter).
- **Proveniência em foco**: cada spec mostra status (Confirmado/Conflito/Anomalia/
  NA), medidor de confiança e um popover com a evidência verificada + fonte.
- **Acessível**: primitivos Radix (tooltip/popover/foco).
