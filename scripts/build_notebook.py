"""Build notebooks/smoke/smoke.ipynb: sandbox check (gold/empty) + one agent run on Kaggle."""
import json
from pathlib import Path

CELLS = [
    ("markdown", "# Smoke test: swegemma harness + hosted Gemma 4\n\n"
     "1. Install the official harness from `metric/gemma-4-developer-agent-wheelhouse`.\n"
     "2. **Sandbox check**: the reference patch must resolve; an empty patch must not.\n"
     "3. One agent run (config k0) with `gemma-4-31b-it` via the Gemini API, if the `GEMINI_API_KEY` secret is attached.\n\n"
     "Code: https://github.com/TechNaom/gemma4-agentic-swe"),
    ("code", """import glob, os, subprocess, sys
from pathlib import Path

def sh(cmd):
    print('$', cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)

sh('git clone -q --depth 1 https://github.com/TechNaom/gemma4-agentic-swe /kaggle/working/repo')
os.chdir('/kaggle/working/repo')

def find_one(pattern):
    hits = glob.glob(pattern, recursive=True)
    assert hits, f'not found: {pattern}'
    return Path(hits[0])

WHEELHOUSE = find_one('/kaggle/input/**/gemma-4-developer-agent-wheelhouse').resolve()
DATA_DIR = find_one('/kaggle/input/**/gemma-4-developer-agent/tasks.jsonl').parent
print('wheelhouse:', WHEELHOUSE, '| data:', DATA_DIR)

sh('pip install -q "google-adk==1.36.1" litellm networkx python-dotenv cachetools docker')
harness = [str(w) for w in WHEELHOUSE.glob('*.whl') if w.name.split('-')[0] in ('swegemma', 'adk_submission', 'adk_eval_core')]
sh('pip install -q --no-deps ' + ' '.join(harness))
os.environ['PYTHONPATH'] = 'src'"""),
    ("markdown", "## Sandbox check"),
    ("code", """TASKS = 'fastapi_15661 requests_7505'
sh(f'python -m g4swe.run_eval --mode gold  --data-dir {DATA_DIR} --task-ids {TASKS}')
sh(f'python -m g4swe.run_eval --mode empty --data-dir {DATA_DIR} --task-ids {TASKS}')"""),
    ("markdown", "## One agent run (k0, Gemma 4 31B via Gemini API)"),
    ("code", """try:
    from kaggle_secrets import UserSecretsClient
    os.environ['GEMINI_API_KEY'] = UserSecretsClient().get_secret('GEMINI_API_KEY')
except Exception as e:
    print('GEMINI_API_KEY secret not attached; skipping agent run.', e)
if os.environ.get('GEMINI_API_KEY'):
    sh(f'python -m g4swe.run_eval --mode agent --agent agents/k0 --data-dir {DATA_DIR} --task-ids requests_7505')"""),
    ("code", """sh('tar czf /kaggle/working/results.tgz results')
sh('cat results/*/runs.jsonl')"""),
]


def cell(kind, src):
    c = {"cell_type": kind, "metadata": {}, "source": src}
    if kind == "code":
        c.update(execution_count=None, outputs=[])
    return c


nb = {
    "cells": [cell(k, s) for k, s in CELLS],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}
out = Path(__file__).resolve().parents[1] / "notebooks" / "smoke"
(out / "smoke.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")
(out / "kernel-metadata.json").write_text(json.dumps({
    "id": "manoharpapasani/g4swe-smoke",
    "title": "g4swe smoke",
    "code_file": "smoke.ipynb",
    "language": "python",
    "kernel_type": "notebook",
    "is_private": True,
    "enable_gpu": False,
    "enable_internet": True,
    "dataset_sources": ["metric/gemma-4-developer-agent-wheelhouse"],
    "competition_sources": ["gemma-4-developer-agent"],
    "kernel_sources": [],
    "model_sources": [],
}, indent=2), encoding="utf-8")
print("wrote", out)
