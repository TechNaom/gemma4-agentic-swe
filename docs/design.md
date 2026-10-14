# Design: Do code-graph tools help a Gemma 4 coding agent, and can we trust the verdict?

Status: draft v0.1, 2026-10-15. Direction chosen: **A + B + C combined**.

## 1. One-line pitch

We run a Gemma 4 coding agent on real Python GitHub issues with code-graph tools switched on and off (C),
record every run so any verdict can be re-checked offline at zero GPU cost (A), and stress-test the patch
verifiers that produce those verdicts with planted bugs (B).

## 2. Research questions

| ID | Question | Piece |
|---|---|---|
| RQ1 | Which code-graph tools (dependency lookup, call graph, related-code retrieval, ...) change the issue-fix rate of a Gemma 4 agent, and by how much? | C |
| RQ2 | *How* do they help or hurt: fewer wasted steps, better file localisation, shorter context, more tool errors? | C + A |
| RQ3 | How often does the patch verifier give the wrong verdict, and which bug types slip through? | B |
| RQ4 | How much does a recorded-run replay cut the cost of re-evaluating an agent after a rule or verifier change? | A |

## 3. System

```
issues ──► agent (Gemma 4 + tool config k) ──► recorder ──► run store (JSONL)
                                                               │
                         replayer ◄────────────────────────────┘
                            │
             verifier(s) ◄──┴──► planted-bug patches (B)
                            │
                         results ──► analysis + charts ──► paper
```

### 3.1 Recorder and replayer (A)

- Wraps every model call and tool call. Stores: prompt, response, tool name, args, output, latency, tokens,
  and the final patch. One JSONL file per run, plus a run manifest (model, tool config, seed, commit SHA).
- **Replay mode:** feeds recorded model responses back instead of calling the model. A changed verifier,
  scoring rule or tool post-processor can be re-run over every past run with no GPU.
- Divergence check: if a replayed step would produce a different tool output, flag it and stop that run.

### 3.2 Ablation (C)

The harness (`swegemma`, see `HARNESS_README.md`) exposes 9 tools: `run_command`, `read_file`, `edit_file`,
`write_file`, `get_status`, `submit_patch`, and three code-intelligence tools built on precomputed per-commit
call graphs (`graphs/*.json`, NetworkX node-link) and embeddings (`embeddings/*.npz`):

- `get_code_neighbors(node)`: callers and callees of a symbol
- `search_similar_code(query)`: nearest symbols by embedding cosine similarity
- `get_code_subgraph(nodes)`: induced call subgraph over a set of symbols

Tool configurations:

| Config | Tools |
|---|---|
| k0 | Baseline: the 6 workspace/execution tools |
| k1 | k0 + `get_code_neighbors` |
| k2 | k0 + `search_similar_code` |
| k3 | k0 + `get_code_subgraph` |
| k4 | k0 + all three graph tools |
| k5 | k4 + read-only `code_analyzer` sub-agent (as in the starter kit) |

- Pilot: 10 issues × 6 configs = 60 runs.
- Full: 30–50 issues × 6 configs. Repeat a subset with 2–3 seeds to measure noise.
- Metrics: resolve rate, steps to fix, tokens, first-correct-file step, tool-error rate.

### 3.3 Planted-bug benchmark (B)

- Take correct patches (gold or agent-produced) and inject known faults: off-by-one, wrong branch,
  swallowed exception, partial fix, edits to the wrong file, test-only changes, formatting-only diffs.
- Run each verifier (test-based, LLM-judge with Gemma 4, rule-based) over them through the replayer.
- Metrics: false accept and false reject rate per fault type and per verifier.

## 4. Model and compute

| Use | Model | Where | Cost |
|---|---|---|---|
| Bulk ablation runs | `gemma-4-31b-it` | Gemini API (hosted Gemma, free tier) | Free, rate-limited |
| Fidelity check on a subset | `gemma-4-31b-it-qat-w4a16-ct` (competition model) | Kaggle GPU notebook, vLLM | Free quota |
| LLM-judge verifier (B) | `gemma-4-31b-it` or `gemma-4-26b-a4b-it` | Gemini API | Free, rate-limited |

The Gemini API lists `gemma-4-31b-it` and `gemma-4-26b-a4b-it`. Gemma 4-specific rate limits are not published,
so they are read from the AI Studio quota page (open item O2). Re-running a subset on the quantised competition
model shows whether the API results carry over to it.

### 4.1 Supporting resources

The owner has a **Google AI Pro** subscription. It does not raise Gemini API limits, but we use it for:

- Related-work research (Gemini Deep Research, NotebookLM) for the paper
- Prompt prototyping for the agent and the LLM judge in the AI Studio web UI (higher UI limits)
- Any Google Cloud credits it unlocks, as a paid fallback if free API limits block the full matrix

## 5. Issue source

The competition dataset ships **129 training tasks** in `tasks.jsonl` (SWE-bench style: `instance_id`, `repo`,
`base_commit`, `patch`, `test_patch`, `problem_statement`, `hints_text`): fastapi 67, rich 48, requests 13, httpx 1.
Each task has a repo snapshot (`snapshots/*.tgz`, ~21 GB total) and per-commit graph + embedding files. We sample
from these, stratified by repo. The hidden main-track test set (~120 tasks) is never used.

Verification follows the harness: apply agent patch, reset test files, apply `test_patch`, run `pytest`;
resolved iff exit code 0 and every target test passed. The gold `patch` gives correct patches to seed B.

## 6. Repository layout (planned)

```
src/g4swe/
  agent/       ADK agent configs per tool setting
  record/      recorder + replayer
  faults/      planted-bug generators (B)
  verify/      verifiers
  analysis/    metrics + charts
experiments/   run configs, manifests
notebooks/     Kaggle notebooks (public)
runs/          recorded runs (released as a dataset)
paper/         draft, figures
```

## 7. Timeline

| Week | Dates | Build | Stop-here result |
|---|---|---|---|
| 1 | Oct 15–21 | Resolve O1–O3, recorder/replayer, agent with switchable tools, 10-issue pilot | Working tool + pilot |
| 2 | Oct 22–28 | Full ablation, all runs recorded | Main results |
| 3 | Oct 29–Nov 4 | Planted-bug set, replay through verifiers, paper draft | Full story |
| 4 | Nov 5–10 | Charts, edit, reproducibility check, submit | Submitted |

## 8. Open items and risks

| ID | Item | Status |
|---|---|---|
| O1 | Code-graph tools the harness exposes | **Resolved 2026-10-15**: 3 tools, data shipped (section 3.2) |
| O1b | Where the `swegemma` harness lives | **Resolved 2026-10-15**: wheel `swegemma-0.2.11` (+ `adk_submission`, `adk_eval_core`) in Kaggle dataset `metric/gemma-4-developer-agent-wheelhouse`; licence unstated, so installed at run time, not redistributed |
| O1c | Routing harness model calls to hosted Gemma | **Resolved 2026-10-15**: harness CLI reads `LITELLM_API_BASE`/`LITELLM_API_KEY`; Gemini's OpenAI-compatible endpoint returns valid tool calls for `gemma-4-31b-it` (`scripts/smoke_toolcall.py`) |
| O2 | Gemma 4 rate limits on the Gemini API for our project | Key works (3–6 s/call, one transient 500); limits still to measure under load |
| O3 | Does the QAT w4a16 model load in vLLM on Kaggle T4s (`--dtype float16`, Marlin)? | Test in Kaggle notebook |
| O4 | Sandbox needs Linux (Docker or POSIX subprocess backend); the owner's laptop is Windows with no Docker/WSL distro | Run sandboxes in Kaggle notebooks (Linux, internet on for Gemini API calls) |
| R1 | Rate limits too tight for the full matrix | Shrink to 30 issues; spread runs over days |
| R2 | Harness package unavailable outside Kaggle | Our own harness re-implementing the documented tools becomes part of resource A |
| R3 | Results noisy at this sample size | Repeat seeds on a subset; report confidence intervals |
| R4 | Gemini API context and behaviour differ from vLLM 32k serving | Cap context at 32,768 tokens in our runner; fidelity subset on the QAT model |
