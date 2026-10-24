# Pilot findings (2026-10-24)

6 configs × 10 pilot tasks = 60 runs, `gemma-4-31b-it-qat-w4a16-ct` on vLLM, 4x L4, official harness,
15-minute / 60-tool-call / 200-turn budget per task. Full tables: `SUMMARY.md`.

## 1. The agent almost never uses the graph tools it is given

| | Runs with graph tools available | Runs that called any graph tool | Graph tool calls |
|---|---|---|---|
| k1–k5 | 50 | 4 (8%) | 6 |

The harness does advertise them (a "Code Intelligence Tools" section in the task prompt, verified in the
traces), and the calls that were made returned useful results. Gemma 4 still prefers `read_file` and
`run_command` (grep). With tools this rarely used, the k0–k5 differences below cannot be attributed to them.

**Implication:** the experiment measures *availability*, not *use*. To learn whether the tools help, a second
arm should make the agent use them (prompt guidance or a required first localisation step).

## 2. Resolve rates are flat: 60–70% in every config

k0 70% · k1 70% · k2 60% · k3 70% · k4 60% · k5 70%. With 10 tasks, a 1-task swing is 10 points, so these are
indistinguishable. Same 7 tasks pass in nearly every config; the same 3 fail in every config.

## 3. Failures are mostly budget/context, not reasoning

| Failure | Count | Where |
|---|---|---|
| Context window exceeded (32,768 tokens, vLLM max_model_len) | 7 | rich_3944 (5 configs), rich_3468 (k4) |
| Session timeout (15 min) | 2 | fastapi_14616 (k0), rich_3468 (k5) |
| Turn budget (200 turns) | 1 | rich_2943 (k4) |

rich_3944 overflows the context in 5 of 6 configs: the competition's 32k context is a real constraint.

## 4. Cost of a run

Mean 33–45 tool calls and 290k–400k tokens per task; median 3–4 minutes. k4 (all three graph tools listed)
was the most expensive (45 calls, 400k tokens) despite barely calling them.
