# Planted-bug run, 2026-10-23

163 mutants of the gold patches of 62 valid tasks (7 operators, `src/g4swe/faults.py`, seed 20261023),
each verified with the official `swegemma` harness (subprocess sandbox, Kaggle CPU). All 163 applied cleanly.

A mutant **escapes** if the harness marks it resolved: a broken fix the tests accept.

| Operator | Mutants | Escaped | Rate |
|---|---|---|---|
| bool_swap | 19 | 10 | 53% |
| off_by_one | 15 | 5 | 33% |
| drop_file | 16 | 4 | 25% |
| drop_line | 60 | 12 | 20% |
| return_none | 21 | 2 | 10% |
| flip_compare | 26 | 2 | 8% |
| remove_raise | 6 | 0 | 0% |
| **Total** | **163** | **35** | **21%** |

- **24 of 62 tasks (39%)** accept at least one broken fix.
- By repo: fastapi 12/72 (17%), rich 23/91 (25%).

## Caveat: equivalent mutants

Some escapes may not be bugs at all (an *equivalent mutant* changes code without changing behaviour,
e.g. `return False` -> `return None` where the result is only used as a boolean). The weak-test rate is
therefore an upper bound until each escape is reviewed: see `escaped_review.md`.

Files: `mutants.jsonl` (what was changed), `runs.jsonl` (harness verdicts), `run_manifest.json`.
