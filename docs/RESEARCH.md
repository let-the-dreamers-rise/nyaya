# The price of a world model

### Measuring the cost-capability frontier for programmatic world models, and finding the cheapest architecture that still works

A research proposal for the Sentient Foundation Open Source AGI programme.
Written for the technical council rather than for a landing page: the
reviewers include information theorists who wrote the OML papers, and the
right register for them is a precise claim with an experiment attached.

> **This document was rewritten on 7 September 2026** after a novelty check
> that its own previous version demanded. The check overturned the previous
> framing. What replaced it, and the retractions it forced, are recorded in
> [LANDSCAPE.md](LANDSCAPE.md) rather than quietly edited away. The short
> version: ARC-AGI-3 has been solved on the public set by LLM-in-the-loop
> programmatic world models, at roughly $119 a game, and the interesting
> question moved.

---

## 0. The question, in one paragraph

Programmatic world models work. Tycho reaches 100.00 RHAE on the ARC-AGI-3
public set with Opus 5; OPINE-World solves 20 of 25 games. Both put a frontier
language model inside the learning loop, and in OPINE-World's own baseline
table, program synthesis without one clears *no levels at all*. So the
capability question is answered, and it is not answered in our favour.

What is not answered is **the price.** Tycho's runs cost about $119 per game;
its authors list the exclusion of inference cost from the efficiency metric as
an explicit limitation. OPINE-World reports no cost at all. The field has
demonstrated that this class of intelligence *can* be built and has never
measured what it costs to run -- which is precisely the measurement that
decides whether it reaches a phone, an offline clinic, or anyone who is not
being billed by an API. **This proposal measures that frontier and then tries
to move along it.**

## 1. The problem, stated exactly

An agent meeting an unfamiliar interactive environment must infer its
mechanics from a handful of interactions. Current systems -- ours included --
learn **parameters inside a fixed hypothesis class**: which colour is the
body, what displacement each control produces, which colours block, which
colour is being consumed. Given a template library, data selects among
templates.

The failure is total and diagnostic when the true mechanism lies outside that
class. In our own ARC-AGI-3 runs this is visible per level: on the games we
call wall levels, the agent collects thousands of clean transitions and
learns nothing, because no amount of evidence can select a hypothesis the
learner cannot represent. Prediction stays at the copy-forward baseline; the
planner plans confidently inside a model that is structurally wrong.

**This is the boundary that matters for general intelligence.** Not "learn
faster within a class", but *grow the class*. An agent that cannot extend
what it is able to conceive of is a curve-fitter with extra steps.

## 2. Where the field actually is (verified 7 September 2026)

Full citations, caveats and the retractions this forced are in
[LANDSCAPE.md](LANDSCAPE.md). The compressed version:

| Work | What it does | Limitation we build against |
|---|---|---|
| **DreamCoder** (Ellis et al.) | Wake-sleep library learning: solved programs become new primitives, growing the DSL | Offline task batches, not online interaction with an unknown environment |
| **WorldCoder** (NeurIPS 2024) | LLM writes a world model as code; sample-efficient transfer by reusing program fragments; auditable because programs are readable | **LLM in the learning loop** -- every hypothesis revision is a model call |
| **PoE-World** (arXiv 2505.10819) | Products of programmatic experts; data-efficient because synthesis needs less data than gradient training | Authors state it *struggles to scale beyond simple gridworlds* |
| **OPINE-World** (arXiv 2607.01531) | Two cooperating LLM agents, CEGIS synthesis, replay verification, ontology-error-guided exploration. **20/25 games, 160/183 levels, 78.4 AE** | No code released; no cost reported; single run per game, no variance (authors' own limitation) |
| **Tycho** (arXiv 2607.28287) | Free-form executable hypotheses an agent can model, test, plan with, repair or bypass. **100.00 RHAE, all 183 levels** (Opus 5) | ~**$119/game**; inference cost explicitly excluded from the metric (authors' own limitation); public set, warm runs, single pass |
| **Executable World Models for ARC-AGI-3** (arXiv 2605.05138) | Coding agents synthesise executable environment models | Frontier-model dependent; cost per hypothesis is a model call |
| **One Life to Learn** (arXiv 2510.12088) | Symbolic world models for stochastic environments from unguided exploration | Different regime; useful for the stochastic extension |

Two facts follow, and the proposal is built on both.

**First, the LLM in the loop is winning, and we say so.** In OPINE-World's own
baseline table, WorldCoder and neural latent world models -- the families
nearest ours -- clear **zero levels**. Any version of this proposal claiming
that removing the model from the learning loop beats keeping it in would be
contradicted by published evidence on the first page. That claim is retracted.

**Second, the entire field reports capability and not one system reports
cost as a scored axis.** Tycho's ~$119/game is a footnote outside its own
metric. OPINE-World's cost is absent. Yet the difference between $119 a game
and $0 a game is the whole difference between a demonstration and something a
person in Lagos or Ghaziabad can actually run. Nobody has drawn that curve
because nobody has an instrumented cheap end to anchor it.

> **The novelty check this document previously deferred has been done.**
> OPINE-World does perform online programmatic world modelling with replay
> verification -- so it, not us, holds that ground, and with a much stronger
> result. It does so with two frontier LLM agents, no released code and no cost
> accounting. Our contribution is therefore re-scoped, on purpose and in
> public, from *a better learner* to *the measurement of what these learners
> cost and how cheap one can get before it stops working.*

## 2b. The fastest route to peer standing: own the measurement

A solo researcher does not become a peer of five funded labs by
reimplementing five papers. Reimplementation is months of work and any
resulting comparison is dismissible in one sentence -- *you implemented mine
wrong* -- which is usually a fair objection.

The asymmetry worth exploiting is different. **Every system in the table above
is evaluated on its own setup, with its own protocol, against its own
baseline.** There is no shared corpus, no shared causal-replay discipline, and
no common denominator, so the field cannot currently answer a simple question:
for a given interaction budget, which class of world-model learner predicts
best, and where does each one break?

We are unusually placed to answer it, and as of 7 September 2026 **the
substrate is built and published**, not proposed:

```bash
git clone https://github.com/let-the-dreamers-rise/nyaya && cd nyaya
python -m bench.run --corpus bench/corpus-heldout
```

Two corpora of 25 episodes each (development and held-out, 24,499+ recorded
transitions in total, labelled with actions, click coordinates and level
events), delta-encoded 331x so they ship losslessly inside the repository; a
replay harness that predicts before it learns; changed-cell F1 as the headline
so the copy-forward null scores 0.000 by construction; and **tokens and
ms/step reported next to every score.** A method joins in ten lines. See
[`bench/README.md`](../bench/README.md).

That this exists before the funding, rather than after it, is the point: the
proposal's first deliverable is already contestable by a stranger.

Two rules keep this honest and cheap:

1. **Only run code the authors released.** Where a method has public code, run
   it under our protocol and report it. Where it does not, report the authors'
   own published numbers as *their setup, not ours*, clearly separated. Never
   reimplement a method and then claim a comparison against it.
2. **Invite correction before publishing.** Send each author their result and
   the exact command that produced it. A correction received is a
   collaboration started; a correction received after publication is a fight.

This inverts the standing problem. Rather than a low leaderboard score asking
for attention, it is a resource the field has to cite -- and every method added
makes the substrate more valuable while costing us nothing but a run.

## 3. The contribution, in four claims

**C1 -- The cost-capability frontier is measurable, and is currently blank.**
For a fixed interaction budget, prediction quality is a function of inference
spend. Today the field has exactly two points: roughly $119 per game with a
frontier model in the loop (Tycho, solved), and $0 per game with a fixed
hypothesis class (this runtime, F1 0.253 held out, 19 of 25 episodes never
reaching threshold). Everything between is unmeasured. We measure it: the same
corpus, the same causal-replay protocol, cost as a scored column rather than a
footnote. *This is the claim that cannot fail wastefully -- the curve is useful
to the field whichever shape it has.*

**C2 -- The curve can be bent, by moving work out of the model and into
programs.** The prediction is not that programs beat frontier synthesis. It is
that most of what a frontier call currently does on this benchmark is *routine*
-- re-deriving the same physics, re-searching the same paths -- and routine work
is compressible into programs that then cost nothing to re-run. Programs that
survive replay become primitives, so the hypothesis class grows from the
agent's own failures: mispredicted transitions are exactly the specification
for the next synthesis round. This is DreamCoder's wake-sleep loop moved into
online interaction, and it is **EvoSkill's stated thesis** (agents learning
from their own attempts, including failed ones, producing reusable artefacts
without retraining) instantiated where that programme has not yet gone.
Measured as: cost per level cleared, not levels cleared.

**C3 -- The delegation architecture that makes the cheap end possible.** Once
physics and search live in programs, actions stop costing tokens. Measured on
ARC-AGI-3 through the real sandbox: a stock 27B agent spent ~441 tokens of
reasoning per environment action and exhausted its ~70k-token budget in all 25
games; with the runtime carrying physics and search, actions cost ~0 tokens at
1.4 ms each. This is the systems result that anchors the cheap end of the
curve, and the reason a point at $0 exists to measure at all.

**The composite claim:** *the cost-capability frontier for programmatic world
models, measured on a shared open corpus with cost as a scored axis -- and the
cheapest architecture that still clears levels.*

**What we are explicitly not claiming:** that this beats Tycho or OPINE-World
on capability. It does not, they are far ahead, and the proposal that pretended
otherwise has been retracted.

Order of operations matters and is deliberate: **C0 ships first.** The
substrate is useful to others even if C1-C3 turn out to be wrong, which makes
it the only part of this proposal that cannot fail wastefully. It is also the
artefact that earns the standing to be read on C1-C3 at all.

## 4. Why this is Sentient's thesis, mechanically

OML made **weights** loyal: fingerprinting lets a model be released openly and
still owned by its community. What an agent learns *after* deployment has no
such mechanism -- it lives in opaque context windows and closed fine-tunes,
ownable by no one and auditable by no one.

A learned skill that is **a readable program** is loyal by construction:

- **Inspectable** -- the belief is a line of code with the evidence that earned it.
- **Editable** -- deleting a rule deletes the belief, and the agent's verdict
  actually changes. Demonstrated, not asserted (`demo_scam.py`).
- **Portable** -- it carries between models, so no vendor owns the behaviour.
- **Irrevocable** -- a file on the user's device cannot be switched off remotely.
- **A natural OML object** -- a program can carry provenance and community
  ownership the way a fingerprinted model does. Stated as roadmap, not as done.

And "runs on the cheapest phone" is not a marketing line here; it is a
*consequence* of C1. Removing the model from the learning loop is what makes
CPU-only, offline, sub-second learning possible at all.

## 5. Experiments

All five run against an existing corpus: 24,499+ recorded transitions across
25 public ARC-AGI-3 games, with a causal-replay harness already written
(predict before learning, learn after, no peeking).

**E0 -- The frontier (ships first; the substrate already exists and is
published).** Run every method with released code under one protocol on the
shared corpus: the copy-forward null, our template learner, enumerative DSL
synthesis at several search budgets, a small local model in the loop, and
**Tycho**, whose code is public under Apache-2.0. Report per-game changed-cell
F1, exact-frame rate, interactions-to-threshold, and **cost in tokens, dollars
and wall-clock** -- as a scored column, not a footnote. Plot quality against
spend. Methods without public code (OPINE-World) appear as their own published
numbers in their own setup, visually separated, never reimplemented.

*The deliverable is the curve, and the curve is publishable whatever it shows.*
If it is a cliff -- capability collapsing the moment the frontier model leaves
-- that is the most important negative result in on-device agent research and
nobody has published it. If it is a slope, the interesting engineering is
finding where on that slope a phone can sit.

**E1 -- Hypothesis-class coverage (baseline; already run).** Replay every
game; score exact-frame and changed-cell F1 of the current template learner.
Result to date, with the interval that the first version of this document
omitted: aggregate F1 **0.253 (95% CI 0.039-0.490)** on 3,318 held-out
transitions the learner was never developed against, and **0.185 (CI
0.043-0.355)** on development logs.

**And the finding that matters more.** Two diagnostic baselines were added to
the registry in September: `memorise`, an exact lookup table, and
`last-effect`, a one-line heuristic that replays whatever an action did last
time. `memorise` scores 0.024-0.048, so the corpus is genuinely novel rather
than repetitive -- the benchmark measures what it claims to. But `last-effect`
scores **0.228 on development, beating the template learner's 0.185** and
reaching threshold on 11 of 25 episodes against 6, at a fortieth of the cost
per step. On held-out data the learner leads, inside heavily overlapping
intervals.

So the control says something sharper than "the learner is weak": **a fixed
hypothesis class barely separates from *do what you did last time*.** That is
direct evidence that the bottleneck is the class rather than the search inside
it, which is exactly the premise of C2 -- and it is stronger motivation for
this proposal than the flattering number it replaces.

**E2 -- Does synthesis beat templates where templates fail?** Run enumerative
DSL synthesis on the wall-level games specifically. Metric: changed-cell F1
on held-out transitions of games where the template learner sits at baseline.
*Falsifiable prediction: synthesis lifts at least three wall-level games
above 0.4 F1 where templates achieve ~0.* Note the standing counter-evidence:
WorldCoder, a program synthesiser, clears zero levels in OPINE-World's table.
If E2 fails, that counter-evidence is confirmed and we report it as such.

**E3 -- Does library learning transfer?** Train on games 1..k, measure
sample-efficiency on unseen games k+1..25 with and without the accumulated
library. Metric: interactions required to reach a fixed prediction quality.
*Falsifiable prediction: transitions-to-threshold falls monotonically as the
library grows -- and if it does not, library learning is not helping here and
we report that.*

**E4 -- Active experiment design.** Choose the action maximising expected
disambiguation between surviving programs, versus frontier exploration.
Metric: actions spent to pin the theory. *Prediction: fewer than the ~40-70
actions the LLM-driven agent spent wandering.*

**E5 -- Cost per level cleared.** Tokens, dollars and wall-clock per
environment action and per level cleared, for every method in E0. Already
instrumented at the cheap end; Tycho's public code supplies the expensive end
measured by us rather than quoted. *Falsifiable prediction: at least one
architecture clears levels at under $1 per game -- two orders of magnitude below
the published frontier result. If nothing does, the honest headline is that
capability on this benchmark currently costs $100+ a game and open on-device
agents are further away than the field's framing suggests.*

Every experiment reports denominators, held-out splits, and negative results.
The evaluation harness is part of the deliverable precisely so the numbers can
be contested.

## 6. What could make this fail, said plainly

1. **The curve may be a cliff.** It is entirely possible that capability on
   this benchmark collapses to zero the moment a frontier model leaves the
   loop -- WorldCoder's 0 levels in OPINE-World's table is evidence for exactly
   that. This would falsify C2. It would *not* falsify C1: the cliff is itself
   the measurement, it is currently unpublished, and it is the single most
   decision-relevant fact for anyone funding on-device agents. This is why C1
   ships first and why it is the claim we are willing to be judged on.
2. **Enumerative synthesis may not scale.** PoE-World reports difficulty
   beyond simple gridworlds; a naive DSL search explodes combinatorially. The
   mitigation is a small typed DSL plus library growth pruning the space, and
   E2 is the honest test of whether that is enough.
3. **An LLM synthesiser is, on current evidence, simply better.** Not a risk --
   a published fact (Tycho, 100.00 RHAE). The proposal is built on top of it
   rather than against it: we measure what it costs and how far down the cost
   axis the capability survives.
4. **Tycho's code may not run under our protocol.** It is an agent that acts in
   a live environment; our corpus is logged transitions. Adapting it is real
   work and may require a live-environment mode in the harness. Budgeted in
   M2; if it proves impossible, Tycho joins OPINE-World as a quoted result and
   the curve loses its measured expensive anchor, which we would state.
5. **ARC-AGI-3 is one benchmark, and it moved.** Results here are evidence
   about grid-structured interactive environments, not about intelligence. The
   14 April 2026 scoring change also means pre- and post-change numbers are not
   comparable -- which is an argument for the versioned corpus, and a caveat on
   every historical number we quote.
6. **Our own capability is low and stays low.** The runtime clears early levels
   on 2-4 of 25 games. The contribution is the measurement and the cheap end of
   the curve, not a competitive score, and this proposal says so in its title
   rather than its appendix.

## 7. Deliverables

- **The cost-capability curve** for programmatic world models on ARC-AGI-3:
  quality against inference spend, every point measured under one protocol, the
  first such measurement in this literature. This is the headline deliverable.
- **The evaluation substrate** -- corpus, protocol, harness, cost column --
  already shipped under MIT at [`bench/`](../bench/README.md), so every number
  is contestable by a third party today rather than on completion.
- **The runtime**, MIT, dependency-free Python, CPU-only: world-model
  induction, DSL synthesis, library learning, planner, delegation layer.
- **A paper**, submitted to the ARC Prize 2026 Paper Track and arXiv. Note the
  eligibility rule that matters here: *the linked code submission need not
  achieve a high score for the paper to be eligible* -- the track scores the
  research, and requires open-sourcing everything, which this proposal does
  anyway.
- **A skills library format**: learned programs with provenance, portable
  across models -- the artefact that makes behaviour ownable.

## 8. Why open source is load-bearing, not a concession

The product claim *is* readability. A behaviour you cannot read is a behaviour
you cannot audit, edit, or own; a closed implementation of this idea would
defeat its own thesis. Beyond ideology there is a research reason: claims
about sample-efficiency are only worth as much as their reproducibility, and
the corpus plus harness are what let anyone check them. At least one essential
component open and load-bearing is Sentient's stated bar; here every component
is, because the alternative is incoherent.

## 9. What this is not

Not AGI in general, and the proposal should never use the word as a claim. Not
a state-of-the-art bid: Tycho and OPINE-World are ahead and this document says
so on its first page. Not a solved benchmark, ours or anyone's -- the
semi-private set sits at 62.7% for the best model in the world.

What it is: **one measurement the field is missing and one engineering
question that follows from it.** What does a world model cost, and how cheap
can one get before it stops working? The measurement is useful whatever the
answer; the engineering is where an open, on-device, unrevocable agent either
becomes possible or is shown not to be yet. Falsifiable predictions, a
published corpus, a working baseline at the cheap end, a public competitor's
code at the expensive end, and negative results reported in the same voice as
positive ones.
