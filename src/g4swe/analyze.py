"""Summarise agent runs: one row per config, plus tool usage and a task x config matrix.

Reads every results directory given (each holds runs.jsonl and traces/trace_<task>.json, as written by
g4swe.run_eval) and prints Markdown tables.

    python -m g4swe.analyze results/*_agent_k*                 # print
    python -m g4swe.analyze results/*_agent_k* --out summary.md
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

GRAPH_TOOLS = ("get_code_neighbors", "search_similar_code", "get_code_subgraph")
EDIT_TOOLS = ("edit_file", "write_file")


def trace_stats(path: Path) -> dict:
    """Tool counts, tokens and how early the agent first edited a non-test source file."""
    if not path.exists():
        return {}
    t = json.loads(path.read_text(encoding="utf-8"))
    calls = [c for s in t.get("steps", []) if s.get("source") == "agent" for c in (s.get("tool_calls") or [])]
    names = [c.get("function_name", "?") for c in calls]
    first_edit = next(
        (i for i, c in enumerate(calls, 1)
         if c.get("function_name") in EDIT_TOOLS
         and not _is_scratch_or_test(str((c.get("arguments") or {}).get("filepath", "")))),
        None,
    )
    return {
        "tools": Counter(names),
        "n_calls": len(calls),
        "tokens": (t.get("final_metrics") or {}).get("total_tokens"),
        "first_edit": first_edit,
    }


def _is_scratch_or_test(path: str) -> bool:
    p = path.lstrip("/").removeprefix("workspace/")
    name = p.rsplit("/", 1)[-1]
    return (p.startswith(("tests/", "test/", "/tmp", "tmp/")) or name.startswith(("test_", "repro"))
            or name.endswith("_test.py") or "/" not in p and name.startswith(("reproduce", "debug", "check")))


def load(dirs: list[Path]) -> list[dict]:
    rows = []
    for d in dirs:
        runs = d / "runs.jsonl"
        if not runs.exists():
            continue
        for line in runs.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r.get("mode") != "agent":
                continue
            r.update(trace_stats(d / "traces" / f"trace_{r['instance_id']}.json"))
            rows.append(r)
    return rows


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else float("nan")


def _median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else float("nan")


def report(rows: list[dict]) -> str:
    by_cfg: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_cfg[r["agent"]].append(r)
    cfgs = sorted(by_cfg)
    out = ["## Per config", "",
           "| Config | Tasks | Resolved | Rate | Mean tool calls | Median time (s) | Mean tokens | Mean first source edit (call #) | Errors |",
           "|---|---|---|---|---|---|---|---|---|"]
    for c in cfgs:
        rs = by_cfg[c]
        res = sum(r["resolved"] for r in rs)
        out.append(
            f"| {c} | {len(rs)} | {res} | {res / len(rs):.0%} | {_mean(r.get('n_calls') for r in rs):.1f} | "
            f"{_median(r['duration_seconds'] for r in rs):.0f} | {_mean(r.get('tokens') for r in rs):,.0f} | "
            f"{_mean(r.get('first_edit') for r in rs):.1f} | {sum(bool(r.get('error')) for r in rs)} |")

    out += ["", "## Graph tool usage", "",
            "Calls per run, and the share of runs that used the tool at least once.", "",
            "| Config | " + " | ".join(GRAPH_TOOLS) + " | read_file | run_command | sub-agent |",
            "|---|" + "---|" * (len(GRAPH_TOOLS) + 3)]
    for c in cfgs:
        rs = by_cfg[c]
        cells = []
        for tool in (*GRAPH_TOOLS, "read_file", "run_command"):
            counts = [r.get("tools", Counter()).get(tool, 0) for r in rs]
            used = sum(1 for x in counts if x)
            cells.append(f"{_mean(counts):.1f} ({used}/{len(rs)})")
        sub = [sum(v for k, v in r.get("tools", Counter()).items() if "analyzer" in k) for r in rs]
        cells.append(f"{_mean(sub):.1f} ({sum(1 for x in sub if x)}/{len(rs)})")
        out.append(f"| {c} | " + " | ".join(cells) + " |")

    tasks = sorted({r["instance_id"] for r in rows})
    grid = {(r["instance_id"], r["agent"]): r for r in rows}
    out += ["", "## Task x config", "", "✅ resolved, ❌ not resolved, · not run (tool calls in brackets)", "",
            "| Task | " + " | ".join(cfgs) + " |", "|---|" + "---|" * len(cfgs)]
    for t in tasks:
        cells = []
        for c in cfgs:
            r = grid.get((t, c))
            cells.append("·" if r is None else f"{'✅' if r['resolved'] else '❌'} ({r.get('n_calls', r['tool_calls'])})")
        out.append(f"| {t} | " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+", type=Path, help="results directories (each with runs.jsonl)")
    ap.add_argument("--out", type=Path, help="also write the Markdown here")
    args = ap.parse_args()
    md = report(load(args.dirs))
    print(md)
    if args.out:
        args.out.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
