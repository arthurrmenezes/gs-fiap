# Demo fixture — Ford Ranger Raptor (offline)

Drives the pipeline end-to-end with **no network**, used by both the CLI demo
(`python -m specradar.pipeline.orchestrate --make Ford --model "Ranger Raptor"`)
and the golden acceptance test (`tests/golden`).

- `documents/` — cleaned source text for two sources (Ford official, tier 1;
  iCarros, tier 3).
- `extraction.json` — the canned LLM tool outputs per document, in order. Every
  `evidence_snippet` is a **literal substring** of its document, so the real
  evidence verifier runs against this fixture.

It deliberately includes two adversarial cases:
1. **Hallucination** — iCarros claims `engine.torque_nm = 600 Nm` with an
   evidence snippet absent from the document → the verifier discards it, leaving
   the Ford value (583 Nm). This proves the anti-hallucination guarantee.
2. **Anomaly** — the price is the planted `R$ 499`, which the sanity check flags
   as `ANOMALY` (a mid-size pickup cannot cost R$ 499).
