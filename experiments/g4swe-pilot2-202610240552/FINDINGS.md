# Pilot 2 findings (2026-10-24)

k0 and k4 re-run, plus nudge configs n1–n5 (same tools as k1–k5, prompt says "locate code with the
code-intelligence tools first"). All with `max_output_tokens: 4096` (was 16384). Same 10 pilot tasks,
same model and budgets as pilot 1. Full tables: `SUMMARY.md`.

## 1. The 4096-token output cap removed every context overflow

| | Context-window overflows | All errors |
|---|---|---|
| Pilot 1 (16384 cap) | 7 / 60 | 10 / 60 |
| Pilot 2 (4096 cap) | **0 / 70** | 5 / 70 (all: 60-tool-call budget on fastapi_14616) |

## 2. A one-paragraph nudge raises tool adoption from ~0% to up to 90%

| Config | Runs using a graph tool |
|---|---|
| k0 / k4 (no nudge) | 0/10, 1/10 |
| n1 (`get_code_neighbors`) | 3/10 |
| n2 (`search_similar_code`) | 6/10 |
| n3 (`get_code_subgraph`) | 7/10 |
| n4 (all three) | 5/10 |
| n5 (all three + analyzer sub-agent) | 9/10 (sub-agent called in 8/10) |

## 3. Using the tools did not help; the trend is slightly negative

| Config | Resolved | Mean tool calls | Mean tokens | First source edit (call #) |
|---|---|---|---|---|
| k0 | 8/10 | 32.7 | 286k | 17.1 |
| n4 | 8/10 | 35.8 | 329k | 20.5 |
| n1, n2, n3, n5 | 6/10 each | 36.9–40.7 | 339k–391k | 19.6–26.4 |

Nudged agents spend more calls and tokens and reach their first source edit later. n1/n2/n3/n5 each lose
2 tasks k0 solves and gain none (p = 0.50, exact McNemar, n = 10): consistent direction, not yet significant.

## 4. Run-to-run variation

k0 solved 7/10 in pilot 1 and 8/10 here; the difference is fastapi_14616 (15-minute timeout in pilot 1).
rich_3468 and rich_3944 fail in every config in both pilots.

## Next: full ablation on all 68 valid tasks

Pilot sample sizes cannot separate configs (95% intervals ~40–90%). The full run tests, with paired
statistics, whether (a) offering tools changes outcomes (k4 vs k0) and (b) pushing the agent to use
them does (n4, n5 vs k0).
