"""Run the official swegemma harness with hosted Gemma 4 (Gemini API) or a supplied patch.

Modes:
  agent  Run an agent config (agents/k0..k5) end to end: Phase 1 agent, Phase 2 verification.
  gold   Skip the agent and verify each task's reference patch. Sandbox check: should resolve.
  empty  Skip the agent and verify an empty patch. Sandbox check: should NOT resolve.
  patch  Skip the agent and verify patches from --patch-dir. Files are named <instance_id>.patch or
         <instance_id>__<variant>.patch; each file is one verification. Replays recorded runs (A)
         and checks planted-bug patches (B).

Supplied-patch modes reuse the harness's own Phase 2 unchanged; only the patch source differs.

    python -m g4swe.run_eval --mode gold --data-dir /kaggle/input/competitions/gemma-4-developer-agent --n 2
    python -m g4swe.run_eval --mode agent --agent agents/k0 --task-ids fastapi_15661
    python -m g4swe.run_eval --mode patch --patch-dir faults/patches
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # offline Kaggle sessions may lack it; .env is only used locally
    def load_dotenv(*_a, **_k):
        return False

GEMINI_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"


@dataclass
class RunRecord:
    instance_id: str
    variant: str
    repo: str
    mode: str
    agent: str
    resolved: bool
    test_exit_code: int
    tool_calls: int
    duration_seconds: float
    patch_chars: int
    error: str | None


def route_models(backend: str, api_base: str) -> None:
    """Point the harness's LiteLLM calls at hosted Gemma (Gemini API) or a local vLLM server.

    For `local`, start vLLM with `--served-model-name <alias>` matching the agent YAML's `model:`.
    """
    if backend == "local":
        os.environ["LITELLM_API_BASE"] = api_base
        os.environ["LITELLM_API_KEY"] = "EMPTY"
        return
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set (.env locally, Kaggle Secrets on Kaggle).")
    os.environ["LITELLM_API_BASE"] = GEMINI_OPENAI_BASE
    os.environ["LITELLM_API_KEY"] = key


def select_tasks(tasks, task_ids: list[str] | None, n: int | None, seed: int):
    if task_ids:
        wanted = set(task_ids)
        return [t for t in tasks if t.instance_id in wanted]
    if n:
        rng = random.Random(seed)
        return rng.sample(list(tasks), min(n, len(tasks)))
    return list(tasks)


def build_evaluator(args, data_dir: Path, results_dir: Path):
    from google.adk.agents.context_cache_config import ContextCacheConfig
    from google.adk.apps._configs import EventsCompactionConfig
    from swegemma.cli import _build_cli_model_registry
    from swegemma.config import EvalConfig, build_submission_limits
    from swegemma.evaluate import Evaluator

    agent_dir = Path(args.agent).resolve()
    limits, gen_constraints = build_submission_limits()
    config = EvalConfig(
        tasks_path=data_dir / "tasks.jsonl",
        snapshots_dir=data_dir / "snapshots",
        results_dir=results_dir,
        submission_dir=agent_dir,
        models=_build_cli_model_registry(submission_dir=agent_dir),
        sandbox=args.sandbox,
        timeout_seconds=args.timeout_seconds,
        verification_timeout_seconds=300,
        max_time_minutes=args.max_time_minutes,
        max_tool_calls=args.max_tool_calls,
        max_turns=args.max_turns,
        limits=limits,
        generation_constraints=gen_constraints,
        context_cache_config=ContextCacheConfig(min_tokens=2048, ttl_seconds=1800, cache_intervals=10),
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=15, overlap_size=2, token_threshold=14336, event_retention_size=5
        ),
        graph_dir=str(data_dir / "graphs"),
        embeddings_dir=str(data_dir / "embeddings"),
        wheels_dir=data_dir / "wheels",
        skip_agent_patch=(args.mode == "empty"),
        display_mode="quiet",
    )
    evaluator = Evaluator(config)
    evaluator.supplied_patch = None

    if args.mode in ("gold", "patch"):
        from adk_eval_core.tracing import SessionTrace

        async def supplied_patch(task, *_a, **_k):
            patch = task.patch if args.mode == "gold" else evaluator.supplied_patch
            return patch, None, SessionTrace()

        evaluator._run_agent_sandbox = supplied_patch
    return evaluator


def build_jobs(args, tasks) -> list[tuple]:
    """(task, variant, patch_text) per verification. Only patch mode has more than one job per task."""
    if args.mode != "patch":
        return [(t, "", None) for t in tasks]
    by_id = {t.instance_id: t for t in tasks}
    jobs = []
    for f in sorted(Path(args.patch_dir).glob("*.patch")):
        instance_id, _, variant = f.stem.partition("__")
        if instance_id in by_id:
            jobs.append((by_id[instance_id], variant, f.read_text(encoding="utf-8")))
    return jobs


async def run(args) -> list[RunRecord]:
    from swegemma.models import load_tasks

    data_dir = Path(args.data_dir)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    agent_name = Path(args.agent).name if args.mode == "agent" else "-"
    results_dir = Path(args.results_root) / f"{stamp}_{args.mode}_{agent_name}"
    results_dir.mkdir(parents=True, exist_ok=True)

    tasks = select_tasks(load_tasks(data_dir / "tasks.jsonl"), args.task_ids, args.n, args.seed)
    if args.mode == "agent":
        route_models(args.backend, args.api_base)
    evaluator = build_evaluator(args, data_dir, results_dir)

    model = None
    if args.mode == "agent":
        from adk_submission.discovery import discover_declared_models

        model = ", ".join(sorted(discover_declared_models(Path(args.agent))))
        model += " via Gemini API" if args.backend == "gemini" else f" via local vLLM ({args.api_base})"
    manifest = {
        "mode": args.mode,
        "agent": agent_name,
        "model": model,
        "task_ids": [t.instance_id for t in tasks],
        "seed": args.seed,
        "sandbox": args.sandbox,
        "budget": {
            "max_tool_calls": args.max_tool_calls,
            "max_time_minutes": args.max_time_minutes,
            "max_turns": args.max_turns,
        },
        "python": platform.python_version(),
        "started": stamp,
    }
    (results_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    jobs = build_jobs(args, tasks)
    records: list[RunRecord] = []
    for i, (task, variant, patch) in enumerate(jobs, start=1):
        print(f"[{i}/{len(jobs)}] {task.instance_id} {variant} ({task.repo}) mode={args.mode}", flush=True)
        evaluator.supplied_patch = patch
        r = await evaluator.evaluate_task(task=task, task_index=i, total_tasks=len(jobs))
        stem = f"{task.instance_id}__{variant}" if variant else task.instance_id
        rec = RunRecord(
            instance_id=task.instance_id,
            variant=variant,
            repo=task.repo,
            mode=args.mode,
            agent=agent_name,
            resolved=bool(r.resolved),
            test_exit_code=r.test_exit_code,
            tool_calls=r.tool_calls,
            duration_seconds=round(r.duration_seconds, 1),
            patch_chars=len(r.agent_patch or ""),
            error=r.error,
        )
        records.append(rec)
        for sub, text in (("test_outputs", r.test_output), ("patches", r.agent_patch)):
            (results_dir / sub).mkdir(exist_ok=True)
            ext = "log" if sub == "test_outputs" else "patch"
            (results_dir / sub / f"{stem}.{ext}").write_text(text or "", encoding="utf-8")
        print(f"    resolved={rec.resolved} exit={rec.test_exit_code} tools={rec.tool_calls} "
              f"{rec.duration_seconds}s err={(rec.error or '')[:120]}", flush=True)
        with open(results_dir / "runs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec)) + "\n")

    resolved = sum(r.resolved for r in records)
    print(f"\n{args.mode} {agent_name}: resolved {resolved}/{len(records)} -> {results_dir}")
    return records


def main() -> None:
    load_dotenv()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["agent", "gold", "empty", "patch"], default="agent")
    ap.add_argument("--patch-dir", help="Directory of <instance_id>[__<variant>].patch files (patch mode)")
    ap.add_argument("--backend", choices=["gemini", "local"], default="gemini",
                    help="gemini: hosted Gemma via Gemini API; local: vLLM server at --api-base")
    ap.add_argument("--api-base", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--task-file", help="File with one instance_id per line (e.g. experiments/pilot_tasks.txt)")
    ap.add_argument("--agent", default="agents/k0", help="Agent config directory (agent mode)")
    ap.add_argument("--data-dir", default=os.environ.get("G4SWE_DATA_DIR", "data"))
    ap.add_argument("--results-root", default="results")
    ap.add_argument("--task-ids", nargs="*")
    ap.add_argument("--n", type=int, help="Random sample of N tasks")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--sandbox", choices=["subprocess", "docker"], default="subprocess")
    ap.add_argument("--max-tool-calls", type=int, default=60)
    ap.add_argument("--max-time-minutes", type=float, default=30)
    ap.add_argument("--max-turns", type=int, default=200)
    ap.add_argument("--timeout-seconds", type=int, default=300)
    args = ap.parse_args()
    if args.task_file:
        args.task_ids = (args.task_ids or []) + Path(args.task_file).read_text(encoding="utf-8").split()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
