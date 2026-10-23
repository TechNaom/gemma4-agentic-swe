"""Build a Kaggle notebook (+ kernel-metadata.json) that runs this repo on the competition data.

    python scripts/build_notebook.py audit                  # gold/empty check on all tasks (CPU)
    python scripts/build_notebook.py agent                  # one agent run via Gemini API (CPU, needs secret)
    python scripts/build_notebook.py gpu [task ids...]      # agent runs on the Kaggle-hosted competition model (GPU)
    python scripts/build_notebook.py faults                 # planted-bug patches verified on the valid tasks (CPU)

audit/agent write notebooks/smoke (kernel g4swe-smoke); gpu and faults get their own notebook and kernel.
"""
import json
import sys
from pathlib import Path

MODE = sys.argv[1] if len(sys.argv) > 1 else "audit"
GPU_TASKS = " ".join(sys.argv[2:]) or "rich_2725 fastapi_14786"
GPU_MODEL = "gemma-4-31b-it-qat-w4a16-ct"
USER = "manoharpapasani"

SETUP = """import glob, os, subprocess, sys
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

def find_one(pattern):
    hits = glob.glob(pattern, recursive=True)
    assert hits, f'not found: {pattern}'
    return Path(hits[0])

__GET_CODE__
WHEELHOUSE = find_one('/kaggle/input/**/gemma-4-developer-agent-wheelhouse').resolve()
DATA_DIR = find_one('/kaggle/input/**/gemma-4-developer-agent/tasks.jsonl').parent
print('wheelhouse:', WHEELHOUSE, '| data:', DATA_DIR)
os.environ['PYTHONPATH'] = 'src'"""

GET_CODE_ONLINE = """sh('git clone -q --depth 1 https://github.com/TechNaom/gemma4-agentic-swe /kaggle/working/repo')
os.chdir('/kaggle/working/repo')"""

# The L4 x4 machine is offline, so the GPU notebook takes our code from the private dataset g4swe-code.
GET_CODE_OFFLINE = """REPO = Path('/kaggle/working/repo'); REPO.mkdir(exist_ok=True)
tgz = glob.glob('/kaggle/input/**/g4swe-code.tgz', recursive=True)
if tgz and Path(tgz[0]).is_file():
    sh(f'tar xzf {tgz[0]} -C {REPO}')
else:  # Kaggle sometimes unpacks archives into a folder
    src = find_one('/kaggle/input/**/src/g4swe/run_eval.py').parents[2]
    sh(f'cp -r {src}/. {REPO}/')
os.chdir(REPO)"""
CODE_DATASET = f"{USER}/g4swe-code"
OFFICIAL_IMAGE = "gcr.io/kaggle-private-byod/python@sha256:37c64f7dd9c54116ecd1bcc88817c5469b88387388fade02bfa8bf3fc647d461"

INSTALL_HARNESS_ONLY = """sh('pip install -q "google-adk==1.36.1" litellm networkx python-dotenv cachetools docker')
harness = [str(w) for w in WHEELHOUSE.glob('*.whl') if w.name.split('-')[0] in ('swegemma', 'adk_submission', 'adk_eval_core')]
sh('pip install -q --no-deps ' + ' '.join(harness))"""

# Same steps as the official getting-started notebook: full wheelhouse incl. vLLM, restoring '+cu128' names.
INSTALL_FULL_WHEELHOUSE = """import shutil
for pth in glob.glob('/usr/local/lib/python*/*-packages/*cutlass*.pth'):
    os.unlink(pth)
tmp_whl = Path('/tmp/wheelhouse'); tmp_whl.mkdir(exist_ok=True)
for w in WHEELHOUSE.glob('*.whl'):
    if 'cutlass' in w.name.lower():
        continue
    name = w.name.replace('cu128', '+cu128') if ('cu128' in w.name and '+' not in w.name) else w.name
    if not (tmp_whl / name).exists():
        os.symlink(w, tmp_whl / name)
sh('pip install -q --no-deps --force-reinstall ' + ' '.join(sorted(str(w) for w in tmp_whl.glob('*.whl'))))
sh('nvidia-smi --query-gpu=name,memory.total --format=csv')"""

START_VLLM = f"""import shutil, traceback
import torch
from adk_submission import VllmConfig, VllmServer

MODEL = '{GPU_MODEL}'
server = None
try:
    MODEL_PATH = find_one(f'/kaggle/input/models/**/{{MODEL}}/*/config.json').parent
    gpus = torch.cuda.device_count()
    tp = 4 if gpus >= 4 else (2 if gpus >= 2 else 1)
    server = VllmServer(VllmConfig(
        model=str(MODEL_PATH), port=8000, host='127.0.0.1',
        tool_call_parser='gemma4', reasoning_parser='gemma4', max_model_len=32768,
        dtype='bfloat16' if torch.cuda.is_bf16_supported() else 'auto',
        gpu_memory_utilization=0.90, enable_auto_tool_choice=True,
        scheduler_reserve_full_isl=False, tensor_parallel_size=tp, startup_timeout=60 * 20,
        extra_args=['--served-model-name', MODEL],  # agent YAML `model:` must equal this name
    ))
    server.start()
    print('vLLM up:', server.base_url, 'tp =', tp, 'gpus =', gpus)
    open(LOG, 'a').write(f'vLLM up: {{server.base_url}} tp={{tp}} gpus={{gpus}} model={{MODEL_PATH}}\\n')
except Exception:
    # Python errors here never reach notebook.log otherwise; record them plus what the inputs look like.
    open(LOG, 'a').write('START_VLLM FAILED\\n' + traceback.format_exc())
    sh('find /kaggle/input -maxdepth 6 -path "*models*" | head -40', check=False)
    raise
finally:
    if server is not None and getattr(server, 'log_path', None):
        shutil.copy(server.log_path, '/kaggle/working/vllm.log')
sh(f'python scripts/make_agents.py --model {{MODEL}}')"""

SUMMARY = """import json
sh('tar czf /kaggle/working/results.tgz results')
for f in sorted(glob.glob('results/*/runs.jsonl')):
    rows = [json.loads(line) for line in open(f)]
    print(f, sum(r['resolved'] for r in rows), '/', len(rows))
    for r in rows:
        print('   ', r)"""

if MODE == "gpu":
    name, kernel = "gpu", "g4swe-gpu"
    cells = [
        ("markdown", f"# Agent runs on the Kaggle-hosted competition model\n\n"
         f"Serves `{GPU_MODEL}` with vLLM on the attached GPUs (as in the official getting-started notebook) "
         "and runs agent config k0 through the official `swegemma` harness.\n\n"
         "Code: https://github.com/TechNaom/gemma4-agentic-swe"),
        ("code", SETUP.replace("__GET_CODE__", GET_CODE_OFFLINE)),
        ("code", INSTALL_FULL_WHEELHOUSE),
        ("code", START_VLLM),
        ("code", f"sh(f'python -m g4swe.run_eval --mode agent --backend local --agent agents/k0 "
                 f"--data-dir {{DATA_DIR}} --task-ids {GPU_TASKS}', check=False)"),
        ("code", SUMMARY),
    ]
    # Same machine and image as the official getting-started notebook. The L4 x4 machine is offline:
    # pushing it with enable_internet=True is rejected (400), as is turning Internet on in the editor.
    meta_extra = {
        "enable_gpu": True,
        "enable_internet": False,
        "machine_shape": "NvidiaL4",
        "docker_image": OFFICIAL_IMAGE,
        "dataset_sources": ["metric/gemma-4-developer-agent-wheelhouse", CODE_DATASET],
        "model_sources": [f"google/gemma-4/Other/{GPU_MODEL}/2"],
    }
elif MODE == "faults":
    name, kernel = "faults", "g4swe-faults"
    cells = [
        ("markdown", "# Planted-bug benchmark (piece B)\n\n"
         "Breaks each valid task's reference patch in one small way (7 operators, `src/g4swe/faults.py`) and "
         "verifies every mutant with the official harness. A mutant that still resolves is a broken fix the "
         "tests cannot catch.\n\nCode: https://github.com/TechNaom/gemma4-agentic-swe"),
        ("code", SETUP.replace("__GET_CODE__", GET_CODE_ONLINE) + "\n" + INSTALL_HARNESS_ONLY),
        ("code", "sh(f'python -m g4swe.faults --tasks {DATA_DIR}/tasks.jsonl "
                 "--task-file experiments/valid_tasks.txt --out faults/patches')\n"
                 "sh(f'python -m g4swe.run_eval --mode patch --patch-dir faults/patches "
                 "--data-dir {DATA_DIR} --task-file experiments/valid_tasks.txt', check=False)\n"
                 "sh('cp faults/manifest.jsonl results/')"),
        ("code", SUMMARY),
    ]
    meta_extra = {"enable_gpu": False, "model_sources": []}
else:
    name, kernel = "smoke", "g4swe-smoke"
    cells = [
        ("markdown", "# Smoke test: swegemma harness + hosted Gemma 4\n\n"
         "Audit mode verifies every task with its reference patch (should resolve) and an empty patch "
         "(should not). Agent mode runs config k0 with `gemma-4-31b-it` via the Gemini API.\n\n"
         "Code: https://github.com/TechNaom/gemma4-agentic-swe"),
        ("code", SETUP.replace("__GET_CODE__", GET_CODE_ONLINE) + "\n" + INSTALL_HARNESS_ONLY),
    ]
    if MODE == "audit":
        cells.append(("code", "sh(f'python -m g4swe.run_eval --mode gold  --data-dir {DATA_DIR}')\n"
                              "sh(f'python -m g4swe.run_eval --mode empty --data-dir {DATA_DIR}')"))
    else:
        cells.append(("code", """try:
    from kaggle_secrets import UserSecretsClient
    os.environ['GEMINI_API_KEY'] = UserSecretsClient().get_secret('GEMINI_API_KEY')
except Exception as e:
    open(LOG, 'a').write(f'GEMINI_API_KEY secret not available: {e!r}\\n')
    print('GEMINI_API_KEY secret not available:', repr(e))
sh(f'python -m g4swe.run_eval --mode agent --agent agents/k0 --data-dir {DATA_DIR} --task-ids rich_2725', check=False)"""))
    cells.append(("code", SUMMARY))
    meta_extra = {"enable_gpu": False, "model_sources": []}


def cell(kind, src):
    c = {"cell_type": kind, "metadata": {}, "source": src}
    if kind == "code":
        c.update(execution_count=None, outputs=[])
    return c


nb = {
    "cells": [cell(k, s) for k, s in cells],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}
out = Path(__file__).resolve().parents[1] / "notebooks" / name
out.mkdir(parents=True, exist_ok=True)
(out / f"{name}.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")
(out / "kernel-metadata.json").write_text(json.dumps({
    "id": f"{USER}/{kernel}",
    "title": kernel.replace("-", " "),
    "code_file": f"{name}.ipynb",
    "language": "python",
    "kernel_type": "notebook",
    "is_private": True,
    "enable_internet": True,
    "dataset_sources": ["metric/gemma-4-developer-agent-wheelhouse"],
    "competition_sources": ["gemma-4-developer-agent"],
    "kernel_sources": [],
    **meta_extra,
}, indent=2), encoding="utf-8")
print("wrote", out / f"{name}.ipynb")
