"""Run the official swegemma harness with hosted Gemma 4 (Gemini API) or a supplied patch.

Modes:
  agent  Run an agent config (agents/k0..k5) end to end: Phase 1 agent, Phase 2 verification.
  gold   Skip the agent and verify each task's reference patch. Sandbox check: should resolve.
  empty  Skip the agent and verify an empty patch. Sandbox check: should NOT resolve.

Supplied-patch modes reuse the harness's own Phase 2 unchanged; only the patch source differs.
The same seam replays recorded patches (A) and planted-bug patches (B).

    python -m g4swe.run_eval --mode gold --data-dir /kaggle/input/competitions/gemma-4-developer-agent --n 2
    python -m g4swe.run_eval --mode agent --agent agents/k0 --task-ids fastapi_15661
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

from dotenv import load_dotenv

GEMINI_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"


@dataclass
class RunRecord:
    instance_id: str
    repo: str
    mode: str
    agent: str
    resolved: bool
    test_exit_code: int
    tool_calls: int
    duration_seconds: float
    patch_chars: int
    error: str | None


def route_models_to_gemini() -> None:
    """Point the harness's LiteLLM calls at Gemini's OpenAI-compatible endpoint."""
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

    if args.mode == "gold":
        from adk_eval_core.tracing import SessionTrace

        async def supplied_patch(task, *_a, **_k):
            return task.patch, None, SessionTrace()

        evaluator._run_agent_sandbox = supplied_patch
    return evaluator


async def run(args) -> list[RunRecord]:
    from swegemma.models import load_tasks

    data_dir = Path(args.data_dir)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    agent_name = Path(args.agent).name if args.mode == "agent" else "-"
    results_dir = Path(args.results_root) / f"{stamp}_{args.mode}_{agent_name}"
    results_dir.mkdir(parents=True, exist_ok=True)

    tasks = select_tasks(load_tasks(data_dir / "tasks.jsonl"), args.task_ids, args.n, args.seed)
    if args.mode == "agent":
        route_models_to_gemini()
    evaluator = build_evaluator(args, data_dir, results_dir)

    manifest = {
        "mode": args.mode,
        "agent": agent_name,
        "model": "gemma-4-31b-it via Gemini API" if args.mode == "agent" else None,
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

    records: list[RunRecord] = []
    for i, task in enumerate(tasks, start=1):
        print(f"[{i}/{len(tasks)}] {task.instance_id} ({task.repo}) mode={args.mode}", flush=True)
        r = await evaluator.evaluate_task(task=task, task_index=i, total_tasks=len(tasks))
        rec = RunRecord(
            instance_id=task.instance_id,
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
    ap.add_argument("--mode", choices=["agent", "gold", "empty"], default="agent")
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
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
