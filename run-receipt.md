> Public copy of the lab's run receipt for the EvoMemBench subset replication (article: 《16K 到 128K，Agent 记忆增益从 +18 缩至 +6：EvoMemBench 子集复测与 Token 成本解剖》, vxi.me). The gateway's name and base URL are redacted; the model label, all numbers, deviations and errata are reproduced in full.

# EvoMemBench InEp-Exec scoped run — execution receipt

Status: EXECUTED (full run complete, 2026-11-02). Adjudication below follows the
pre-registered plan in `experiment-plan.md` and its verdict vocabulary.
All first-party numbers in this receipt come from the official runner's own
per-sample CSVs (`per_sample.csv`) of the runs recorded here.

## Run configuration (frozen at step 0, unchanged throughout)

- Upstream: github.com/DSAIL-Memory/EvoMemBench @ `5f550e0c48f9f1873f64bab9d1c94da5d3ccc4aa`, subset In-Episode-Execution (INEP-EXEC, BFCL multi_turn_ours).
- Environment: Gorilla File System only, all 50 shipped samples (`ids_gorilla_fs.json`), data file SHA-256 `08fd17fa87a2b915a45aa0787668f8196d034dcfea4e6bab55d41abd4b13ea2d`.
- Arms (protocol flags identical to the authors' official scripts: FC mode, long-context noise on, per-sample memory scope):
  - A0 — no memory, via the authors' own OpenAI-compatible backend (`BATCH_BACKEND=gpt5mini`).
  - A1 — BM25 retrieval (`--memory-type bm25 --memory-top-k 3`), local backend, zero API memory tokens.
  - A2 — ACE procedural memory (`--memory-type ace`), substituted for ReasoningBank at step 0 (deviation D2 below).
- Budgets: 16000 and 128000 context tokens, six configurations, 300 episodes total. The 18 step-0.5 pilot episodes (3 per configuration, identical configuration) are included in these 300 via the runner's `--resume`; the remaining 282 ran 2026-11-02 ~14:10–14:32 CST.
- Backbone: the endpoint labelled `gpt-6-luna` at the owner's third-party OpenAI-compatible gateway (base URL redacted in this public copy), fixed for the whole run. **Identity boundary: the label is the gateway's; the underlying served model cannot be independently verified from this side. Every number below is bounded to that labelled endpoint and is a variant caliber, never the paper's DeepSeek-V3.2 caliber.**
- Errors: 0 API/runtime failures across all 300 episodes.

## Results (official success = the runner's own checker; n = 50 per cell)

| Arm | Budget | Success | Progress | Avg steps | Input tokens | Output tokens | of which memory-module tokens |
|---|---|---|---|---|---|---|---|
| A0 none | 16K | 19/50 = 38% | 0.643 | 12.32 | 2,041,594 | 29,979 | 0 |
| A0 none | 128K | 22/50 = 44% | 0.673 | 12.24 | 1,952,204 | 28,366 | 0 |
| A1 BM25 | 16K | 21/50 = 42% | 0.673 | 12.20 | 1,946,011 | 27,584 | 0 |
| A1 BM25 | 128K | 22/50 = 44% | 0.670 | 12.16 | 1,944,198 | 28,329 | 0 |
| A2 ACE | 16K | 28/50 = 56% | 0.762 | 13.68 | 3,791,732 | 216,319 | 1,338,755 |
| A2 ACE | 128K | 25/50 = 50% | 0.713 | 12.84 | 3,493,985 | 212,936 | 1,324,153 |

Run totals: 15,169,724 input tokens + 543,513 output tokens for 300 episodes.
At the Luna-tier list prices used at decision time (USD 0.20/M input, USD 1.20/M
output) this is roughly USD 3.7; the gateway account's own pricing applies and
is not visible from this side — either way the total sits far below the
pre-registered USD 60 hard cap. The step-0.5 pilot extrapolation (24.5M input)
overshot the actual total, because the three pilot episodes were token-heavier
than the full-set average.

Gains over the same-budget A0 (percentage points of success rate):

| Arm | 16K gain | 128K gain |
|---|---|---|
| A1 BM25 | +4.0 | 0.0 |
| A2 ACE | +18.0 | +6.0 |
| Best method | +18.0 | +6.0 |

## Adjudication (bounded to this subset, this backbone label, this single run)

- **Finding 3, core pattern (memory gains shrink as the context budget grows): REPRODUCED_DIRECTION.** Both memory arms shrink (BM25 +4.0 → 0.0; ACE +18.0 → +6.0), and the best-method gain shrinks from +18.0 to +6.0 points. The paper reports the same pattern on its DeepSeek-V3.2 caliber across four environments (best method +14.5 at 16K → +8.5 at 128K). Direction matches; magnitudes are the same order but are not the paper's cells and must not be quoted as them.
- **Finding 3, tail clause (at 128K, memory methods fall below the no-memory baseline): NOT_REPRODUCED in this subset.** No tested method fell below A0 at 128K. BM25's gain fully evaporated to an exact tie (44% vs 44%) — the boundary case of the clause, not an instance of it — and ACE remained +6.0 above baseline. With only two of the paper's fifteen methods tested, this neither confirms nor refutes the clause for the methods not run.
- **Composite verdict for the pre-registered reader claim: PARTIAL** — the shrinkage pattern reproduced in direction on a budget backbone; the below-baseline clause was not observed.
- **Observation (not a pre-registered primary test):** the procedural arm (ACE) is the strongest arm at both budgets, directionally consistent with the paper's Finding 4 (procedural memory fits execution tasks).
- **First-party cost facts:** ACE's memory module consumed 2,662,908 tokens across its 100 episodes (about 17.6% of the whole run's input) and generated roughly 7.4x A0's output tokens (reflector and curator calls); BM25's memory added zero API tokens. This cost asymmetry between memory families is measured here, not reported in the paper.
- **Pilot anomaly resolved:** the step-0.5 pilot suggested A0 burns more input at 16K than at 128K; at n=50 the two budgets are nearly identical (2.04M vs 1.95M). The pilot pattern was small-sample step-count noise, as suspected at the time.

## Statistical limits (read before quoting any cell)

- n = 50 per cell: a 4-point delta is two episodes; per-cell 95% intervals are roughly ±14 points. No single cell difference except ACE at 16K (+18) approaches separation. The direction verdict rests on the joint pattern (both arms shrinking; best-method gain shrinking), not on any one cell.
- Single run, single seed configuration, one environment of the paper's four, 50 of the 200 samples per environment the paper's Table 2 states (deviation D1). Nothing here speaks to the paper's other three environments, its other thirteen methods, or its DeepSeek-V3.2 caliber.

## Deviations recorded at step 0 (also in state-history)

- D1 — Sample counts: the repository ships 50 samples per environment; the paper's Table 2 states 200 per environment. Shipped counts were run (pre-registered stop condition 1).
- D2 — A2 method: ACE replaces ReasoningBank. As shipped, the ReasoningBank backend hard-requires a DashScope API key with embedding model `text-embedding-v4` hardcoded; the owner arranged gateway access only. ACE is the same procedural family and the paper's other headline procedural method.
- D3 — Transport: memory arms run through a minimal transport shim in the local working copy only (`EVOMEM_TRANSPORT=openai` inside `bfcl_eval/memory/ark_client.py`, documented in `EVOMEM_LOCAL_PATCHES.md` in that working copy). The authors' memory-arm transport is the Volcengine Ark batch SDK and their OpenAI backend refuses memory types. The shim changes transport only; protocol, prompts, memory logic, budget truncation and scoring are the pinned upstream code. One inherited configuration asymmetry is recorded for honesty: the authors' OpenAI-backend branch constructs its handler with temperature 1, while the Ark path (and therefore our shimmed memory arms) passes no temperature parameter — this asymmetry is the upstream code's own, kept as shipped.
- D4 — Backbone provenance: gateway-labelled endpoint instead of an official API (owner decision, 2026-11-02); see the identity boundary above.

## What this run does not establish

- Anything about the paper's full InEp-Exec table, its other quadrants (InEp-Know, CrossEp-Know, CrossEp-Exec), or any method not run here.
- Anything about the gateway endpoint's identity beyond its label.
- The optional CrossEp-Know Easy/Hard secondary probe (Finding 5 sign flip) was not run; it remains an untested plan item, not a result.

## Addendum (2026-11-02, drafting stage)

The CrossEp-Know secondary probe, described above as an untested plan item,
was subsequently attempted at pilot scale on 2026-11-02 and cancelled by the
owner the same day after the gateway account's quota ran out. The pilot
produced no adjudicable data (no completed grading), and the full probe was
never run. Finding 5 therefore remains untested by us; this dossier records
the probe as CANCELLED_BY_OWNER, not pending. The InEp-Exec results and the
PARTIAL verdict above are unaffected.


## Addendum — external-review corrections and paired analysis (2026-11-02)

Three external reviews (Gemini, hy4, ChatGPT) were adjudicated against the pinned repository, the paper v1/v3 full texts, and the frozen run artifacts (`full_results.json`, per-sample CSVs). Full adjudication: `external-review-adjudication.md`. Frozen run numbers are unchanged; two paper-fact errors and one registered deviation are corrected here.

### E-1. Deviation D1 is WITHDRAWN (version misreading)

D1 claimed the paper's Table 2 states 200 samples per environment while the repo ships 50. That is v1's Table 2 (verified against the v1 HTML: Gorilla File System (200), etc.). The version under replication, **v3, lists 50 per environment in Table 2** (InEp-Exec total 200), which matches the shipped repository exactly. The Step-0 reconciliation followed a third-party registry note that quoted the v1 text. Consequence: the run's per-environment n=50 equals the paper's own evaluation scale; there is no sample-count deviation. D2-D4 stand.

### E-2. Paper's total evaluation samples: 2,954 (not ~5.8K)

v3 Table 2 sums to 1200 + 200 + 884 + 200 + 270 + 200 = 2,954 evaluation samples. claims.json c1 corrected.

### E-3. The paper does report token usage — at method level

The paper defines token usage (agent + memory module combined) in section 5.1 and reports it per method in Tables 17/19/21/23 (InEp-Exec at 16K/32K/64K/128K). What it does not report is the memory-module-only split that this run measured (claims c15 basis corrected accordingly). Cross-check at 128K (Table 23): ACE averages 196,563 total tokens per instance vs the DeepSeek-V3.2 no-memory baseline's 110,987 — a 1.77x ratio, with the overhead equal to 43.5% of ACE's total. Different caliber from this run's 36.5% (ACE input-internal split, gateway endpoint), same order of magnitude.

### E-4. Paired analysis on the frozen per-sample results (new)

All six cells ran the same 50 task ids (verified: identical id sets in all six per_sample.csv files), so gains were re-analyzed as paired per-task differences (10,000-resample bootstrap over tasks, seed 20261102):

- Success counts: A0 19/50 -> 22/50; BM25 21/50 -> 22/50; ACE 28/50 -> 25/50 (16K -> 128K).
- Discordant pairs vs same-budget A0: ACE@16K 9 wins / 0 losses; ACE@128K 6 / 3; BM25@16K 4 / 2; BM25@128K 3 / 3.
- Gain shrinkage (paired bootstrap 95% CI): ACE +12.0 pts [+0.0, +26.0]; BM25 +4.0 pts [-10.0, +20.0].
- Decomposition of ACE's shrinkage (6 tasks): baseline drift +3 tasks and ACE's own move -3 tasks contribute equally.

Interpretation: the ACE 16K gain rests on a clean paired signal (9-0), the shrinkage direction is borderline under the paired CI (lower bound at 0), and BM25's shrinkage is indistinguishable from zero. The run's composite verdict (PARTIAL) is unchanged; the article's statistics paragraph now states this paired basis and describes the direction claim as descriptive.
