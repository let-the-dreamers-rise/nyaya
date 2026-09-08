# Nyaya

**ARC-AGI-3 was solved this year for about $119 a game. This is the
measurement of what happens when you spend less, and how much of an agent a
person can own at $0.**

*(nyaya, NYAH-yuh: the Indian school of logic; literally "method, rule". Not
affiliated with Nyaaya, the Indian legal-information nonprofit.)*

**The whole thing on one page:** [the project site](https://claude.ai/code/artifact/aaf9ecdc-f203-487a-b542-ac370294df33),
also served from [`docs/index.html`](docs/index.html).

In July 2026 two systems put frontier language models inside a world model's
learning loop and largely closed ARC-AGI-3: Tycho reaches 100.00 RHAE on the
public set, OPINE-World solves 20 of 25 games. In the same papers, program
synthesis without a model in the loop clears **zero levels**.

So capability is no longer the open question. **Price is**, and with it
ownership. Tycho's authors list the exclusion of inference cost from their
metric as a limitation; OPINE-World reports no cost at all. Nobody has drawn
the curve of quality against spend, which is the curve that decides whether
any of this runs on a phone, offline, for someone nobody is billing, as a
file nobody can revoke.

This repository is the cheap end of that curve, instrumented: a
dependency-free Python runtime that learns environment rules from a handful
of examples, on CPU, in seconds, for **zero tokens**, and stores what it
learned as *a page of Python you can read, edit and own*. A behaviour you
cannot read is a behaviour you cannot trust.

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

No GPU, no network, no API key. Two rows matter more than ours. **`memorise`
scores 0.024**: it is a lookup table, so its score is the share of the corpus
that is repetition, and almost none of it is. **`last-effect` is a one-line
heuristic** and our learner has not been shown to beat it; on the development
corpus the heuristic wins outright at a fortieth of the cost. Our own
benchmark produced that result the week it was built. See
[`bench/README.md`](bench/README.md).

## How much of an agent can you own at $0? Two percent, today.

The delegation architecture says a frontier model proposes and a world model
that costs nothing per call carries the routine steps. Before asking anyone
to fund that, we measured how many steps the free end can take *now*, on
games it has never seen, with no error:

```bash
python scripts/delegation.py --corpus bench/corpus-heldout
```

```text
method                actions  commits  commit ok  delegable  no-ops
last-effect              3318    22.7%       8.6%       2.0%    6.1%
nyaya-templates          3318    38.1%       2.5%       0.9%    5.2%
dsl-synthesis-rel        3318    59.0%       0.7%       0.4%    2.4%
```

An action is *delegable* when the model committed to a prediction and the
whole frame was right. The learners over-commit: synthesis claims 59% of
actions and is right on 0.7%. The one-line heuristic is the best delegator
in the registry. The curve starts at two percent, and the work is calibrated
commitment. The prediction on record, in
[docs/RESEARCH.md](docs/RESEARCH.md): over 20% delegable at under $1 a game,
or a published reason why not.

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
Citations, caveats, and the two claims this evidence forced us to retract
from our own drafts are in [docs/LANDSCAPE.md](docs/LANDSCAPE.md).

## The same synthesiser, pointed at a phone

The rule search that learns grid physics also reads the bank and UPI
messages already on an Indian phone, on the phone, and says what it noticed:

```bash
nyaya-money serve demo        # or, in Termux on Android: curl -sL .../install-termux.sh | bash
```

```text
  - Rs 12,000 went to kyc.update9@ybl, a first-time recipient, 9 minutes after
    a message that said 'kyc' and 'blocked'. That is the shape of a scam.
  - On Sundays, in the evening, money goes to Zomato. Right 14 of 14 times.
```

No server, no model, no network; a test asserts the page loads nothing from
outside and binds loopback only. It is a demonstration that the free end of
the curve reaches a Rs 8,000 phone, not the product of this repository.
[docs/MONEY.md](docs/MONEY.md) has the steps and what it will never do.

## Labelled text, and the baseline that beats it

```bash
python scripts/text_baselines.py data/sms.tsv
```

```text
method                       precision   recall     F1  readable
nyaya readable rules           100.0%    77.8%  0.875  46 rules
naive-bayes (bag of words)      98.7%    94.4%  0.965  7930 weights
```

**Naive Bayes wins by 0.09 F1.** Readability costs about nine points on this
dataset. That price was never published before, and closing the gap while
keeping the rules readable is a research question, not a claim already won.

## Use it from an agent (MCP)

```bash
claude mcp add nyaya -- python -m nyaya.mcp_server
```

`learn_skill`, `screen_message`, `list_beliefs`. Standard library only;
nothing uploaded, no model called.

## How it works, in three sentences

1. **Watch.** Every interaction, or every labelled example, is folded into a
   factored symbolic theory, with held-out verification before anything is
   believed.
2. **Compile.** What survives is emitted as small readable programs:
   inspectable, editable, portable, zero inference cost to re-run.
3. **Delegate.** A language model, where present at all, proposes goals and
   reads anomalies; it never does the routine thinking. Two percent of it
   today, measured above.

## What is in the box

- [`bench/`](bench/README.md): 50 episodes across two corpora, causal-replay
  protocol, method registry, cost next to quality, two failed attempts at
  library transfer documented with numbers.
- `nyaya/synthesis.py`: the program synthesiser. Separate-and-conquer over a
  registered primitive set; every rule pinned and carrying its evidence.
- `nyaya/world_model.py`, `nyaya/executor.py`: the template learner and the
  policies an agent names instead of moves.
- `nyaya/skill.py`: the shared artefact every learner returns. Beliefs plus
  provenance, renderable as editable Python, portable as JSON.
- `nyaya/money/`: the phone demonstration above.
- `nyaya/mcp_server.py`, `nyaya/sms_rules.py`, `nyaya/cli.py`.
- `scripts/delegation.py`, `scripts/text_baselines.py`: the two comparisons a
  reviewer would run.
- **235 tests. MIT. Python 3.9 or later, standard library only.**
- [`docs/`](docs/README.md), indexed by reader.

## Roadmap (statuses are honest)

| Stage | What | Status |
|---|---|---|
| C0 | Shared evaluation substrate, cost as a scored column | shipped |
| C1 | The cost-capability curve, Tycho at the expensive end, measured not quoted | next; needs compute |
| C2 | Bending the curve: the library grows from the agent's own failures | attempted twice, failed twice, [documented](bench/README.md) |
| C3 | Delegation with calibrated commitment; a small local model routing only what the world model has earned | pilot measured at 2%; the funded work |

## Status, for anyone deciding whether to bet on this

Solo researcher, India. Public since 31 August 2026. Everything above
regenerates from a command in this repo. When the evidence went against us we
published it: a one-line heuristic beats our learner, naive Bayes beats our
rules, two claims were retracted in writing, and the delegation number is two
percent. That record is the reason to trust the rest.

## Licence

MIT, corpus included. The ARC-AGI-3 logs were produced with the TAAF/Duck
harness; see [docs/LANDSCAPE.md](docs/LANDSCAPE.md) for provenance.
