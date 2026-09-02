# CLAUDE.md — SpecRadar

> Contexto-mestre do projeto. Leia este arquivo **inteiro** no início de cada sessão antes de escrever qualquer código.
> Projeto acadêmico FIAP × Ford — Inteligência Competitiva Automotiva.

---

## 1. O que é o SpecRadar

Ferramenta de inteligência competitiva que recebe uma entrada simples — **marca + modelo + versão + uma lista livre de atributos técnicos** — e devolve uma **ficha de especificações padronizada, comparável, auditável e sempre no mesmo formato**, independentemente do veículo.

**O problema que resolve:** hoje a Ford descobre como concorrentes se posicionam (preço e pacotes de equipamentos) por **busca manual** — sites, YouTube, reportagens, concessionárias — gastando **~1 hora por versão** num processo **impreciso** (erros passam despercebidos e viram decisão de negócio).

**A reframe central:** isto **não é um buscador**. É um **pipeline de dados com IA na camada de extração** que transforma a web heterogênea em uma **base canônica** de specs da concorrência. A consulta é só a superfície; o ativo é o dado normalizado + a taxonomia + a camada de confiança.

**Caso de validação (aceite oficial da Ford):** a **Ford Ranger Raptor**. A solução precisa entregar corretamente toda a ficha técnica da Raptor (ver `tests/golden/ranger_raptor_truth.yaml`). Isso vira um **golden test automatizado** — não uma checagem manual feita uma vez.

---

## 2. Princípios inegociáveis

Estas decisões já foram tomadas. **Não as reabra** sem o dono do projeto pedir explicitamente. Se uma tarefa empurrar contra um destes princípios, pare e sinalize.

1. **A IA lê, nunca inventa.** O LLM é um *parser universal* de fontes bagunçadas, jamais o *autor* de um número. Toda extração é **ancorada em evidência**: o modelo é obrigado a citar o trecho literal da fonte, e esse trecho é **verificado programaticamente** contra o documento. Evidência que não existe na página → valor descartado e marcado como suspeita de alucinação.

2. **Normalização é determinística — código, nunca LLM.** Conversão de unidade, parsing de strings e mapeamento de sinônimos são Python puro, testável. Conversão errada por alucinação é um bug invisível que destrói confiança. Cada conversor/parser tem teste unitário.

3. **Todo valor carrega proveniência.** Cada spec persistida tem `source_url`, `source_tier`, `confidence` e `extracted_at`. Sem proveniência, o dado não entra na camada `curated`.

4. **Conflito nunca é resolvido em silêncio.** Quando fontes divergem além da tolerância, ambos os valores são preservados e o campo recebe `status = CONFLICT`. O sistema sinaliza; o humano decide.

5. **Ausência é explícita.** Atributo não encontrado → `status = NA` com valor `null`. Nunca um chute, nunca um campo omitido.

6. **A saída padronizada é uma VIEW, não uma tabela larga.** O armazenamento é em **formato longo** (`vehicle × attribute × source`). A "ficha sempre no mesmo formato" é uma view que pivota usando a taxonomia como espinha. Atributo novo **não** muda o schema físico.

7. **A taxonomia é a fonte da verdade do domínio.** Atributos, tipos, unidades e valores permitidos vivem em `taxonomy/*.yaml`, versionados. **Nunca** hardcode um atributo no código Python — carregue da taxonomia.

8. **O golden test da Raptor é gate de merge.** Nenhum PR entra na main sem `pytest tests/golden` passando.

---

## 3. Stack tecnológica

Escolhida para nascer **dentro** da stack de dados da Ford (Airflow → BigQuery → visualização), não ao lado dela. O ecossistema é Python; é uma decisão deliberada não brigar contra ele.

| Camada | Tecnologia | Por quê |
|---|---|---|
| Linguagem | **Python 3.12** | Ecossistema nativo de Airflow, BigQuery e LLM SDKs |
| API | **FastAPI + Pydantic v2** | Contrato tipado, validação de entrada, OpenAPI grátis |
| Extração | **LLM com structured outputs** (Anthropic / tool-use) | JSON Schema *imposto*, não pedido em prosa |
| Fetch | **httpx** (estático) · **Playwright** (fallback JS) | Playwright é caro/frágil → só quando a página exige JS |
| Busca de fontes | **SerpAPI** ou **Google CSE** | Descoberta de URLs candidatas, restrita a allowlist |
| Armazenamento | **Google BigQuery** | Stack Ford; camadas medallion + views |
| Orquestração | **Apache Airflow** | Stack Ford; DAG on-demand + DAG de refresh |
| Visualização | **Looker Studio** | Nativo do BigQuery, consumidor final é analista |
| CI/CD | **GitHub Actions** | Lint + types + unit + golden a cada PR |
| Qualidade | **ruff** (lint+format) · **mypy** · **pytest** | Padrão moderno |

---

## 4. Arquitetura — pipeline de 6 estágios

Fluxo ponta a ponta. Cada estágio é um módulo isolado e testável em `src/specradar/`.

```
Entrada              [1] API + resolução de atributos
  │                      Valida {make, model, version, year?, attributes[]}.
  │                      Mapeia atributos livres → taxonomia canônica.
  ▼
[2] Resolução de fontes   sources/resolver.py
  │                      Allowlist por autoridade → URLs candidatas.
  │                      fetcher.py (httpx/Playwright) → cleaner.py (HTML/PDF → texto limpo).
  ▼
[3] Extração ancorada     extraction/extractor.py
  │                      LLM + JSON Schema forçado. Para cada atributo:
  │                      {value_raw, evidence_snippet, confidence, found}.
  │                      verifier.py confirma evidence_snippet ⊂ documento.
  ▼
[4] Normalização          normalization/{units,parsers,categorical}.py
  │                      Determinística: cv↔kW↔hp, parsing de pneu/motor, sinônimos.
  ▼
[5] Reconciliação         reconciliation/{coalesce,conflicts,anomalies}.py
  │                      Coalesce por autoridade · conflito · sanity check por categoria.
  ▼
[6] Persistência          storage/{bigquery,schema,views}.py
                          raw → staging → curated. View pivotada = ficha padronizada.
```

**Orquestração (Airflow, `dags/`):**
- `specradar_on_demand.py` — dispara o pipeline para uma consulta nova.
- `specradar_refresh.py` — semanal: re-extrai o portfólio monitorado, faz **diff** contra a versão anterior e **alerta** quando um concorrente muda spec ou preço. (É isto que transforma "consulta pontual" em "monitoramento contínuo".)

---

## 5. Estrutura do repositório

```
specradar/
├── CLAUDE.md                      # este arquivo
├── README.md
├── pyproject.toml
├── .env.example
├── .pre-commit-config.yaml
├── taxonomy/
│   ├── attributes.yaml            # dicionário canônico de atributos (a joia da coroa)
│   ├── synonyms.yaml              # termo-fonte → valor/atributo canônico
│   └── sources.yaml               # allowlist de fontes + tiers de autoridade
├── src/specradar/
│   ├── config.py                  # settings via pydantic-settings (.env)
│   ├── api/
│   │   ├── main.py                # app FastAPI
│   │   ├── routes.py
│   │   └── schemas.py             # SpecRequest / SpecSheetResponse
│   ├── taxonomy/
│   │   ├── loader.py              # carrega + valida os YAML
│   │   └── models.py              # AttributeDef, DataType (enum)
│   ├── sources/
│   │   ├── resolver.py            # busca + allowlist por autoridade
│   │   ├── fetcher.py             # httpx / Playwright
│   │   └── cleaner.py             # HTML/PDF → texto limpo
│   ├── extraction/
│   │   ├── extractor.py           # chamada LLM, structured output
│   │   ├── prompts.py
│   │   └── verifier.py            # verificação de evidência (anti-alucinação)
│   ├── normalization/
│   │   ├── units.py               # conversões de unidade
│   │   ├── parsers.py             # pneu, motor, dimensões
│   │   └── categorical.py         # mapeamento de sinônimos
│   ├── reconciliation/
│   │   ├── coalesce.py            # coalesce por autoridade
│   │   ├── conflicts.py           # detecção de conflito
│   │   └── anomalies.py           # sanity checks por categoria
│   ├── storage/
│   │   ├── bigquery.py            # cliente BQ, read/write
│   │   ├── schema.py              # schemas das tabelas
│   │   └── views.py               # SQL da view pivotada
│   └── pipeline/
│       └── orchestrate.py         # runner ponta a ponta (local + chamado pelos DAGs)
├── dags/
│   ├── specradar_on_demand.py
│   └── specradar_refresh.py
├── tests/
│   ├── unit/                      # rápidos, puros (units, parsers, verifier)
│   ├── golden/
│   │   ├── ranger_raptor_truth.yaml
│   │   └── test_ranger_raptor.py  # gate de merge
│   └── conftest.py
└── docs/
    └── architecture.md
```

---

## 6. Modelo de dados (BigQuery, formato longo)

**Camadas medallion:**
- `raw` — documentos brutos buscados (HTML/PDF). Imutável. Trilha de auditoria.
- `staging` — valores extraídos pelo LLM, antes de normalizar/reconciliar.
- `curated` — normalizado e reconciliado. É o que a view consome.

**Tabelas centrais (`curated`):**

```
dim_vehicle    vehicle_id · make · model · version · model_year · market
dim_attribute  attribute_id · name · group · data_type · canonical_unit · value_set
dim_source     source_id · domain · authority_tier · kind
fact_spec      vehicle_id · attribute_id · value_raw · value_norm · unit
               · source_url · source_tier · confidence · status · reconciled_at
```

**`status` (enum):** `OK` · `CONFLICT` · `ANOMALY` · `NA` · `LOW_CONFIDENCE`

**View de saída:** `curated.v_spec_sheet` pivota `fact_spec` pela taxonomia → ficha com formato idêntico para qualquer veículo, lacunas como `NA` explícito. É **isto** que a API serve e o Looker consome.

**Notas de custo/escala:** particionar `fact_spec` por `reconciled_at`; clusterizar por `vehicle_id`. Não fazer `SELECT *` em tabelas grandes.

---

## 7. A taxonomia canônica

O esquema canônico é o que torna a saída "sempre no mesmo formato". A ficha da Raptor revela que ele precisa suportar **5 tipos de dado difíceis** (além de boolean/texto triviais):

| `data_type` | Exemplo na Raptor | Tratamento |
|---|---|---|
| `SCALAR_UNIT` | `397 cv`, `583 Nm` | valor + unidade canônica; conversão determinística |
| `CATEGORICAL` | `4WD`, `Matrix LED` | restrito a `value_set`; sinônimos mapeados |
| `COMPOSITE` | `V6 3.0L biturbo` | parseado em sub-campos (cilindros/cilindrada/aspiração) |
| `DIMENSIONAL` | `285/70 R17` | parseado (largura/perfil/aro) |
| `ENUM_LIST` | modos de condução | conjunto de valores categóricos |

**Regra de ouro:** atributo nunca é hardcoded no Python. `taxonomy/loader.py` carrega e valida; o resto do código consome objetos `AttributeDef`.

**Excerto de `attributes.yaml` (padrão a seguir):**

```yaml
- id: engine.power_cv
  name: "Potência"
  group: powertrain
  data_type: SCALAR_UNIT
  canonical_unit: cv          # conversor aceita hp, kW e converte para cv

- id: drivetrain
  name: "Tração"
  group: powertrain
  data_type: CATEGORICAL
  value_set: ["FWD", "RWD", "4WD", "AWD"]

- id: wheels.tires
  name: "Pneus"
  group: wheels
  data_type: DIMENSIONAL
  parser: tire                # width / aspect_ratio / rim_diameter_in

- id: drive_modes
  name: "Modos de condução"
  group: dynamics
  data_type: ENUM_LIST
  value_set: [Normal, Sport, Slippery, Mud, Sand, "Rock Crawl", Baja]
```

> Tarefa de bootstrap: materializar ~35 atributos cobrindo os 5 tipos, usando a ficha da Raptor como molde de cobertura.

**`synonyms.yaml`** mapeia variantes de fonte → canônico (ex.: `"4x4" → 4WD`, `"tração nas quatro rodas" → 4WD`). Fontes são brasileiras (PT-BR), então o mapa PT→canônico é essencial.

**`sources.yaml`** — allowlist ordenada por **autoridade** (tier 1 vence no coalesce):
1. Site oficial da montadora
2. FIPE (preço) · Inmetro/PBEV (consumo/eficiência)
3. Agregadores: iCarros, Webmotors, Carros na Web
4. Editorial/reviews (menor confiança)

---

## 8. Contrato de extração (o coração anti-alucinação)

`extraction/extractor.py` deve seguir **exatamente**:

1. **Schema imposto.** A saída do LLM é forçada por JSON Schema / tool-use — nunca "peça JSON no prompt e parseie texto".
2. **Forma por atributo:** `{ attribute_id, value_raw, evidence_snippet, confidence: 0..1, found: bool }`.
3. **Evidência obrigatória e verificada.** `verifier.py` confirma que `evidence_snippet` é substring literal do documento limpo (comparação com whitespace normalizado). Falhou → descarta o valor, marca `NA`, loga como suspeita de alucinação. **Esta verificação é o que torna a solução defensável em produção.**
4. **Não encontrado → `found: false`, valor `null`.** Jamais inferir.
5. **O LLM para aqui.** Ele não converte unidade, não reconcilia, não decide conflito. Tudo isso é estágio determinístico a jusante.

---

## 9. Reconciliação e anomalias

- **Coalesce por autoridade** (`coalesce.py`): havendo o mesmo atributo de várias fontes, vence o tier mais alto.
- **Conflito** (`conflicts.py`): se valores de tiers comparáveis divergem além da tolerância do tipo, `status = CONFLICT` e ambos preservados.
- **Anomalia** (`anomalies.py`): sanity checks por categoria. Ex.: preço de picape média esperado em `[150_000, 600_000]` BRL → `R$ 499` dispara `status = ANOMALY`. **Este é exatamente o erro plantado na ficha da Raptor do briefing; capturá-lo automaticamente é um diferencial — mantenha o check.**

---

## 10. Comandos de desenvolvimento

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # preencher chaves

# Rodar a API (dev)
uvicorn specradar.api.main:app --reload

# Rodar o pipeline localmente para um veículo
python -m specradar.pipeline.orchestrate --make Ford --model "Ranger Raptor"

# Testes
pytest tests/unit -q            # rápidos, sem rede
pytest tests/golden -q          # aceite Raptor (gate de merge)

# Qualidade (rodar antes de todo commit)
ruff check . && ruff format --check . && mypy src
```

**`.env` (ver `.env.example`):**
```
ANTHROPIC_API_KEY=
GOOGLE_CLOUD_PROJECT=
BQ_DATASET=specradar
GCP_SA_KEY_PATH=
SEARCH_API_KEY=
SEARCH_ENGINE_ID=
```

---

## 11. Convenções

- **Idioma:** prosa/docs em PT-BR; **código, identificadores, nomes de campo, paths e mensagens de commit em inglês.** Chaves de atributo em inglês (`engine.power_cv`); valores categóricos canônicos podem ser PT-BR (legibilidade do analista) — definidos no `value_set`.
- **Tipagem:** type hints em tudo; `mypy` sem erros. Modelos de dados são Pydantic v2.
- **Erros:** falhe explicitamente com exceções específicas; nunca engula exceção silenciosamente. Em estágio de dados, prefira marcar `status` a abortar a ficha inteira.
- **Sem rede em testes unitários.** LLM, BigQuery e fetch são mockados em `tests/unit`. Chamadas reais só em `tests/golden` (e marcadas).
- **Determinismo:** `normalization/` e `reconciliation/` são funções puras — entrada → saída, sem efeito colateral.
- **Logging estruturado** (não `print`): cada estágio loga `vehicle_key`, `attribute_id`, decisão e `confidence`.
- **Git:** Conventional Commits (`feat:`, `fix:`, `test:`, `refactor:`...). Branch `feature/<slug>`. PR só entra com lint + types + unit + golden verdes.

---

## 12. Estratégia de testes

- **Unit** (`tests/unit`): um teste por conversor de unidade, por parser (pneu, motor, dimensão) e pelo verifier de evidência. Rápidos e puros.
- **Golden** (`tests/golden`): a Ranger Raptor com gabarito fixo em `ranger_raptor_truth.yaml`. O pipeline roda e o resultado é comparado **campo a campo**. Valida:
  - todos os 5 tipos de dado difíceis;
  - formato de saída idêntico;
  - `price.brl` sinalizado como `ANOMALY`;
  - campo ausente como `NA` explícito.
- **Definition of Done** (toda feature): código tipado, `mypy`/`ruff` limpos, teste unitário cobrindo o caminho feliz + 1 borda, golden test ainda verde, e — se mexeu em domínio — taxonomia/sinônimos atualizados via o mesmo PR.

---

## 13. Escopo

**MVP (este semestre) — construir:**
- [ ] Taxonomia canônica (~35 atributos, 5 tipos) + synonyms + sources
- [ ] API FastAPI com contrato `SpecRequest`/`SpecSheetResponse`
- [ ] Resolução de fontes com allowlist por autoridade (3–4 fontes)
- [ ] Extração ancorada com verificação de evidência
- [ ] Normalização das unidades e parsers principais
- [ ] BigQuery (raw/staging/curated) + view pivotada
- [ ] 1 DAG no Airflow (on-demand)
- [ ] Golden test da Raptor no CI
- [ ] Dashboard comparativo no Looker (ficha + spec diff vs. Ford)

**Fora do MVP (roadmap, apresentar mas não construir agora):**
- Monitoramento contínuo com alertas de mudança (DAG de refresh + diff)
- Revisão humana com fila para baixa confiança (human-in-the-loop)
- Cobertura total do mercado BR e múltiplos mercados
- Integração com dado licenciado B2B (ex.: JATO), se a Ford já licenciar

> Saber o que foi cortado é maturidade. Não prometa o roadmap inteiro como se fosse MVP.

---

## 14. Caso de validação — Ranger Raptor

Gabarito de aceite (resumo; o arquivo canônico é `tests/golden/ranger_raptor_truth.yaml`):

| Atributo | Valor esperado | Tipo |
|---|---|---|
| `engine.configuration` | V6 3.0 L biturbo | COMPOSITE |
| `engine.power_cv` | 397 cv @ 5.650 rpm | SCALAR_UNIT |
| `engine.torque_nm` | 583 Nm @ 3.500 rpm | SCALAR_UNIT |
| `transmission` | automática, 10 marchas, paddle shifters | COMPOSITE |
| `drivetrain` | 4WD | CATEGORICAL |
| `suspension.dampers` | FOX Racing Live Valve 2.5" | TEXT |
| `performance.0_100_kmh_s` | 5.8 s | SCALAR_UNIT |
| `drive_modes` | Normal, Sport, Slippery, Mud, Sand, Rock Crawl, Baja (7) | ENUM_LIST |
| `steering_modes` | Normal, Sport, Comfort | ENUM_LIST |
| `exhaust_modes` | Normal, Quiet, Sport, Baja | ENUM_LIST |
| `damper_modes` | Normal, Sport, Baja | ENUM_LIST |
| `headlights` | Matrix LED | CATEGORICAL |
| `wheels.tires` | 285/70 R17 AT, aro 17" | DIMENSIONAL |
| `price.brl` | **R$ 499 → ANOMALY** (esperado ser sinalizado) | SCALAR_UNIT |

---

## 15. Gotchas (atenção redobrada)

- **Alucinação de spec é fatal.** A verificação de evidência (§8) não é opcional. Sem ela, o projeto não tem valor.
- **Conversão de unidade errada é invisível.** Teste cada conversor nos dois sentidos. Cuidado com `cv` (métrico) vs `hp` (imperial) — não são iguais.
- **Drift de ano-modelo.** Ficha muda por ano. Sempre carregar `model_year`; dado sem ano é suspeito.
- **Legalidade/ToS de scraping.** Respeitar `robots.txt` e termos das fontes. Preferir dado oficial/estruturado a scraping agressivo.
- **Playwright é fallback, não padrão** — custo e fragilidade. Tente `httpx` primeiro.
- **Custo de LLM e de BigQuery.** Cache de documentos brutos (`raw`, por `content_hash`) evita re-extração; particionamento evita varredura cara.
- **PT-BR nas fontes.** Sinônimos e parsing precisam lidar com português ("cavalos", "câmbio automático", "tração integral").

---

## 16. Glossário

- **Ficha padronizada** — saída final, formato fixo, gerada pela view `v_spec_sheet`.
- **Taxonomia canônica** — dicionário único de atributos (`attributes.yaml`); fonte da verdade do domínio.
- **Extração ancorada** — extração de LLM obrigada a citar e ter verificada a evidência da fonte.
- **Proveniência** — `source_url` + `source_tier` + `confidence` + `extracted_at` de cada valor.
- **Tier de autoridade** — ranking de confiabilidade da fonte; tier 1 (montadora) vence no coalesce.
- **Spec diff** — comparativo lado a lado destacando vantagens/gaps de um veículo vs. a Ford.
- **Golden test** — teste de aceite da Raptor; gate de merge.
- **Medallion (raw/staging/curated)** — camadas de maturidade do dado no BigQuery.

---

*Última atualização: manter este arquivo vivo. Ao mudar arquitetura, taxonomia ou escopo, atualize aqui no mesmo PR.*