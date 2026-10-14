# Plan

## Goal

Submit a strong paper to the Gemma 4 Developer Agent Paper Track by **2026-11-12 23:59 UTC**,
judged equally on novelty, quality/generality, relevance, verifiability and clarity.

## Prize categories

- **Best Paper:** an empirical paper with new findings
- **Best New Resource:** a dataset, tool, library or software
- **Best New Application:** a new use case, e.g. using code graphs or the provided embeddings

## Directions under consideration

| | Direction | Category fit | Compute |
|---|---|---|---|
| A | Record-and-replay evaluation tool for tuning local coding agents | Best New Resource | Low |
| B | Seeded-fault benchmark for patch verifiers | Best New Resource | Low to medium |
| C | Ablation of the code-graph tools on agent success | Best Paper | High |

**Decision (2026-10-15):** all three combined. C is the main study, A is its tooling, B checks the verifiers. See [design.md](design.md).

## Paper outline (fixed by the rules)

1. Title and subtitle
2. Abstract
3. Introduction
4. Method and experiments
5. Related work and citations

Optional: a public Kaggle notebook and an arXiv-style PDF.

## Open items

- [x] Choose the direction
- [ ] Accept the rules on both Kaggle competitions
- [ ] Set up the Kaggle API locally; pull the dataset and `HARNESS_README.md`
- [x] Write the design doc for the chosen direction
- [ ] Get a Gemini API key and check Gemma 4 rate limits
- [ ] Test the QAT model in a Kaggle GPU notebook
