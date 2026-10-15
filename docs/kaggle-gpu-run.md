# Run the agent on Kaggle's GPU (hands-on guide)

Goal: run our agent (config k0) on two pilot tasks with the competition's own model,
`gemma-4-31b-it-qat-w4a16-ct`, on Kaggle L4 GPUs. You do the clicks; each step says what it does and why.

Time: about 10 minutes of setup, then 20–60 minutes of running.

---

## Part 1: Get a notebook with the right environment

The official notebook already has the right GPU, Python version and inputs, so we start from a copy of it.

1. Open https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent
2. Click **Copy & Edit** (top right). A copy opens in the editor.
3. Rename it at the top: **g4swe gpu run**.
4. Right-hand panel → **Session options**:
   - **Accelerator**: choose the **L4** option (for example *GPU L4 x4*). *Why: the model needs about 17 GB; L4 is what the competition uses.*
   - **Internet**: **On**. *Why: the first cell downloads our code from GitHub.*
5. Right-hand panel → **Input**: check these are listed (they come with the copy):
   - Competition: *Google - The Gemma 4 Developer Agent*
   - Dataset: *gemma-4-developer-agent-wheelhouse*
   - Models: *gemma-4* (the 31B qat w4a16 variant must be among them)
6. **Delete all the existing cells** (click a cell → three-dot menu → Delete cell). We replace them with ours.

---

## Part 2: Add our five cells

Add each as a new **code** cell (**+ Code**), in order. Paste exactly.

### Cell 1: Download our code and find the data

*What it does: clones our GitHub repo, defines a helper `sh()` that runs a shell command and saves its output to `notebook.log`, and finds where Kaggle mounted the competition data.*

```python
import glob, os, subprocess, sys
from pathlib import Path

LOG = '/kaggle/working/notebook.log'

def sh(cmd, check=True):
    # Tee output to notebook.log: Kaggle's API log is often empty.
    with open(LOG, 'a') as log:
        log.write(f'$ {cmd}\n')
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log.write(p.stdout + f'[exit {p.returncode}]\n')
    print('$', cmd, '\n', p.stdout[-3000:], flush=True)
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
os.environ['PYTHONPATH'] = 'src'
```

✅ Expect: a line like `wheelhouse: /kaggle/input/... | data: /kaggle/input/...`

### Cell 2: Install the harness and vLLM

*What it does: installs the competition's packages (the `swegemma` harness, Google ADK, and vLLM, the program that serves the model on the GPU), then shows which GPUs you got.*

```python
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
sh('pip install -q python-dotenv')
sh('nvidia-smi --query-gpu=name,memory.total --format=csv')
```

✅ Expect (takes a few minutes): a list of GPUs at the end, e.g. four lines of `NVIDIA L4, 23034 MiB`.

### Cell 3: Start the model server

*What it does: loads Gemma 4 31B onto the GPUs with vLLM and publishes it at `http://127.0.0.1:8000/v1` under the name our agent asks for. Then it writes the six agent configs (k0–k5) to use this model.*

```python
import torch
from adk_submission import VllmConfig, VllmServer

MODEL = 'gemma-4-31b-it-qat-w4a16-ct'
MODEL_PATH = find_one(f'/kaggle/input/models/**/{MODEL}/*/config.json').parent
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
sh(f'python scripts/make_agents.py --model {MODEL}')
```

✅ Expect (5–15 minutes): `vLLM up: http://127.0.0.1:8000 tp = 4 gpus = 4`, then `k0: baseline...` through `k5: ...`

### Cell 4: Run the agent

*What it does: runs agent k0 (no graph tools) on two pilot tasks. For each one the agent reads the issue, explores the repo, edits code, runs tests and submits a patch; then the harness checks it with hidden tests.*

```python
sh(f'python -m g4swe.run_eval --mode agent --backend local --agent agents/k0 '
   f'--data-dir {DATA_DIR} --task-ids rich_2725 fastapi_14786', check=False)
```

✅ Expect: for each task a line like `resolved=True exit=0 tools=23 412.5s`

### Cell 5: Summarise and package the results

*What it does: bundles everything into `results.tgz` so it can be downloaded, and prints each run.*

```python
import json
sh('tar czf /kaggle/working/results.tgz results')
for f in sorted(glob.glob('results/*/runs.jsonl')):
    rows = [json.loads(line) for line in open(f)]
    print(f, sum(r['resolved'] for r in rows), '/', len(rows))
    for r in rows:
        print('   ', r)
```

---

## Part 3: Run it

Two options:

- **Interactive (recommended the first time):** click **Run All** at the top and watch each cell. If one fails, stop and send me the error text.
- **Background:** **Save Version** → **Save & Run All (Commit)**. It runs even if you close the browser. Results appear under the version's **Output** tab.

---

## Part 4: Read the results

1. **Cell 4's output**: `resolved=True` means the agent's fix passed the hidden tests.
2. **Output** (right panel or the version's Output tab): download `results.tgz` and `notebook.log`.
3. Inside `results/<run>/`:
   - `runs.jsonl`: one line per task (resolved, tool calls, time)
   - `patches/<task>.patch`: what the agent changed
   - `traces/`: every step the agent took. We'll read one together; it's the best way to see how an agent "thinks".

## If something fails

| Symptom | Likely cause | What to do |
|---|---|---|
| `not found: /kaggle/input/**/...` in Cell 1 | An input isn't attached | Right panel → **Input** → add the missing competition, dataset or model |
| `is not a supported wheel on this platform` in Cell 2 | Wrong environment | Make sure you copied the official notebook (Part 1) |
| Cell 3 runs out of memory | Too few GPUs | Check **Accelerator** is an L4 option with several GPUs |
| `resolved=False` in Cell 4 | The agent didn't solve it | Not an error. That's data. We'll read the trace to see why. |
