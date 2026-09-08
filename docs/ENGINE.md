# The engine, and the research behind it

This is what the README led with until 9 September 2026, moved here so the
README can lead with the thing a person can put on a phone. Nothing below
has been softened.

**The whole thing on one page:** [the project site](https://claude.ai/code/artifact/aaf9ecdc-f203-487a-b542-ac370294df33),
also served from [`index.html`](index.html).

---

**ARC-AGI-3 was solved this year for about $119 a game. This is the
measurement of what happens when you spend less.**

In July 2026 two systems put frontier language models inside a world model's
learning loop and largely closed ARC-AGI-3: Tycho reaches 100.00 RHAE on the
public set, OPINE-World solves 20 of 25 games. In the same papers, program
synthesis without a model in the loop clears **zero levels**.

So capability is no longer the open question. **Price is.** Tycho's authors
list the exclusion of inference cost from their metric as a limitation;
OPINE-World reports no cost at all. Nobody has drawn the curve of quality
against spend, which is exactly the curve that decides whether any of this
runs on a phone, offline, for someone nobody is billing.

This repository is the cheap end of that curve, instrumented: a dependency-free
Python runtime that learns environment rules, or the shape of a scam, from a
handful of examples, on CPU, in seconds, for **zero tokens**, and stores what
it learned as *a page of Python you can read, edit and own*.

## Sixty seconds

```bash
git clone https://github.com/let-the-dreamers-rise/nyaya && cd nyaya
python -m bench.run --corpus bench/corpus-heldout
```

```text
corpus: 25 episodes, 3318 transitions
protocol: predict before learning; threshold F1 >= 0.5

method                 exact      F1          95% CI   tokens  ms/step  reached
--------------------------------------------------------------------------------
copy-forward             6%   0.000     0.000-0.000        0     0.00     0/25
last-effect              8%   0.151     0.065-0.289        0     0.07     6/25
memorise                 8%   0.024     0.009-0.038        0     0.01     0/25
nyaya-templates          6%   0.253     0.039-0.490        0     3.06     5/25
```

No GPU, no network, no API key. Two things in that table matter more than our
own row. **`memorise` scores 0.024**: it is a lookup table, so its score is the
share of this corpus that is repetition. Almost none of it is. **`last-effect`
is a one-line heuristic** and our world-model learner has not been shown to
beat it: the intervals overlap here, and on the development corpus the
heuristic wins outright at a fortieth of the cost per step. That is an
unflattering result about our own method, discovered by our own benchmark, and
it is the best argument for the benchmark that exists. See
[`../bench/README.md`](../bench/README.md).

## The state of the field, verified

| System | Model in the loop | Result | Cost/game | Code |
|---|---|---|---|---|
| Tycho | Opus 5 | **100.00 RHAE**, 183/183 levels | ~$119 | Apache-2.0 |
| Tycho | GPT-5.6 Sol | **100.00 RHAE**, 183/183 levels | ~$179 | Apache-2.0 |
| OPINE-World | Opus 4.8 | 20/25 games, 160/183 levels | not reported | none |
| WorldCoder *(as run by OPINE-World)* | none | **0 levels** | n/a | public |
| **nyaya** | **none** | 2-4 early levels; F1 0.253 (CI 0.039-0.490) | **$0** | MIT |

The 100% runs are on the **public** set and are **warm**. The semi-private
leaderboard sat at 62.7% for the best model in the world on 4 September 2026.
Full citations, caveats, and the claims this evidence forced us to retract are
in [LANDSCAPE.md](LANDSCAPE.md).

## The same idea on labelled text, and the baseline that beats it

```bash
python -m nyaya learn data/sms.tsv -o skill.py
python -m nyaya explain skill.py "Congratulations! You won a prize, text WIN to 87121 to claim"
python scripts/text_baselines.py data/sms.tsv
```

```text
UCI SMS, 4459 train / 1115 held out, seed 7

method                       precision   recall     F1  accuracy   fit s  readable
----------------------------------------------------------------------------------
nyaya readable rules           100.0%    77.8%  0.875     96.8%    1.85  46 rules
naive-bayes (bag of words)      98.7%    94.4%  0.965     99.0%    0.06  7930 weights
hand-written keyword list       63.4%    71.6%  0.672     89.9%    0.00  14 rules
majority class                   0.0%     0.0%  0.000     85.5%    0.00  1 constant
```

**Naive Bayes wins on F1 by 0.09 and trains thirty times faster.** On this
dataset readability costs about nine points of F1 and sixteen of recall. That
price was never published before, and closing the gap while keeping the rules
readable is a research question, not a claim already won. What 7,930 weights
cannot do is be opened by the person they protect. Forty-six sentences can.

## Use it from an agent (MCP)

```bash
claude mcp add nyaya -- python -m nyaya.mcp_server
```

Three tools, standard library only: `learn_skill` (labelled examples in, a
page of readable Python out, with held-out metrics), `screen_message` (a
verdict plus every rule that fired), `list_beliefs` (audit a filter before
trusting it). Nothing is uploaded and no model is called.

## How it works, in three sentences

1. **Watch.** Every interaction, or every labelled example, is folded into a
   factored symbolic theory by voting, with held-out verification before
   anything is believed.
2. **Compile.** What survives is emitted as small readable programs:
   inspectable, editable, portable, zero inference cost to re-run.
3. **Delegate.** A language model, where present at all, proposes goals and
   reads anomalies; it never does the routine thinking.

## What is in the box

- [`bench/`](../bench/README.md): 50 episodes across two corpora, causal-replay
  protocol, method registry, cost reported next to quality.
- `nyaya/synthesis.py`: the program synthesiser; separate-and-conquer over a
  registered primitive set, every rule pinned and carrying its evidence.
  Domain-agnostic on purpose: `grid`, `grid-relative`, and the money
  witness's own primitives all point the same search at different streams.
- `nyaya/world_model.py`: the template learner for interactive environments.
- `nyaya/executor.py`: policies an agent names instead of moves.
- `nyaya/skill.py`: the shared artefact every learner returns. Beliefs plus
  provenance, renderable as editable Python, portable as JSON.
- `nyaya/sms_rules.py`, `nyaya/cli.py`: rule induction from labelled text and
  its command line.
- `nyaya/mcp_server.py`: the MCP server above.
- `nyaya/money/`: the product. See the README.
- `demo/index.html`: the belief ledger, 47 rules, switch any off.
- `scripts/text_baselines.py`: the comparisons a reviewer would run.

## Research roadmap

| Stage | What | Status |
|---|---|---|
| C0 | Shared evaluation substrate, cost as a scored column | shipped |
| C1 | The cost-capability curve: every method with public code under one protocol, Tycho at the expensive end | next; needs compute |
| C2 | Bending the curve: library growth from the agent's own failures | attempted twice, failed twice, documented in [RESEARCH.md](RESEARCH.md) and [`../bench/README.md`](../bench/README.md) |

## Relationship to grant programmes

This engine is behind independent funding applications, and each reviewer
deserves to see that plainly: **Sentient Foundation** (the cost-capability
frontier; [RESEARCH.md](RESEARCH.md), [ASK.md](ASK.md)), **Autonomys**
(*Auto Evolve*, [AUTONOMYS.md](AUTONOMYS.md)), and the **Alliance** accelerator
(the money product in the README). Same engine, different completions; none
claims work another did.
