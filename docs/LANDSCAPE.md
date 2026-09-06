# Where ARC-AGI-3 actually stands, September 2026

*Verified 7 September 2026. Every number here is the authors' own, quoted from
their paper or the public leaderboard, with the source named. Nothing in this
file is our measurement, and nothing here was reimplemented by us.*

This document exists because an earlier draft of our own application said
**"nobody has beaten this benchmark, leaderboard scores sit in the low single
digits."** That was true when it was written and it is false now. Rather than
quietly delete the sentence, this file records what replaced it and what that
means for the research we are proposing.

---

## 1. The capability question is largely answered

| System | Model | Games | Levels | Score | Actions | Code |
|---|---|---|---|---|---|---|
| **Tycho** | Opus 5 | 25/25 | 183/183 | **100.00 RHAE** | 6,641 | Apache-2.0 |
| **Tycho** | GPT-5.6 Sol | 25/25 | 183/183 | **100.00 RHAE** | 7,766 | Apache-2.0 |
| **Tycho** | Opus 4.8 | 17/25 top-decile | -- | 88.49 | 10,354 | Apache-2.0 |
| **OPINE-World** | Opus 4.8 | 20/25 | 160/183 | 78.4 AE | -- | none released |
| OPINE-World baseline1 | GPT-5.5 | -- | -- | 63.8 | -- | -- |
| **WorldCoder** (as run by OPINE-World) | -- | 0 | **0** | 0.0 | -- | public |
| Neural latent world models (as run by OPINE-World) | -- | 0 | **0** | 0.0 | -- | -- |
| **nyaya** (ours) | none in the loop | 2-4 early levels | -- | 1.86-3.38 | -- | MIT |

Sources: Tycho, arXiv 2607.28287 (Lehmann, Aioanei, Vahdati; NIMI-research);
OPINE-World, arXiv 2607.01531 (Courtis, Li, Sanner).

Both leading systems are **object-centric programmatic world models with a
large language model inside the learning loop.** OPINE-World couples two
cooperating LLM agents in a hypothesis-and-test loop with replay verification
and CEGIS. Tycho lets an agent model, test, plan with, repair or bypass a
free-form executable hypothesis.

**The uncomfortable line for us:** in OPINE-World's own table, program
synthesis and neural latent world models -- the family our approach belongs to
-- **clear no levels at all.** WorldCoder scores zero. That is direct
disconfirming evidence against any claim that symbolic induction without a
model in the loop wins on capability, and this proposal does not make that
claim.

## 2. Three caveats that keep the question open

**The 100% is on the public set, warm.** Tycho's perfect runs are on the 25
public games, and public runs scoring 100% are *warm* -- the agent carries
learnings from previous runs into the scored one. The semi-private leaderboard
tells a different story:

| Semi-private, as of 4 September 2026 | Score |
|---|---|
| GPT-6 Astra | 62.7% |
| Claude Opus 5 | 30.2% |
| GPT-5.6 Sol | 7.8% |

Generalisation to unseen games is not solved. It is roughly a third to two
thirds solved, depending on the model.

**Single runs, no variance.** OPINE-World reports one run per game and lists
the absence of variance estimates as a limitation. Tycho's headline rows are
single-pass evaluations. Neither is a claim about expected performance.

**The benchmark moved.** The 14 April 2026 changelog changed public scoring,
republished fifteen game versions, switched the human baseline from the
second-best human to the median human per level, and raised the per-level cap
from 1.0x to 1.15x. Numbers from before and after that date are not
comparable, which is itself an argument for a fixed, versioned corpus.

## 3. The axis nobody scores

This is the finding that matters.

| System | Cost per game | Where it is reported |
|---|---|---|
| Tycho (GPT-5.6 Sol) | **$179 mean / $114 median** (~$4,470 total) | a footnote |
| Tycho (Opus 5) | **$119 mean / $97 median** (~$2,990 total) | a footnote |
| OPINE-World | **not reported** | -- |
| nyaya runtime | **$0** (~0 tokens, 1.4 ms/action) | measured, this repo |

Tycho lists, among its own stated limitations, the **exclusion of inference
costs from the action-efficiency metric.** The benchmark's headline metric
measures how *few actions* an agent takes and says nothing about what those
actions cost to produce. So the field's leading result is: this benchmark can
be solved, for about $119 a game, by a frontier model, on the public set, warm.

That is a real and impressive result. It is also **not a result about
intelligence that runs anywhere.** A method costing $119 per game cannot run on
a phone, cannot run offline, cannot run for a user who is not being billed, and
cannot run at all if the provider revokes access -- which is the entire premise
of the programme this proposal is written for.

## 4. What this does to our claims

**Retracted.** "Nobody has beaten this benchmark." False as of July 2026.
Removed from `README.md`, `PITCH.md` and `RESEARCH.md`.

**Retracted.** Any framing in which removing the LLM from the learning loop is
expected to win on capability. The evidence points the other way and we say so.

**Survives, and is stronger.** The cost-capability frontier is unmeasured. Two
of the three leading systems report no cost at all; the third reports it
outside its own metric. Nobody has asked how much prediction quality survives
per dollar, or where a cheap architecture breaks, because nobody has an
instrumented cheap end. We do -- that is what `bench/` is.

**Survives, and is more valuable.** The case for a shared substrate got
stronger, not weaker. OPINE-World released no code and cannot be reproduced by
anyone. Tycho released code under Apache-2.0 and can be. The benchmark's own
scoring changed mid-year. A fixed versioned corpus with a causal-replay
protocol and a cost column is exactly the thing that would let these three
results be compared at all.

**Reframed.** The research question is no longer *can programs learn world
models* -- answered, yes, with frontier models. It is:

> **What is the cheapest architecture that retains the capability, and what
> exactly is lost at each step down the cost curve?**

That question is open, it is measurable, it is the one this repository is
instrumented to answer, and it is the one whose answer decides whether any of
this reaches the people the funder cares about.

## 5. What we do next, concretely

1. **Run Tycho under our protocol.** Its code is public and Apache-2.0, so
   rule 1 of the substrate permits it: run what the authors released, report it
   with its cost, send them the result and the command before publishing.
2. **Quote OPINE-World, never reimplement it.** No code, so it appears in the
   table as the authors' own numbers in their own setup, visually separated.
3. **Fill in the middle of the curve.** Between $119/game with a frontier model
   and $0/game with a fixed hypothesis class there is an unexplored space:
   small local models proposing, programs verifying; synthesis budgets; how
   many levels survive each order-of-magnitude cost reduction. That curve is
   the contribution.
4. **Report the losses.** If nothing survives the cost reduction, that is a
   publishable and useful negative result about the price of open, on-device
   intelligence, and it gets written up in the same voice as a win.

## Sources

- Tycho: [arXiv 2607.28287](https://arxiv.org/abs/2607.28287) -- code at `github.com/NIMI-research/Tycho`
- OPINE-World: [arXiv 2607.01531](https://arxiv.org/abs/2607.01531)
- ARC-AGI-3 leaderboard: [arcprize.org/arc-agi/3/leaderboard](https://arcprize.org/arc-agi/3/leaderboard)
- PoE-World: [arXiv 2505.10819](https://arxiv.org/abs/2505.10819)
- One Life to Learn: [arXiv 2510.12088](https://arxiv.org/abs/2510.12088)
