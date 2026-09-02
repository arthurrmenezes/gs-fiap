# SpecRadar

> Inteligência competitiva automotiva — FIAP × Ford.
> Recebe `marca + modelo + versão + atributos` e devolve uma **ficha de
> especificações padronizada, comparável, auditável e sempre no mesmo formato**.

A reframe central: **não é um buscador**, é um **pipeline de dados com IA na
camada de extração** que transforma a web heterogênea em uma base canônica de
specs da concorrência. Ver [`CLAUDE.md`](CLAUDE.md) para o contexto-mestre e
[`docs/architecture.md`](docs/architecture.md) para o detalhamento.

## Pipeline de 6 estágios

```
[1] API + resolução de atributos   (src/specradar/api, taxonomy)
[2] Resolução de fontes            (src/specradar/sources)
[3] Extração ancorada              (src/specradar/extraction)   ← anti-alucinação
[4] Normalização determinística    (src/specradar/normalization)
[5] Reconciliação                  (src/specradar/reconciliation)
[6] Persistência (medallion)       (src/specradar/storage)
```

Os quatro pilares inegociáveis: **a IA lê, nunca inventa** (evidência verificada
programaticamente); **normalização é código, nunca LLM**; **todo valor carrega
proveniência**; **conflito nunca é resolvido em silêncio**.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env            # preencher chaves (ver tabela no .env.example)
```

## Uso

```bash
# API (dev)
uvicorn specradar.api.main:app --reload

# Pipeline local para um veículo (usa fixtures offline por padrão)
python -m specradar.pipeline.orchestrate --make Ford --model "Ranger Raptor" --version "Raptor 3.0 V6"
```

## Testes e qualidade

```bash
pytest tests/unit -q            # rápidos, sem rede — conversores, parsers, verifier
pytest tests/golden -q          # aceite Ranger Raptor (gate de merge)

ruff check . && ruff format --check . && mypy src
```

O **golden test da Raptor é gate de merge**: nenhum PR entra na main sem
`pytest tests/golden` verde. Ele valida os 5 tipos de dado difíceis, o formato
de saída idêntico, o `price.brl` sinalizado como `ANOMALY` e o campo ausente
como `NA` explícito.

## Estrutura

Ver §5 do [`CLAUDE.md`](CLAUDE.md). A **taxonomia** (`taxonomy/*.yaml`) é a fonte
da verdade do domínio — atributos nunca são hardcoded no Python.

## Escopo (MVP)

Taxonomia canônica · API FastAPI · resolução de fontes por autoridade · extração
ancorada com verificação · normalização · BigQuery (raw/staging/curated) + view
pivotada · DAG on-demand · golden test no CI. Fora do MVP: monitoramento
contínuo com alertas, human-in-the-loop, cobertura total do mercado.
