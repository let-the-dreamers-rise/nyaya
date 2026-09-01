# Nyaya

**Agents that compile experience into rules.**

A dependency-free Python runtime for sample-efficient agents on hardware
people actually own. It learns the rules of an environment -- or the shape of
a scam -- from a handful of examples, on CPU, in seconds, and stores what it
learned as **a page of Python the user can read, edit, and truly own**.

A behaviour you cannot read is a behaviour you cannot trust. A skill that is
a file on your own device is a skill nobody can revoke. Loyal AI, at the
layer above the weights: the user owns what the agent learns.

*Nyaya*: the Indian school of logic -- literally "method, rule".

---

## Sixty seconds to the point

```bash
git clone https://github.com/let-the-dreamers-rise/nyaya && cd nyaya
python -m nyaya learn data/sms.tsv -o skill.py
python -m nyaya explain skill.py "Congratulations! You won a prize, text WIN to 87121 to claim"
```

```text
held-out: precision 100.0%  recall 77.8%  F1 0.875  accuracy 96.8%  (n=1115)
learned 47 rules (6 accusing, 41 vouching) from 5574 examples in 1.08s on CPU

verdict: FLAG (score 5, threshold 1)
  +3  contains an SMS shortcode to text        (accuses)
  +1  claims the reader won a prize or lottery (accuses)
  +1  contains the word 'claim'                (accuses)
```

No GPU, no network, no weights, no pip dependencies. Open `skill.py`: every
belief is a sentence with the training evidence that earned it. Delete a
line and the verdict changes -- that is what owning a skill means.

Two more demos: `python demo.py` (the runtime meets a game it has never
seen, learns its physics from 8 probes, clears the level with zero LLM
calls) and `python demo_scam.py` (the full scam-screening story, including
adapting to Indian scam patterns from 32 local examples).

## The numbers, with denominators

Every claim here has a harness behind it in this repo or its research
corpus. Nothing is rounded up.

| Claim | Measurement |
|---|---|
| Scam skill learned from real data | 46-47 readable rules from 4,459-5,574 labelled SMS (public UCI corpus) in ~1-2s on CPU |
| Held out on real messages | precision **100.0%**, recall 77.8%, F1 0.875 (n=1,115) |
| Few-shot domain adaptation | 32 Indian-pattern examples lift recall 81% -> 94% (illustrative seed set, n=32) |
| Agent cost collapse | stock 27B agent: ~441 tokens of reasoning per action, budget exhausted in all 25 games; with the runtime carrying physics and search: ~0 tokens at 1.4 ms/action |
| No-LLM capability | the symbolic runtime alone clears early levels on 2-4 of 25 ARC-AGI-3 public games per run, including games the LLM-driven agent never cleared |
| Honest status | ARC-AGI-3 leaderboard scores sit in the low single digits of a possible ~115 for everyone; ours included. The contribution is a mechanism and a measurement, not a solved benchmark |

## How it works, in three sentences

1. **Watch:** every interaction (or labelled example) is folded into a
   factored symbolic theory -- what moves, what blocks, what depletes; or
   which patterns accuse and which vouch -- by voting, with held-out
   verification before anything is believed.
2. **Compile:** what survives verification is emitted as small readable
   programs (skills), not weights -- inspectable, editable, portable across
   models, zero inference cost.
3. **Delegate:** an LLM, where present at all, proposes goals and reads
   anomalies; it never does the routine thinking. That is why actions cost
   milliseconds instead of tokens, and why the whole thing runs on a phone-
   class CPU.

## What is in the box

- `nyaya/world_model.py` -- the theory learner for interactive environments:
  body, movement, blocking (with an exoneration rule), click effects,
  autonomous movers, decay. Zero imports, injectable into restricted
  sandboxes as source.
- `nyaya/executor.py` -- policies an agent names instead of moves
  (`learn_controls`, `auto_route`, `auto_solve`...): one call runs hundreds
  of verified environment actions.
- `nyaya/sms_rules.py` -- rule induction from labelled text: every rule a
  human sentence with its evidence; skills rendered as editable Python.
- `nyaya/cli.py` -- `nyaya learn | eval | classify | explain`, the tool a
  stranger can point at their own TSV in one minute.
- `nyaya/delegation.py` -- injects the runtime into an LLM harness's
  sandbox and corrects its prompt.
- 100 tests. MIT. Python >= 3.9, stdlib only.

## Roadmap (statuses are honest)

| Stage | What | Status |
|---|---|---|
| C0 | A shared evaluation substrate for programmatic world models: 24,499+ recorded ARC-AGI-3 transitions, causal-replay protocol, head-to-head of every method with released code -- including cost per hypothesis revision, the axis nobody reports | corpus + harness exist in the research repo; packaging for release is next |
| C1-C3 | DSL synthesis, library learning (the hypothesis class grows from the agent's own failures), active experiment design | proposed -- see `docs/RESEARCH.md`, with falsifiable predictions and the ways it could fail stated |
| MVP | The CLI you just ran, hardened; skills with provenance | live in this repo |
| Vertical | On-device scam screening for SMS/links/forwards, India-first (live-call screening is gated by Android platform policy and is a partnership milestone, named honestly as such) | bridge artefact measured; product not started |

## Relationship to grant programmes (stated plainly)

This repo is the core runtime behind two independent funding applications,
and both reviewers deserve to see that clearly rather than discover it:

- **Sentient Foundation (Open Source AGI programme):** Nyaya as research --
  programmatic world models with no language model in the learning loop, and
  skills as the loyal behaviour layer above the weights. Spine:
  [`docs/RESEARCH.md`](docs/RESEARCH.md), ask: [`docs/ASK.md`](docs/ASK.md).
- **Autonomys (Subspace Foundation grants):** *Auto Evolve* -- a proposed
  integration that anchors these skills, their evidence and their lineage on
  Autonomys' permanent storage and identity stack (Auto Drive, Auto ID,
  Auto EVM), so learned knowledge becomes cumulative and verifiable across
  agents. Nyaya is the engine; Auto Evolve is that engine plus their chain.
  Research: [`docs/AUTONOMYS.md`](docs/AUTONOMYS.md).

Same engine, two different completions. Neither application claims work the
other did; both link here.

## Status, for anyone deciding whether to bet on this

Solo founder, India. Pre-users -- the repo went public on 31 August 2026.
What exists is measured and reproducible; what does not exist yet is labelled
roadmap. Instruments first: every number above can be regenerated by a
command in this repo, and negative results get reported in the same voice as
positive ones.

## Licence

MIT. The ARC-AGI-3 measurements were made with the TAAF/Duck harness
(Apache-2.0, Tufa Labs) driving a Qwen model; this runtime contains none of
that code and runs anywhere Python runs.
