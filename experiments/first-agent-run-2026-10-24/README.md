# First real agent run, 2026-10-24

Config **k0** (no graph tools) with `gemma-4-31b-it-qat-w4a16-ct` served by vLLM on Kaggle 4x L4,
through the official `swegemma` harness. Two pilot tasks.

| Task | Resolved | Tool calls | Time | Tokens | Same as the developers' fix? |
|---|---|---|---|---|---|
| fastapi_14786 | ✅ | 13 | 106 s | 117k | **Identical** (`param.strip()`) |
| rich_2725 | ✅ | 32 | 278 s | 330k | **Different fix, same effect**: changes which box segment is picked (`1 if last else 2`) instead of reordering the segment tuple |

## How to read it

- `traces/trace_<task>.json`: every step (what Gemma was told, what it thought, each tool call and result).
- `logs/<task>.log`: the same session as readable text.
- `patches/<task>.patch`: what the agent changed.
- `test_outputs/<task>.log`: the hidden tests run by the examiner.

## Notable behaviour

- fastapi_14786: reproduced the bug with a script, fixed one line, then **added a test to the repo's test file**
  (the harness strips test-file edits before grading, so only the source fix counted), cleaned up the script,
  checked `git diff`, submitted.
- rich_2725: 13 `read_file` calls paging through `rich/table.py` 30–150 lines at a time before finding the
  indexing bug, a natural case for graph tools (k1–k4) to shorten the search.
