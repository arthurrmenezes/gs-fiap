# SpecRadar — Arquitetura

Detalhamento do pipeline descrito no `CLAUDE.md`. A reframe central: **não é um
buscador**, é um **pipeline de dados com IA na camada de extração**.

## Visão geral

```
SpecRequest (API)
   │  [1] resolução de atributos livres → taxonomia canônica
   ▼
[2] Resolução de fontes        sources/resolver.py · fetcher.py · cleaner.py
   │      allowlist por autoridade → URLs → texto limpo (Document)
   ▼
[3] Extração ancorada          extraction/extractor.py · prompts.py · verifier.py
   │      LLM (tool-use, JSON Schema imposto) → ExtractedValue
   │      verifier: evidence_snippet ⊂ documento? senão descarta (anti-alucinação)
   ▼
[4] Normalização               normalization/{units,parsers,categorical,dispatch}.py
   │      determinística, pura → NormalizedValue (value_norm canônico)
   ▼
[5] Reconciliação              reconciliation/{coalesce,conflicts,anomalies}.py
   │      coalesce por tier · CONFLICT · ANOMALY · NA → ReconciledSpec
   ▼
[6] Persistência               storage/{schema,views,bigquery}.py
          raw → staging → curated (formato longo) · view pivotada v_spec_sheet
```

## Os quatro contratos inegociáveis (onde vivem no código)

| Princípio | Implementação |
|---|---|
| A IA lê, nunca inventa | `extraction/verifier.py` — `evidence_snippet` é substring literal do documento, verificado programaticamente; falha → descarta + `NA` + log `suspected_hallucination`. |
| Normalização é código, nunca LLM | `normalization/` — funções puras, testadas nos dois sentidos. O LLM **para** em `extractor.py`. |
| Todo valor carrega proveniência | `models.NormalizedValue`/`ReconciledSpec` — `source_url`, `source_tier`, `confidence`, `extracted_at`. |
| Conflito nunca em silêncio | `reconciliation/coalesce.py` — divergência entre tiers comparáveis → `CONFLICT`, ambos preservados em `alternatives`. |

## Modelo de dados (BigQuery, formato longo)

`fact_spec` é `vehicle × attribute × source` — atributo novo **não** muda o
schema físico (`storage/schema.py`). A "ficha sempre no mesmo formato" é a view
`curated.v_spec_sheet` (`storage/views.py`), que faz `dim_vehicle CROSS JOIN
dim_attribute LEFT JOIN fact_spec` usando a taxonomia como espinha — lacunas
viram `NA` explícito. `v_spec_diff` compara cada concorrente contra o baseline
Ford para o dashboard (Looker).

Particionamento por `reconciled_at`, clustering por `vehicle_id`.

## Fontes de dados

- **Web heterogênea** — descoberta via `sources/search.py` (Google CSE),
  restrita à allowlist (`taxonomy/sources.yaml`), fetch `httpx` com fallback
  Playwright, limpeza em `sources/cleaner.py`.
- **Ford data sheet (Excel)** — `ingest/ford_datasheet.py` lê a planilha oficial
  fornecida (matriz de equipamentos do Ranger: XLT/Limited/Limited+ 26MY) como
  **fonte estruturada tier 1**. Por ser estruturada, ela pula a extração por LLM,
  mas passa pela mesma normalização + reconciliação. É o **baseline Ford** do
  spec-diff.

## Testabilidade e modo offline

I/O (busca, fetch, LLM, BigQuery) é injetável via Protocols
(`SearchClient`, `LLMClient`, `StorageWriter`). Por isso as etapas [3]–[6] rodam
**sem rede**: o golden test e o CLI usam `pipeline/fixtures.py` (documentos
limpos + saída de LLM canned) e `InMemoryWriter`. O verifier roda de verdade
sobre os fixtures (snippets são substrings reais), então a garantia
anti-alucinação é exercida ponta a ponta.

## Orquestração

- `dags/specradar_on_demand.py` — pipeline para uma consulta nova.
- `dags/specradar_refresh.py` — scaffold semanal de monitoramento (diff/alerta é
  roadmap, §13).
