Before measuring agents, I measured the public benchmark. Here are the results, with all code and data open, in line with the competition's public-sharing rule.

**Repo:** https://github.com/TechNaom/gemma4-agentic-swe (Apache-2.0)

## 1. Only 68 of 129 public tasks are valid locally

I ran every public task through the official harness twice: once with its **reference (gold) patch**, which should pass, and once with an **empty patch**, which should fail. A task can separate a good agent from a bad one only if both hold.

| Repo | Tasks | Gold passes | Empty passes | Valid |
|---|---|---|---|---|
| fastapi | 67 | 31 | 2 | 29 |
| rich | 48 | 39 | 0 | 39 |
| requests | 13 | 3 | 3 | 0 |
| httpx | 1 | 0 | 0 | 0 |
| **Total** | **129** | **73** | **5** | **68** |

- **34 gold failures come from two test libraries missing from the provided wheels:** `inline_snapshot` (27 tasks) and `dirty_equals` (7 tasks).
- 13 tasks fail even with the reference fix, 7 time out and 2 fail for other reasons.
- 5 tasks pass with **no patch at all**.

**Practical tip:** if you tune on the public tasks, use only the 68 valid ones (listed in `experiments/valid_tasks.txt`). Otherwise part of your local score is noise. I don't know whether the hidden environment has the same gaps.

## 2. The tests accept some broken fixes

I planted 163 known bugs into the gold patches, using 7 mutation types, and re-scored every one with the official harness. After a hand review that removed equivalent mutants, **24 of 163 broken fixes (14.7%) were still marked resolved**.

- Inverted booleans escaped most often (53% before review), then off-by-one errors (33%).
- Removed `raise` statements were always caught.

So any resolve rate is an upper bound on truly correct fixes.

## 3. Code-graph tools did not help our agent

Results on the 68 valid tasks, with `gemma-4-31b-it-qat-w4a16-ct` on 4x L4:

| Agent | Tools | Resolved |
|---|---|---|
| k0 | 6 workspace tools only | **50%** (34/68) |
| k4 | k0 + all three graph tools | 47% (32/68), McNemar p = 0.69 |
| n4 | k4 + a prompt nudging graph-tool use | 44% (14/32) |

The agent called a graph tool in fewer than 10% of runs unless told to. Nudging it raised usage but cost more tokens and delayed the first edit, without solving more tasks.

## 4. A warning: public-set results did not transfer

- Our 50% public-set agent **timed out** on the hidden set at 15 minutes per task (the limit is 12 hours in total).
- With a 5-minute cap and **thinking off**, it scored only **0.05** on the public leaderboard.

The hidden tasks come from private repositories and behave very differently from the public ones, so don't rely on public-set tuning alone. We are now testing the same agent with thinking turned on and will post the result here.

## What's in the repo

- `agents/`: all 11 agent configs (k0 to k5, n1 to n5)
- `experiments/audit-2026-10-15/`: the full gold/empty audit
- `experiments/faults-2026-10-23/`: the planted-bug set and its hand review
- `experiments/g4swe-*`: every run summary, trace and patch
- `src/g4swe/`: the runner, including a CPU-only `patch` mode that re-verifies saved patches without a GPU
- `submission/main-k0/`: our exact submitted config

The full write-up is on the Paper Track. Questions and corrections are welcome, especially if your audit results differ from ours.
