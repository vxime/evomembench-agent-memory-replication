# Local patches to the pinned upstream checkout (EvoMemBench run, 2026-11-02)

Upstream: github.com/DSAIL-Memory/EvoMemBench @ 5f550e0c48f9f1873f64bab9d1c94da5d3ccc4aa
Scope: In-Episode-Execution/INEP-EXEC only. These patches exist ONLY in this
local working copy; nothing is pushed upstream.

## Patch 1 — OpenAI transport for ArkBatchClient (bfcl_eval/memory/ark_client.py)

Why: as shipped, every memory arm (and the FC/prompting handlers) calls the
backbone through Volcengine Ark's batch endpoint via the Ark SDK. This run's
backbone is the owner's OpenAI API (Luna-tier GPT, labelled variant arm), and
the gpt5mini backend in run_batch_eval.py refuses memory types other than
"none". The patch adds an opt-in transport (env EVOMEM_TRANSPORT=openai) that
exposes the identical client.batch.chat.completions.create(**kwargs) surface
on top of the official OpenAI client.

What does NOT change: message construction, context-budget truncation, tool
definitions, memory backends (BM25 / ACE logic and prompts), the official
eval_checker scoring, retry policy (tenacity layer kept; SDK retries off),
and call kwargs (no temperature or other parameter added or removed — the
Ark path passes none, so the OpenAI path passes none either; recorded as a
known transport difference vs. the authors' DeepSeek-on-Ark runs).

Also: _is_transient additionally treats HTTP 429/500/502/503/504 status codes
as transient (OpenAI SDK exceptions carry status_code); retry counts and
back-off are unchanged.

## Arm wiring (configuration, not code)

- A0 (no memory): the authors' own gpt5mini backend (BATCH_BACKEND=gpt5mini,
  GPT5MINI_BASE_URL=https://api.openai.com/v1, BATCH_MODEL_GPT5MINI=<pinned
  Luna model id>) — no patch involved.
- A1 (BM25) / A2 (ACE): run_batch_eval.py invoked directly for the
  gorilla_file_system subset only, with EVOMEM_TRANSPORT=openai and
  DEEPSEEK_API_KEY carrying the OpenAI key (the variable name is the authors'
  config surface; the value is the OpenAI key, used only via api.openai.com).
- A2 method substitution (recorded deviation): the pre-registered plan named
  ReasoningBank-style procedural memory. As shipped, ReasoningBank (and
  AgentKB / AWM) hard-require a DashScope (Alibaba) API key with the
  embedding model "text-embedding-v4" hardcoded in the backends. The owner
  arranged OpenAI access only, so A2 = ACE — same procedural-memory family,
  the paper's other headline procedural method (best on CrossEp-Know Hard,
  Finding 6), needing no second provider.

## Sample-count deviation (data, recorded at step 0)

Paper Table 2 states 200 InEp-Exec samples per environment; the repository
ships 50 per environment (200 total across 4 environments; ids files and
BFCL_v4_multi_turn_ours.json agree). This run uses the shipped counts:
Gorilla File System, 50 samples. Data file SHA-256:
08fd17fa87a2b915a45aa0787668f8196d034dcfea4e6bab55d41abd4b13ea2d

## Run configuration (owner, 2026-11-02)

- Backbone endpoint: third-party OpenAI-compatible gateway, base_url
  the gateway host (owner-specified), model label gpt-6-luna (owner-specified,
  fixed for the whole run). The OpenAI SDK appends /chat/completions to the
  base_url; whether this gateway expects the /v1 segment (i.e. base
  the gateway's /v1 base URL) or the bare host is settled empirically at bring-up by
  probing /models on both paths with the key, before any pilot spend — the
  working .env starts with /v1 and the receipt records which path answered.
- Identity boundary: gpt-6-luna is the gateway's label; the underlying served
  model cannot be independently verified from this side. All verdicts are
  bounded to "the endpoint labelled gpt-6-luna at this gateway".
- Key handling: the gateway key arrives via secure entry (custom connector
  for the gateway) and is injected into the run environment only; it is never
  written to the Dossier, memory, or any committed file. The .env in this
  directory holds placeholders only.

## Bring-up verification (2026-11-02)

- Base path settled: the OpenAI Python SDK against the gateway's /v1 base URL lists 29
  models including gpt-6-luna (bare the gateway host also answers /models; /v1
  is used as the canonical form). Plain chat and native function calling
  smoke tests pass on gpt-6-luna, with usage fields populated.
- Raw urllib requests to the gateway are refused by its Cloudflare layer
  (HTTP 403, error code 1010, user-agent based). The harness only ever calls
  through the OpenAI SDK, so this does not affect the runs.
- Harness plumbing verified without spend: all three arms pass --dry-run on
  the first 3 Gorilla File System ids with the exact official flag sets.
