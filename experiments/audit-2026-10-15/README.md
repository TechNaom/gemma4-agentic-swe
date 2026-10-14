# Sandbox audit, 2026-10-15

Every one of the 129 public training tasks was verified twice with the official `swegemma` harness
(subprocess sandbox, Kaggle CPU notebook, competition wheels):

- **gold**: the task's reference patch. Should resolve.
- **empty**: no patch. Should not resolve.

A task is **valid** for measuring agents only if gold resolves and empty does not.

| Repo | Tasks | Gold resolves | Empty resolves | Valid |
|---|---|---|---|---|
| fastapi | 67 | 31 | 2 | 29 |
| httpx | 1 | 0 | 0 | 0 |
| requests | 13 | 3 | 3 | 0 |
| rich | 48 | 39 | 0 | 39 |
| **Total** | **129** | **73** | **5** | **68** |

## Why gold patches fail (56 tasks)

| Cause | Tasks |
|---|---|
| Test imports a package missing from the competition wheels: `inline_snapshot` (27), `dirty_equals` (7) | 34 |
| Tests still fail with the reference patch | 13 |
| Verification timeout | 7 |
| Other | 2 |

## Tasks resolved by an empty patch (5)

`requests_7427`, `requests_7315`, `requests_7309`, `fastapi_14851`, `fastapi_14077`: their tests pass before any fix.

## Implications

- Only **68 / 129 (53%)** of public tasks can tell a working agent from a broken one in this environment.
- On the other 61, any agent score is noise: either nothing can pass, or everything passes.
- All agent experiments in this project use the 68 valid tasks; the rest are reported, not hidden.
- Open: whether the hidden scoring environment has the same gaps (`inline_snapshot` and `dirty_equals` are
  absent from the published `wheels/`).

Files: `gold_runs.jsonl`, `empty_runs.jsonl` (one line per task), manifests.
