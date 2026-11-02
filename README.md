# EvoMemBench subset replication — public evidence bundle

Evidence bundle for the article 《16K 到 128K，记忆增益从 +18 缩到 +6：我在网关最便宜的 GPT 端点上复测了 EvoMemBench 的一个子集》 (vxi.me), a pre-registered subset replication of **EvoMemBench** (arXiv:2605.18421v3) run on 2026-11-02.

**What was run.** One environment (Gorilla File System) of the paper's InEp-Exec setting, using the official repository [DSAIL-Memory/EvoMemBench](https://github.com/DSAIL-Memory/EvoMemBench) pinned at commit `5f550e0c48f9f1873f64bab9d1c94da5d3ccc4aa` and its in-episode runner with the paper's protocol (FC mode, long-context noise on, context budgets 16K / 128K). Three arms — no-memory baseline (A0), BM25 retrieval memory (A1), ACE procedural memory (A2) — over the same 50 tasks per cell, 300 episodes total, zero failed calls. Backbone: an endpoint **labelled `gpt-6-luna`** at the operator's third-party OpenAI-compatible gateway (gateway name redacted in this bundle). The label is the gateway's; the underlying served model cannot be independently verified, so every number here is bounded to that labelled endpoint and is a variant caliber, never the paper's DeepSeek-V3.2 caliber.

**Headline results** (official success rate, n=50 per cell):

| Arm | 16K | 128K | Gain vs same-budget A0 |
|---|---|---|---|
| A0 no memory | 38% (19/50) | 44% (22/50) | — |
| A1 BM25 | 42% (21/50) | 44% (22/50) | +4.0 → 0.0 |
| A2 ACE | 56% (28/50) | 50% (25/50) | +18.0 → +6.0 |

Verdict on the paper's Finding 3: the gain-shrinkage direction was observed on this subset and endpoint; the 128K below-baseline clause was not observed here — composite **PARTIAL**, single run. Paired analysis (same 50 tasks): ACE@16K discordants 9 wins / 0 losses; shrinkage paired-bootstrap 95% CI [0, +26] pts for ACE, [−10, +20] for BM25. Cost anatomy (not reported at this granularity in the paper): ACE's memory module consumed 2,662,908 tokens — 36.5% of ACE's own input, 17.6% of the whole run's input — and ≈7.4× the no-memory arm's output tokens.

**Errata (in the receipt, addendum E-1..E-4).** A registered sample-count deviation (D1) was **withdrawn**: v1's Table 2 listed 200 samples per environment, but v3 — the version replicated — lists 50, matching the shipped repository. The paper's total evaluation samples are 2,954 (v3 Table 2). The paper does report method-level total token usage (Tables 17/19/21/23); the memory-module-only split in this bundle is the part it does not report.

## Contents

- `run-receipt.md` — full run receipt: configuration, per-cell results, token accounting, deviation log (D1 withdrawn per errata), the cancelled Finding-5 probe record, and the external-review errata addendum.
- `data/full_results.json` — per-cell aggregates (success, progress, token splits).
- `data/per_sample/<cell>.csv` — per-task outcomes and token splits for all 300 episodes; the six cells share the same 50 task ids.
- `code/run_one.py`, `code/full.py` — the exact run launchers (public variants: gateway URL and credential are read from the environment).
- `code/transport_shim.patch` — the only code change to the pinned upstream: a transport-layer switch in the memory client (`EVOMEM_TRANSPORT=openai`); protocol, prompts, memory logic, truncation and scoring are unmodified upstream. `code/EVOMEM_LOCAL_PATCHES.md` documents it, including a disclosed upstream asymmetry (the authors' OpenAI path passes temperature 1 for the baseline handler; the memory path passes none — kept as-is).
- `analysis/paired_analysis.py` + `paired_analysis_output.txt` — the paired re-analysis; rerunning it on `data/` reproduces every statistic quoted above.
- `SHA256SUMS` — checksums for every file in this bundle.

## Verify

```sh
sha256sum -c SHA256SUMS
python3 analysis/paired_analysis.py
```

## License

MIT (see `LICENSE`). The upstream benchmark code and data belong to their respective authors; this bundle contains only the replication's own artifacts and documentation.
