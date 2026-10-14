"""Build notebooks/smoke/smoke.ipynb: sandbox check (gold/empty) + one agent run on Kaggle."""
import json
import sys
from pathlib import Path

MODE = sys.argv[1] if len(sys.argv) > 1 else "audit"  # audit | agent

CELLS = [
    ("markdown", "# Smoke test: swegemma harness + hosted Gemma 4\n\n"
     "1. Install the official harness from `metric/gemma-4-developer-agent-wheelhouse`.\n"
     "2. **Sandbox audit** on all 129 tasks: the reference patch must resolve; an empty patch must not.\n"
     "3. One agent run (config k0) with `gemma-4-31b-it` via the Gemini API, if the `GEMINI_API_KEY` secret is attached.\n\n"
     "Code: https://github.com/TechNaom/gemma4-agentic-swe"),
    ("code", """import glob, os, subprocess, sys
from pathlib import Path

LOG = '/kaggle/working/notebook.log'

def sh(cmd, check=True):
    # Tee output to notebook.log: Kaggle's API log is often empty.
    with open(LOG, 'a') as log:
        log.write(f'$ {cmd}\\n')
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log.write(p.stdout + f'[exit {p.returncode}]\\n')
    print('$', cmd, '\\n', p.stdout[-3000:], flush=True)
    if check and p.returncode:
        raise RuntimeError(f'exit {p.returncode}: {cmd}')

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
    *([("markdown", "## Sandbox check")] if MODE == "audit" else []),
    *([("code", """# Every task: the reference patch should resolve, an empty patch should not.
sh(f'python -m g4swe.run_eval --mode gold  --data-dir {DATA_DIR}')
sh(f'python -m g4swe.run_eval --mode empty --data-dir {DATA_DIR}')""")] if MODE == "audit" else []),
    ("markdown", "## One agent run (k0, Gemma 4 31B via Gemini API)"),
    ("code", """try:
    from kaggle_secrets import UserSecretsClient
    os.environ['GEMINI_API_KEY'] = UserSecretsClient().get_secret('GEMINI_API_KEY')
except Exception as e:
    open(LOG, 'a').write(f'GEMINI_API_KEY secret not available: {e!r}\\n')
    print('GEMINI_API_KEY secret not available:', repr(e))
sh(f'python -m g4swe.run_eval --mode agent --agent agents/k0 --data-dir {DATA_DIR} --task-ids rich_2725', check=False)"""),
    ("code", """import json
sh('tar czf /kaggle/working/results.tgz results')
for f in sorted(glob.glob('results/*/runs.jsonl')):
    rows = [json.loads(line) for line in open(f)]
    print(f, sum(r['resolved'] for r in rows), '/', len(rows))
    for r in rows:
        print('   ', r)"""),
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
