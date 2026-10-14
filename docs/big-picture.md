# The big picture

A guide to what this project is, how the pieces fit, and what carries over to future projects.
Read it top to bottom once (about 20 minutes), then use it as a map.

---

## 1. The project in one minute

**The competition.** Kaggle and Google run a challenge: build an AI agent, powered by Gemma 4, that fixes real
bugs in real Python projects (fastapi, rich, requests, httpx). An agent gets a bug report, explores the code,
edits files, runs tests, and submits a fix. A harness scores the fix by running hidden tests.

**The paper track (what we're entering).** Instead of chasing the leaderboard, we write a 3,000-word research
paper that teaches the community something new about building such agents. It is due **2026-11-12**; we aim for
**2026-11-10**.

**Our question.** *Which code-graph tools actually help a Gemma 4 coding agent, and can we trust the
scoring that tells us so?*

---

## 2. Key ideas, in plain words

| Term | What it means | Everyday analogy |
|---|---|---|
| **LLM** | A model that predicts text. Gemma 4 is Google's open one. | A very well-read assistant |
| **Agent** | An LLM in a loop: think → use a tool → look at the result → repeat until done. | An assistant who can also use a computer, not just talk |
| **Tool** | A function the agent may call: `read_file`, `edit_file`, `run_command`, ... | The apps on that computer |
| **Code graph** | A map of which function calls which. Our 3 graph tools query it. | A city map instead of walking every street |
| **Embedding** | A list of numbers describing a piece of code, so similar code has similar numbers. | Finding books "like this one" in a library |
| **Harness** | The program that runs the agent on a task and scores the result. Here: `swegemma`. | The exam hall and the examiner |
| **Sandbox** | An isolated copy of the repo where the agent can do anything without harming the real system. | A practice kitchen |
| **Patch** | The diff of what the agent changed. That's what gets scored. | The answer sheet |
| **Gold patch** | The real fix the project's developers wrote. Known to be correct. | The answer key |
| **Verifier** | Whatever decides if a patch is right. Here: run tests; pass = resolved. | The examiner's marking scheme |
| **Trace** | A full recording of an agent run: every thought, tool call and result. | A dashcam |
| **Ablation** | Remove or add one component at a time and measure the effect. | Cooking the same dish with and without one spice |
| **Resolution rate** | Share of tasks fixed. The competition's score. | Exam percentage |

---

## 3. How a single run works

```
 bug report ──► AGENT (Gemma 4) ◄──────────────┐
                   │ picks a tool               │ tool result
                   ▼                            │
             SANDBOX copy of repo ──────────────┘
             (read, edit, run tests)
                   │ agent calls submit_patch
                   ▼
               PATCH (diff)
                   │
                   ▼
   FRESH sandbox: apply patch + hidden tests ──► pass = resolved ✅  / fail ❌
```

Two separate sandboxes matter: the agent never sees the hidden tests, and it can't cheat by editing them.
The harness even throws away any changes to test files.

---

## 4. Our three pieces and how they connect

| Piece | Question it answers | What we build | Prize it aims at |
|---|---|---|---|
| **C · Ablation** | Do graph tools help? Which one, on which repo? | 6 agent setups (k0–k5), identical except tools; run each on the same tasks | Best Paper |
| **A · Record & replay** | Can anyone re-check our results cheaply? | Save every run (trace + patch); re-score it later without calling the model | Best New Resource |
| **B · Verifier stress test** | Is the scoring itself trustworthy? | Feed the verifier known-good, empty, and deliberately broken patches | Best Paper / Resource |

```
   C runs the agents ──► A records every run ──► B checks the verdicts
         ▲                                              │
         └──────── trusted results feed the paper ◄─────┘
```

The six setups:

| Setup | Tools on top of the basics |
|---|---|
| k0 | none (baseline) |
| k1 | `get_code_neighbors` (who calls what) |
| k2 | `search_similar_code` (embedding search) |
| k3 | `get_code_subgraph` (how a set of functions connect) |
| k4 | all three |
| k5 | all three + a read-only helper agent |

Same prompt, same model, same tasks, same budget. Only the tools change. That is what makes it a fair
experiment: any difference in score comes from the tools.

---

## 5. What we've done so far (2026-10-15)

1. **Chose the direction**: all three pieces combined (owner's call; originally only A was suggested).
2. **Set up access**: Gemini API key (hosted Gemma 4, free) and Kaggle token, both in a gitignored `.env`.
3. **Read the competition data**: 129 practice tasks, repo snapshots, code graphs, embeddings, harness guide.
4. **Found the official harness** (`swegemma`) on Kaggle and made it call Gemma 4 through the Gemini API.
   Proved tool calling works with a tiny test.
5. **Built the experiment**: 6 agent setups, a runner (`src/g4swe/run_eval.py`), a Kaggle notebook.
6. **First sandbox check**: on fastapi_15661 the gold patch passes and an empty patch fails (good). On
   requests_7505 *even the gold patch fails*: a scoring problem, not an agent problem. A full check of all
   129 tasks is running.

That last point is already a research finding: **if the answer key fails the exam, every agent looks worse
than it is.** It's the same lesson as the LinkedIn engine, where a code rule (not the model) caused false rejects.

---

## 6. Where everything runs

| Place | What runs there | Why |
|---|---|---|
| Your laptop | Writing code, git, small tests, analysis | No GPU, Windows, 12 GB RAM; fine for light work |
| Gemini API (Google) | The Gemma 4 model itself | Free, no hardware needed |
| Kaggle notebooks | The sandbox and tests | Linux machines, free, have the competition data |
| GitHub (public repo) | All code, docs, results | Reproducibility and your portfolio |

---

## 7. Lessons that carry over to any future project

1. **Question first, tools second.** "Which tools help and is the score trustworthy?" is a better project than
   "build an agent". A sharp question decides everything else.
2. **Check the measuring stick.** Before trusting any score, test it with a known-good input (should pass) and
   a known-bad one (should fail). This takes minutes and has already found a problem here.
3. **Change one thing at a time.** Otherwise you can't tell what caused a difference.
4. **Record everything.** Traces and manifests let you answer new questions later without re-running.
5. **Free tiers first, hardware last.** Hosted APIs + free notebooks got us running with zero spend.
6. **Secrets never in git.** `.env` locally, Secrets on Kaggle, a pre-commit hook as a safety net.
7. **Small commits, pushed often.** The repo tells the story of the work.
8. **Reuse official tools.** We use the competition's own harness, so our numbers mean the same as theirs.

---

## 8. Reading list (in this order)

| # | What | Why | Time |
|---|---|---|---|
| 1 | This guide | The map | 20 min |
| 2 | [design.md](design.md) | The detailed plan | 15 min |
| 3 | `D:\gemma-4-developer-agent\HARNESS_README.md`, sections 4–6 and 8 | How runs and scoring work | 40 min |
| 4 | Our prompt: [agents/_template/system.md](../agents/_template/system.md) | What the agent is told | 5 min |
| 5 | SWE-bench paper, Jimenez et al. 2023 ([arXiv:2310.06770](https://arxiv.org/abs/2310.06770)) | The benchmark this competition is built on | 45 min |
| 6 | SWE-agent paper, Yang et al. 2024 ([arXiv:2405.15793](https://arxiv.org/abs/2405.15793)) | Why the agent's tools ("interface") matter so much; closest to our question | 45 min |
| 7 | Agentless paper, Xia et al. 2024 ([arXiv:2407.01489](https://arxiv.org/abs/2407.01489)) | A strong counterpoint: simple pipelines can rival agents | 30 min |
| 8 | Google ADK docs ([google.github.io/adk-docs](https://google.github.io/adk-docs/)) | The agent framework the harness uses | browse |

Tip: use NotebookLM (included with your AI Pro) to load papers 5–7 and ask it questions.

---

## 9. What's next

| When | Step | You'll learn |
|---|---|---|
| Next session | Read the 129-task check results together | How to sanity-check a benchmark |
| Next session | Walk through Gemma 4's first real trace | How an agent actually reasons and fails |
| This week | 10-task pilot across all 6 setups | Running a controlled experiment |
| Week 2 | Full ablation | Statistics: error bars, what counts as a real difference |
| Week 3 | Planted-bug benchmark (B) | How verifiers fail |
| Week 3–4 | Write the paper | Turning results into a clear story |
