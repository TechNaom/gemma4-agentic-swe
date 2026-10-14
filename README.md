# gemma4-agentic-swe

**Open research on making a single-accelerator open model a reliable software-engineering agent.**

This repo is our entry for Google DeepMind's
[Gemma 4 Developer Agent Paper Track](https://www.kaggle.com/competitions/gemma-4-developer-agent-paper)
on Kaggle. It may also feed the companion
[Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent).
Everything is done in the open: the method, the experiments, the raw numbers, and the parts that didn't work.

> **Status: planning.** No code or results yet. The research direction is being chosen; see [docs/plan.md](docs/plan.md).

## Why

The best coding agents today run on large cloud models. This project asks how far a model
that fits on consumer hardware can go on real repository issues, and which techniques
(post-training, tooling, code graphs, evaluation) close the gap. The results should be
reproducible on free Kaggle compute.

## The setting

| | |
|---|---|
| Model | `gemma-4-31b-it-qat-w4a16-ct` (the only variant the competition harness supports) |
| Agent format | Google ADK Agent Config (`agent.yaml`) with optional prompts, sub-agents, skills and PEFT LoRA adapters |
| Harness tools | `run_command`, `read_file`, `edit_file`, `write_file`, `submit_patch`, `get_status`, plus code-graph tools `get_code_neighbors`, `search_similar_code`, `get_code_subgraph` |
| Scoring (main track) | SWE-bench style: the patch is applied, the issue's tests run, pass/fail; 12-hour total budget |
| Compute | Kaggle notebooks (L4x4, 96 GB GPU memory, no internet) |

## Timeline

| Date (23:59 UTC) | Milestone |
|---|---|
| 2026-10-15 | Project start |
| 2026-11-10 | Internal target: paper final |
| **2026-11-12** | **Paper track deadline** |
| 2026-11-25 | Main competition: entry and team-merger deadline |
| 2026-12-02 | Main competition: final submission |

## Repository layout (planned)

```
docs/        plan, design notes, experiment log
paper/       the writeup (max 3,000 words) and figures
src/         research code
agent/       the ADK submission (agent.yaml, prompts, skills, adapters)
notebooks/   public Kaggle notebooks to reproduce every number
```

## Principles

- **Reproducible:** every reported number links to the notebook and config that produced it.
- **Honest:** negative results and failure analyses are reported, not hidden.
- **Cheap:** everything runs on free or near-free compute.

## License

[Apache 2.0](LICENSE). Gemma models are subject to the [Gemma Terms of Use](https://ai.google.dev/gemma/terms).
