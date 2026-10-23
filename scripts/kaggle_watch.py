"""Watch Kaggle notebooks; when a run finishes, save its results, analyse them and write a report.

Run by .github/workflows/kaggle-watch.yml every 30 minutes. For each kernel in ops/kaggle-watch.txt:
  - still running -> nothing to do
  - finished (complete or error) and this run (its lastRunTime) not yet processed ->
      download notebook.log and results.tgz, unpack results into experiments/<kernel>-<run time>/,
      run g4swe.analyze over them, and append a section to the report file.
Processed runs are remembered in ops/kaggle-watch-state.json, so each run is reported once.

    python scripts/kaggle_watch.py --report /tmp/report.md     # exit code 0; report empty if nothing new
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH = ROOT / "ops" / "kaggle-watch.txt"
STATE = ROOT / "ops" / "kaggle-watch-state.json"
TERMINAL = ("COMPLETE", "ERROR", "CANCEL")


def kaggle(*args: str) -> str:
    r = subprocess.run(["kaggle", *args], capture_output=True, text=True)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "outdated `kaggle` version" not in l)
    if r.returncode:
        raise RuntimeError(f"kaggle {' '.join(args)} failed: {out[-500:]}")
    return out


def last_run_times() -> dict[str, str]:
    text = kaggle("kernels", "list", "--mine", "--csv", "--page-size", "100")
    start = text.find("ref,")
    return {row["ref"]: row["lastRunTime"] for row in csv.DictReader(io.StringIO(text[start:]))}


def status(kernel: str) -> str:
    m = re.search(r'status "(?:KernelWorkerStatus\.)?(\w+)"', kaggle("kernels", "status", kernel))
    return m.group(1).upper() if m else "UNKNOWN"


def process(kernel: str, run_time: str, state: str) -> str:
    stamp = re.sub(r"[^0-9]", "", run_time)[:12]  # yyyymmddHHMM (UTC)
    dest = ROOT / "experiments" / f"{kernel.split('/')[-1]}-{stamp}"
    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        kaggle("kernels", "output", kernel, "-p", tmp, "--file-pattern", r"notebook\.log|results\.tgz|vllm\.log")
        tmp_path = Path(tmp)
        for name in ("notebook.log", "vllm.log"):
            if (tmp_path / name).exists():
                (dest / name).write_bytes((tmp_path / name).read_bytes())
        tgz = tmp_path / "results.tgz"
        if tgz.exists():
            with tarfile.open(tgz) as tf:
                tf.extractall(tmp_path / "x", filter="data")
            for run_dir in sorted((tmp_path / "x" / "results").glob("*")):
                if run_dir.is_dir():
                    target = dest / run_dir.name
                    subprocess.run(["cp", "-r", str(run_dir), str(target)], check=True)

    lines = [f"## `{kernel}`, run of {run_time} UTC: **{state}**", ""]
    run_dirs = sorted(p for p in dest.iterdir() if (p / "runs.jsonl").exists())
    agent_dirs = [p for p in run_dirs if "_agent_" in p.name]
    if agent_dirs:
        summary = subprocess.run(
            [sys.executable, "-m", "g4swe.analyze", *map(str, agent_dirs), "--out", str(dest / "SUMMARY.md")],
            capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src"), "PATH": _path(), "PYTHONIOENCODING": "utf-8"},
        )
        lines.append(summary.stdout or f"(analysis failed)\n```\n{summary.stderr[-1500:]}\n```")
    for d in run_dirs:
        rows = [json.loads(l) for l in (d / "runs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        lines.append(f"- `{d.name}`: resolved {sum(r['resolved'] for r in rows)}/{len(rows)}")
    if not run_dirs:
        lines.append("No results were produced.")
    if state != "COMPLETE" or not run_dirs:
        log = dest / "notebook.log"
        tail = "\n".join(log.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]) if log.exists() else "(no log)"
        lines += ["", "<details><summary>Last 40 log lines</summary>", "", "```", tail, "```", "</details>"]
    lines += ["", f"Saved to `{dest.relative_to(ROOT).as_posix()}`.", ""]
    return "\n".join(lines)


def _path() -> str:
    import os
    return os.environ.get("PATH", "")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", type=Path, required=True, help="Markdown report path (left empty if nothing new)")
    args = ap.parse_args()

    kernels = [l.strip() for l in WATCH.read_text().splitlines() if l.strip() and not l.startswith("#")]
    seen = json.loads(STATE.read_text()) if STATE.exists() else {}
    runs = last_run_times()
    sections = []
    for kernel in kernels:
        run_time = runs.get(kernel)
        if not run_time:
            print(f"{kernel}: not found")
            continue
        st = status(kernel)
        print(f"{kernel}: {st} (run {run_time})")
        if not st.startswith(TERMINAL) or seen.get(kernel) == run_time:
            continue
        sections.append(process(kernel, run_time, st))
        seen[kernel] = run_time
    STATE.write_text(json.dumps(seen, indent=2, sort_keys=True) + "\n")
    args.report.write_text("\n".join(sections), encoding="utf-8")
    print(f"{len(sections)} new finished run(s)")


if __name__ == "__main__":
    main()
