# CLAUDE.md — SpecRadar (Mobile)

> Contexto do projeto. Leia antes de escrever código.
> Projeto acadêmico FIAP × Ford — Inteligência Competitiva Automotiva — entrega de
> **Mobile Development and IoT** (app Android em APK + backend).

---

## 1. O que é

App mobile que recebe **marca + modelo + versão + uma lista livre de atributos** e
devolve uma **ficha técnica padronizada**, sempre no mesmo formato, com dados
ausentes explícitos ("Não disponível"). Caso de validação: **Ford Ranger Raptor**.

Escopo da entrega: **app mobile (Expo / React Native) + backend (FastAPI)**.
Frontend web, BigQuery, Airflow e Looker foram removidos — não fazem parte desta matéria.
Mantenha tudo **simples** (nível de aluno de 2º ano): sem abstrações desnecessárias.

## 2. Estrutura

```
mobile/                       App Expo (SDK 57, TypeScript, Expo Router)
  src/app/                    Telas (cada arquivo = rota)
    (tabs)/index.tsx          Pesquisar (formulário)
    (tabs)/historico.tsx      Histórico (AsyncStorage)
    (tabs)/ajustes.tsx        Ajustes (modo offline × servidor)
    ficha.tsx                 Ficha técnica (resultado)
    atributo.tsx              Detalhe do atributo (fonte/evidência)
  src/components/             ui.tsx (botão, campo, card...) · spec.tsx (status, linha)
  src/services/               api.ts (backend) · offline.ts (dados embarcados) · storage.ts
  src/data/                   taxonomy.json + raptor-sheet.json (gerados pelo backend)
  src/theme.ts                Identidade visual — única fonte de cores/fontes/espaços
backend/                      API FastAPI (Python 3.12+)
  src/specradar/              pipeline: extração → normalização → reconciliação
  taxonomy/*.yaml             atributos, sinônimos e fontes (fonte da verdade)
  examples/ranger_raptor/     fixture offline (modo demonstração)
  scripts/export_mobile_data.py   gera mobile/src/data/*.json
  tests/                      unit + golden (Raptor)
```

## 3. Princípios (continuam valendo)

1. **A IA lê, nunca inventa.** O LLM só extrai; o trecho citado (evidência) é verificado
   contra o documento. Sem evidência → valor descartado.
2. **Normalização é código, não LLM** (unidades, pneu, motor, sinônimos).
3. **Ausência é explícita:** atributo sem dado → `status = NA`, `value = null`. Nunca omitir.
4. **Formato fixo:** a ficha segue a ordem da taxonomia; veículo sem dados recebe a
   mesma ficha com tudo `NA`.
5. **Taxonomia é a fonte da verdade** — nunca hardcode atributo; edite `taxonomy/*.yaml`
   e rode `scripts/export_mobile_data.py` para atualizar o app.
6. **Anomalias são sinalizadas:** o preço de R$ 499 da Raptor deve sair como `ANOMALY`.

## 4. Como o app obtém os dados

- **Offline (padrão):** usa `src/data/*.json` embarcados → o APK funciona sem servidor.
- **Servidor:** Ajustes → "Usar servidor" → URL (`http://10.0.2.2:8000` no emulador).
  Se o servidor falhar, o app cai para o offline e mostra um aviso (nenhum fluxo termina em erro).
- O backend sem chaves roda em **modo demo** (fixture da Raptor). Com `ANTHROPIC_API_KEY`
  + `SEARCH_API_KEY` faz busca real.

## 5. Comandos

```bash
# Backend
cd backend && python -m venv .venv && .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn specradar.api.main:app --reload --host 0.0.0.0
pytest -q && ruff check . && mypy src

# Mobile
cd mobile && npm install
npx expo start                 # Expo Go / emulador
npx tsc --noEmit && npx expo lint
eas build -p android --profile preview   # gera o APK na nuvem (EAS)
```

## 6. Convenções

- UI e documentação em **PT-BR**; identificadores e commits em inglês (Conventional Commits).
- Mobile: instale libs com `npx expo install` (versões compatíveis com o SDK).
  Não edite `android/`/`ios/` à mão (são gerados pelo `expo prebuild`).
- Cores/fontes só via `src/theme.ts`. Status (OK/NA/ANOMALY/CONFLICT/LOW_CONFIDENCE)
  sempre com `statusMeta`.
- Testes do backend sem rede; o golden test da Raptor precisa passar.
