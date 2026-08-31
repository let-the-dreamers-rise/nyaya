# Programs, not weights: growing an agent's hypothesis space from its own failures

A research proposal for the Sentient Foundation Open Source AGI programme.
Written for the technical council rather than for a landing page: the
reviewers include information theorists who wrote the OML papers, and the
right register for them is a precise claim with an experiment attached.

---

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

## 2. Where the field actually is (August 2026)

Programmatic world models are an active line, and the proposal must be
honest that we are not alone:

| Work | What it does | Limitation we build against |
|---|---|---|
| **DreamCoder** (Ellis et al.) | Wake-sleep library learning: solved programs become new primitives, growing the DSL | Offline task batches, not online interaction with an unknown environment |
| **WorldCoder** (NeurIPS 2024) | LLM writes a world model as code; sample-efficient transfer by reusing program fragments; auditable because programs are readable | **LLM in the learning loop** -- every hypothesis revision is a model call |
| **PoE-World** (arXiv 2505.10819) | Products of programmatic experts; data-efficient because synthesis needs less data than gradient training | Authors state it *struggles to scale beyond simple gridworlds* |
| **OPINE-World** (arXiv 2607.01531) | Object-centric programmatic world model learned online; reports strong ARC-AGI-3 results | LLM-driven; the closest prior work and the novelty risk to check first |
| **Executable World Models for ARC-AGI-3** (arXiv 2605.05138) | Coding agents synthesise executable environment models | Frontier-model dependent; cost per hypothesis is a model call |
| **One Life to Learn** (arXiv 2510.12088) | Symbolic world models for stochastic environments from unguided exploration | Different regime; useful for the stochastic extension |

The common structure: **the synthesiser is a large language model.** That is
a reasonable engineering choice and it buys enormous prior knowledge. It also
fixes the cost of every hypothesis revision at one frontier call, which is
precisely why these systems are demonstrated rather than deployed, and why
none of them runs on a phone.

> **Action before writing any code: read OPINE-World in full.** If it already
> demonstrates online library growth without an LLM, the contribution below
> narrows to the systems result and must be re-scoped. Finding that out costs
> an afternoon and is worth more than a month of building.

## 3. The contribution, in three claims

**C1 -- Induction without a model in the loop.** Transition programs are
synthesised by enumerative search over a typed DSL with counterexample-guided
refinement against logged transitions, on CPU, with no language model called
during learning. The LLM, where present at all, proposes *goals* and reads
anomalies; it never writes the physics.

**C2 -- The hypothesis class grows from the agent's own failures.** Programs
that survive replay become primitives in the DSL, so the space of
representable mechanisms expands with experience. Failure logs are the
training signal: the transitions a theory mispredicts are exactly the
specification for the next synthesis round. This is DreamCoder's wake-sleep
loop moved from offline task batches into online interaction -- and it is
**EvoSkill's stated thesis** (agents learning from their own attempts,
including failed ones, producing reusable artefacts without retraining),
instantiated where that programme has not yet gone.

**C3 -- The delegation architecture that makes it affordable.** Once physics
and search live in programs, actions stop costing tokens. Measured on
ARC-AGI-3: a stock 27B agent spent ~441 tokens of reasoning per environment
action and exhausted its ~70k-token budget in all 25 games; with the runtime
carrying physics and search, actions cost ~0 tokens at 1.4 ms each, verified
through the real sandbox. This is a systems result the modelling papers do
not report, and it is the reason the method can run on hardware people own.

**The composite claim:** *sample-efficient programmatic world-model induction
with library growth and no language model in the learning loop.*

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

**E1 -- Hypothesis-class coverage (baseline; already run).** Replay every
game; score exact-frame and changed-cell F1 of the current template learner.
Result to date: aggregate F1 0.25 on 3,318 held-out transitions from a run
the learner was never developed against, up from 0.18 on development logs.
Per-game residuals name the missing mechanism classes. *This is the control
that every later claim is measured against.*

**E2 -- Does synthesis beat templates where templates fail?** Run enumerative
DSL synthesis on the wall-level games specifically. Metric: changed-cell F1
on held-out transitions of games where the template learner sits at baseline.
*Falsifiable prediction: synthesis lifts at least three wall-level games
above 0.4 F1 where templates achieve ~0.*

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

**E5 -- Cost.** Tokens and wall-clock per environment action, and per level
cleared, against the LLM baseline. Already instrumented.

Every experiment reports denominators, held-out splits, and negative results.
The evaluation harness is part of the deliverable precisely so the numbers can
be contested.

## 6. What could make this fail, said plainly

1. **Enumerative synthesis may not scale.** PoE-World reports difficulty
   beyond simple gridworlds; a naive DSL search explodes combinatorially. The
   mitigation is a small typed DSL plus library growth pruning the space, and
   E2 is the honest test of whether that is enough.
2. **OPINE-World may already have done C2.** Novelty check first, before code.
3. **An LLM synthesiser may simply be better.** If frontier synthesis
   dominates on quality, the contribution collapses to the cost result -- still
   real, but smaller. We would report that rather than bury it.
4. **ARC-AGI-3 is one benchmark.** Results there are evidence about
   grid-structured interactive environments, not about intelligence. The claim
   stays scoped to what was measured.
5. **The current leaderboard position is low** (~1.86 on a scale where ~115 is
   the ceiling, and nobody has beaten this benchmark). The contribution is a
   mechanism and a measurement, not a solved benchmark, and the proposal says
   so in its first paragraph rather than its last.

## 7. Deliverables

- **The runtime**, MIT, dependency-free Python, CPU-only: world-model
  induction, DSL synthesis, library learning, planner, delegation layer.
- **The evaluation harness** and the transition corpus, so every number is
  reproducible and falsifiable by a third party.
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

Not AGI in general, and the proposal should never use the word as a claim. It
is one specific mechanism -- hypothesis-space growth from an agent's own
failures, cheaply enough to run on a phone -- that the benchmark was built to
reward and that the EvoSkill programme already argues for. The honest framing
is a research bet with falsifiable predictions, an existing corpus, a working
baseline, and negative results reported as readily as positive ones.
