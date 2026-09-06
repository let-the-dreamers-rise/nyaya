# Nyaya

**ARC-AGI-3 was solved this year for about $119 a game. This is the
measurement of what happens when you spend less.**

*(nyaya — NYAH-yuh — the Indian school of logic; literally "method, rule". Not
affiliated with Nyaaya, the Indian legal-information nonprofit.)*

In July 2026 two systems put frontier language models inside a world model's
learning loop and largely closed ARC-AGI-3: Tycho reaches 100.00 RHAE on the
public set, OPINE-World solves 20 of 25 games. In the same papers, program
synthesis without a model in the loop clears **zero levels**.

So capability is no longer the open question. **Price is.** Tycho's authors
list the exclusion of inference cost from their metric as a limitation;
OPINE-World reports no cost at all. Nobody has drawn the curve of quality
against spend — which is exactly the curve that decides whether any of this
runs on a phone, offline, for someone nobody is billing.

This repository is the cheap end of that curve, instrumented: a dependency-free
Python runtime that learns environment rules — or the shape of a scam — from a
handful of examples, on CPU, in seconds, for **zero tokens**, and stores what
it learned as *a page of Python you can read, edit and own*.

A behaviour you cannot read is a behaviour you cannot trust. A skill that is a
file on your own device is a skill nobody can revoke.

---

## Sixty seconds

```bash
git clone https://github.com/let-the-dreamers-rise/nyaya && cd nyaya
python -m bench.run --corpus bench/corpus-heldout
```

```text
corpus: 25 episodes, 3318 transitions
protocol: predict before learning; threshold F1 >= 0.5

method                 exact      F1    tokens   ms/step  reached  median
-------------------------------------------------------------------------
copy-forward             6%   0.000         0      0.00     0/25      --
nyaya-templates          6%   0.253         0      4.96     5/25      44
```

No GPU, no network, no API key, no pip install. That is a real point on the
cost curve: **F1 0.253 for $0.00**, on 25 episodes the learner was never
developed against. Nineteen of twenty-five never reach threshold at all, and
the harness says so rather than hiding it.

The corpus, the protocol and the rules that keep the scoreboard honest are in
[`bench/README.md`](bench/README.md). Adding a method takes ten lines.

## The state of the field, verified

| System | Model in the loop | Result | Cost/game | Code |
|---|---|---|---|---|
| Tycho | Opus 5 | **100.00 RHAE**, 183/183 levels | ~$119 | Apache-2.0 |
| Tycho | GPT-5.6 Sol | **100.00 RHAE**, 183/183 levels | ~$179 | Apache-2.0 |
| OPINE-World | Opus 4.8 | 20/25 games, 160/183 levels | not reported | none |
| WorldCoder *(as run by OPINE-World)* | — | **0 levels** | — | public |
| **nyaya** | **none** | 2–4 early levels; F1 0.253 | **$0** | MIT |

Caveats that matter and are easy to lose: the 100% runs are on the **public**
set and are **warm**. The semi-private leaderboard sat at 62.7% for the best
model in the world on 4 September 2026. Generalisation is not solved.

Full citations, the three caveats in detail, and the claims this evidence
forced us to **retract from our own earlier drafts**, are in
[`docs/LANDSCAPE.md`](docs/LANDSCAPE.md).

## The same idea, small enough to run on a phone

The runtime learns readable rules from labelled text as well as from
interaction. This is the demonstration that the zero-dollar end of the curve
reaches real hardware — not a second product.

```bash
python -m nyaya learn data/sms.tsv -o skill.py
python -m nyaya explain skill.py "Congratulations! You won a prize, text WIN to 87121 to claim"
```

```text
verdict: FLAG (score 5, threshold 1)
  +3  contains an SMS shortcode to text        (accuses)
  +1  claims the reader won a prize or lottery (accuses)
  +1  contains the word 'claim'                (accuses)
```

### And here is the baseline that beats it

```bash
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

**Naive Bayes wins on F1 by 0.09 and trains thirty times faster.** We publish
that because you would have run it in five minutes and because it is the
actual result: on this dataset, *readability costs about nine points of F1 and
sixteen points of recall.* That price is the interesting number, it was never
published before, and closing that recall gap while keeping the rules readable
is a stated research question rather than a claim already won.

What 7,930 naive-Bayes weights cannot do is be opened, understood, argued with
or edited by the person they are protecting. Forty-six sentences can. Delete a
line from `skill.py` and the verdict changes — `python demo_scam.py` ends by
doing exactly that.

## Use it from an agent (MCP)

The runtime ships an MCP server, so any agent can learn a skill and hand the
file to its user. Standard library only — a runtime that claims to need no
dependencies should not acquire one just to be reachable.

```bash
claude mcp add nyaya -- python -m nyaya.mcp_server
```

Three tools: `learn_skill` (labelled examples in, a page of readable Python
out, with held-out metrics), `screen_message` (a verdict plus every rule that
fired and why), and `list_beliefs` (audit a filter before trusting it — it
will show you the corpus's biases as plain sentences).

```text
FLAG (evidence 5, threshold 1)

   +3  contains an SMS shortcode to text
   +1  claims the reader won a prize or lottery
   +1  contains the word 'claim'

Every line above is a reason, not a score. If one of them is wrong, it is
one line to delete.
```

Nothing is uploaded and no model is called: the learning happens on the CPU of
whoever ran the server.

## Who this is for, specifically

Not "everyone". Today there is exactly one user this repository serves well,
and they are nameable:

**A researcher or engineer comparing world-model methods.** They have a method
and no way to place it against anyone else's, because every paper in this
literature evaluates on its own setup with its own protocol and no shared
denominator. `bench/` gives them a fixed versioned corpus, a causal-replay
protocol, a null baseline that scores 0.000 by construction, and a cost column
nobody else reports. Adding their method takes ten lines.

That user is findable by name: the authors of Tycho, OPINE-World, PoE-World and
the executable-world-model line; ARC Prize 2026 Paper Track entrants; anyone
building agents that must run without an API bill. The substrate's own rules
require sending each author their result and the command that produced it
before publishing, so the first outreach list *is* the user list.

**The loop:** add a method, run the protocol, compare, publish, argue. Every
method added makes the comparison more valuable to the next person, which is
the only compounding asset here — a benchmark accrues, a runtime does not.

**Everyone else is downstream and honest about it.** The person receiving a
scam SMS is who the mission is for; they are served by a product that does not
exist yet, gated partly behind Android platform policy, and this README will
not pretend otherwise.

## How it works, in three sentences

1. **Watch** — every interaction, or every labelled example, is folded into a
   factored symbolic theory (what moves, what blocks, what depletes; which
   patterns accuse and which vouch) by voting, with held-out verification
   before anything is believed.
2. **Compile** — what survives verification is emitted as small readable
   programs: inspectable, editable, portable across models, zero inference cost
   to re-run.
3. **Delegate** — a language model, where present at all, proposes goals and
   reads anomalies; it never does the routine thinking. That is why actions
   cost milliseconds instead of tokens.

## What is in the box

- [`bench/`](bench/README.md) — the substrate: 50 episodes across two corpora,
  causal-replay protocol, method registry, **cost reported next to quality**.
- `nyaya/world_model.py` — the theory learner for interactive environments:
  body, movement, blocking with an exoneration rule, click effects, autonomous
  movers, decay. Zero imports, injectable into restricted sandboxes as source.
- `nyaya/executor.py` — policies an agent names instead of moves
  (`learn_controls`, `auto_route`, `auto_solve`): one call runs hundreds of
  verified environment actions.
- `nyaya/skill.py` — **the shared artefact both learners return.** A `Skill` is
  beliefs plus provenance: each belief a human sentence carrying its evidence,
  the whole thing renderable as editable Python and portable as JSON. Learned
  physics ("UP moves it by -1 rows and 0 columns") and a learned scam filter
  ("asks for a fee to claim a prize, +3") are the same type, which is what
  makes the first line of this README a fact about the code rather than a
  metaphor.
- `nyaya/sms_rules.py` — rule induction from labelled text; every rule a human
  sentence with the evidence that earned it.
- `nyaya/cli.py` — `nyaya learn | eval | classify | explain`.
- `nyaya/mcp_server.py` — the MCP server above: stdio JSON-RPC, stdlib only.
- `docs/demo/index.html` — the belief ledger: all 47 rules, switch any off,
  watch the verdict change. Same rules and same scoring as the Python.
- `scripts/text_baselines.py` — the comparisons a reviewer would run.
- **170 tests. MIT. Python ≥ 3.9, standard library only.**
- [`docs/`](docs/README.md) — indexed by reader: what to read if you are
  checking the claims, judging the research, or deciding whether to fund it.

## Roadmap (statuses are honest)

| Stage | What | Status |
|---|---|---|
| C0 | Shared evaluation substrate: two corpora, causal-replay protocol, cost as a scored column | **shipped** — [`bench/`](bench/README.md), run it now |
| C1 | The cost-capability curve: every method with public code under one protocol, including Tycho at the expensive end | next; the substrate it needs exists |
| C2 | Bending the curve — DSL synthesis, library growth from the agent's own failures | proposed, with falsifiable predictions and the ways it could fail, in [`docs/RESEARCH.md`](docs/RESEARCH.md) |
| MVP | The CLI above, hardened; skills with provenance | live in this repo |
| Vertical | On-device scam screening, India-first (live-call screening is gated by Android platform policy and is a partnership milestone, not an app-store feature) | bridge artefact measured; product not started |

## Relationship to grant programmes

This repo is the core runtime behind two independent funding applications, and
both reviewers deserve to see that plainly rather than discover it:

- **Sentient Foundation (Open Source AGI programme)** — the cost-capability
  frontier, and skills as the loyal behaviour layer above the weights. Spine:
  [`docs/RESEARCH.md`](docs/RESEARCH.md); ask: [`docs/ASK.md`](docs/ASK.md).
- **Autonomys (Subspace Foundation grants)** — *Auto Evolve*, a proposed
  integration anchoring skills, their evidence and their lineage on Autonomys'
  permanent storage and identity stack. Nyaya is the engine; Auto Evolve is that
  engine plus their chain. Research: [`docs/AUTONOMYS.md`](docs/AUTONOMYS.md).

Same engine, two completions. Neither application claims work the other did.

## Status, for anyone deciding whether to bet on this

Solo founder, India. Pre-users; public since 31 August 2026. Everything above
regenerates from a command in this repo. When the evidence went against us — as
it did in September 2026, when a novelty check refuted the headline claim of
our own draft — the retraction was written down and published rather than
edited out. See [`docs/LANDSCAPE.md`](docs/LANDSCAPE.md).

## Licence

MIT, corpus included. The ARC-AGI-3 logs were produced with the TAAF/Duck
harness (Apache-2.0, Tufa Labs) driving a Qwen model; this runtime contains
none of that code and runs anywhere Python runs.
