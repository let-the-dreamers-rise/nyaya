# bench -- a shared substrate for programmatic world models

A corpus, a protocol, and a scoreboard, so that claims about world-model
learning on ARC-AGI-3 can be compared instead of asserted.

```bash
python -m bench.run                              # development corpus
python -m bench.run --corpus bench/corpus-heldout # never developed against
```

```text
corpus: 25 episodes, 2907 transitions
protocol: predict before learning; threshold F1 >= 0.5

method                 exact      F1    tokens   ms/step  reached  median
-------------------------------------------------------------------------
copy-forward            10%   0.000         0      0.00     0/25      --
nyaya-templates         10%   0.185         0      3.11     6/25      41
```

---

## Why this exists

As of September 2026 the capability question on ARC-AGI-3 is substantially
answered, and it was answered by putting frontier language models inside the
learning loop. Tycho reaches 100.00 RHAE on the public 25-game set; OPINE-World
solves 20 of 25. Program-synthesis and neural latent world models, run as
baselines in those papers, clear **no levels at all**.

So this repository is not here to claim that symbolic induction beats those
systems. It does not.

The axis those papers leave open is **cost**. Tycho lists the exclusion of
inference cost from the action-efficiency metric as an explicit limitation,
and reports roughly **$119 per game** (Opus 5) / **$179 per game** (GPT-5.6
Sol) in a footnote rather than a scoreboard. OPINE-World reports no cost data
and released no code. There is no shared corpus, no common replay discipline,
and no denominator, so the field cannot answer the question that decides
whether any of this reaches a phone:

> **For a fixed interaction budget, how much prediction quality survives per
> unit of inference cost -- and where exactly does each architecture break?**

That is the question this substrate is built to make answerable, and the
reason every method here reports `tokens` and `ms/step` next to its F1.

## The protocol

**Causal replay.** At transition *i* a method may use only transitions
`0..i-1`. It predicts, it is scored, and only then does it observe. There is
no second pass and no peeking. Concretely, for every transition the harness
calls `predict(board, action)`, scores the result, and *then* calls
`observe(before, action, after)`.

**Changed-cell F1 is the headline.** ARC-AGI-3 frames change very little
between steps, so a method that predicts "nothing happens" scores extremely
well on any whole-frame metric. Scoring only the cells that actually changed
removes that free lunch: the `copy-forward` null scores **0.000** by
construction, which is the point of including it. Exact-frame rate is
reported alongside, never as the headline.

**Cells are pooled, not averaged.** `aggregate` pools true positives, false
positives and false negatives across every episode before computing F1. A
mean of per-episode F1 scores would let a 3-transition episode outweigh a
400-transition one.

**Episodes are cut at resets and level changes.** A reset is not a transition
the environment's physics explains, and charging a learner for failing to
predict one measures the wrong thing.

**Two corpora.** `bench/corpus` is development. `bench/corpus-heldout` was
packed from a separate run against which no learner in this repository was
ever developed. Report both; a method that only works on the first is
reporting its own overfitting.

## The corpora

| | episodes | transitions | packed |
|---|---|---|---|
| `bench/corpus` | 25 | 4,388 (2,907 after cuts) | 0.27 MB |
| `bench/corpus-heldout` | 25 | 4,784 | 0.33 MB |

Both were packed from raw ARC-AGI-3 episode logs by `bench/pack.py`, which
stores each frame as a delta against its predecessor:

```bash
python -m bench.pack path/to/episode/logs -o bench/corpus
# packed 25 episodes, 4388 transitions: 93.8 MB -> 0.28 MB (331x smaller)
```

331x is what makes the corpus distributable in a git repository at all, and
it is lossless: `apply_diff(before, diff) == after` for every transition.

## Adding a method

A method is any object with two methods. Register it and it appears in the
table:

```python
from bench.methods import register

@register("my-method")
class MyMethod:
    def __init__(self):
        self.tokens = 0        # optional; report inference cost honestly

    def predict(self, board, action):
        """Return the predicted next board. Called BEFORE observe."""
        return board

    def observe(self, before, action, after):
        """Learn from a transition. Called AFTER predict was scored."""
```

```bash
python -m bench.run --methods my-method,copy-forward --per-episode
```

If your method calls a language model, set `self.tokens` to the running total.
A method that does not report cost is reported as `0`, which is a claim, and
readers are entitled to check it.

## Two rules that keep the scoreboard honest

1. **Only run code the authors released.** Where a method has public code, it
   is run under this protocol and reported here. Where it does not, the
   authors' own published numbers are quoted as *their setup, not ours*, and
   kept visually separate. A reimplementation is never reported as a
   comparison -- "you implemented mine wrong" is usually a fair objection and
   always an unanswerable one.
2. **Authors see their result before publication.** Each is sent their number
   and the exact command that produced it. A correction received before
   publication is a collaboration; the same correction after is a fight.

On those rules, today: Tycho released code (Apache-2.0) and is a candidate
for a real run under this protocol. OPINE-World released none, so it can only
be quoted. That asymmetry is precisely the gap a shared substrate closes.

## The first thing this substrate did was refute its own author

The registry holds two diagnostics that exist to keep everyone, including us,
honest. Both were added after the headline number was already published, and
both changed what that number means.

**`memorise`** is an exact `(board, action)` lookup table. Whatever it scores
is the share of the corpus that is repetition rather than generalisation. It
scores **0.024 held out, 0.048 on development** -- so this corpus is almost
entirely novel transitions, and the benchmark is measuring what it claims to.
A benchmark without this baseline cannot tell you that about itself.

**`last-effect`** is one line of theory: *replay whatever this action did last
time, in the same cells*. It is not a learner in any interesting sense.

| corpus | last-effect | nyaya-templates |
|---|---|---|
| development | **F1 0.228**, 11/25 reached, 0.07 ms/step | F1 0.185, 6/25 reached, 2.8 ms/step |
| held out | F1 0.151 (CI 0.065-0.289) | F1 0.253 (CI 0.039-0.490) |

**On the development corpus the one-line heuristic beats the world-model
learner outright**, at a fortieth of the cost per step. On the held-out corpus
the learner leads, but the intervals overlap so heavily that the difference has
not been demonstrated.

The honest statement, which now replaces the earlier one everywhere it
appeared: **the factored template learner has not been shown to beat a trivial
baseline on this corpus.**

That is a worse result for us than the one we published a week ago, and it is
the strongest possible argument for the substrate: nobody made us run
`last-effect`. The registry did, the moment it existed. Any method added here
does the same to every method already in it, ours first.

It also sharpens the research question rather than dissolving it. If a fixed
hypothesis class barely separates from *do what you did last time*, then the
problem is the class, not the search inside it -- which is precisely what C2
proposes to attack.

## Stage one: programs, searched for rather than fitted

`dsl-synthesis` is the first method here that does not fit parameters inside a
fixed hypothesis class. It searches for **local update rules** -- conjunctions
of tests over a cell's neighbourhood and the action, implying what that cell
becomes -- using separate-and-conquer with counterexample-guided refinement, on
CPU, with no model called at any point.

    when action is 'RIGHT' and right2 is 'b' and self is 'c', it becomes 'b'

That sentence is a program the search found, at precision 1.00 over 90
examples. Nobody wrote it.

| method | dev F1 | dev reached | held-out F1 | held-out reached | mean |
|---|---|---|---|---|---|
| last-effect | **0.228** (0.136-0.316) | **11/25** | 0.151 (0.065-0.289) | 6/25 | 0.190 |
| nyaya-templates | 0.185 (0.043-0.355) | 6/25 | **0.253** (0.039-0.490) | 5/25 | 0.219 |
| dsl-synthesis | 0.171 (0.113-0.239) | 5/25 | 0.213 (0.127-0.321) | **8/25** | 0.192 |
| **dsl-synthesis-rel** | 0.204 (0.119-0.286) | 6/25 | 0.237 (0.134-0.348) | 7/25 | **0.221** |

**No single method dominates and every interval overlaps**, so nothing here is
settled. But two things are visible and both point the same way.

`dsl-synthesis-rel` is the only method that is **never worst on either corpus**,
it has the highest mean, and its interval is roughly a third the width of the
template learner's. A method whose held-out lower bound is 0.134 is a different
proposition from one whose lower bound is 0.039 and which happens to have the
higher midpoint.

And it got there **by changing the hypothesis class in response to a
diagnosis**, twice, which is the actual thesis being tested.

### The second change, and why it worked

The absolute primitive set describes a cell by its fixed neighbours. Under it,
a body that slides one cell needs **four separate rules** -- one per direction --
each trained on a quarter of the evidence. `grid-relative` describes the same
cell as *ahead*, *behind* and *beside* relative to where the action points, so
the same mechanism is **one rule with all of it**.

That single reframing moved development F1 from 0.171 to 0.204 and held-out
from 0.213 to 0.237, and it runs *faster* (7.9 ms/step against 8.9) because
fewer, more general rules are cheaper to apply than many specific ones.

Neither primitive set was deleted. Both are registered, both are scored, and
the benchmark decides -- which is the point of having built the benchmark
before the method.

### What the failures taught, since they are the point

Three bugs were found by measurement rather than by reading the code, and each
is now a test:

1. **It learned rules that changed nothing.** "When self is 'b', it becomes
   'b'" -- support 4,755, precision 0.93, completely useless, and it won the
   search round on sheer support while starving real mechanisms of budget.
2. **Negatives were sampled only next to changes.** Rules looked precise on
   that neighbourhood and fired in a thousand places nobody had shown the
   searcher. Held-out F1 was 0.058 against a 0.313 baseline -- worse than doing
   nothing. Sampling across the whole board fixed it.
3. **One hard outcome ended the entire search.** Precision stayed at 86% while
   recall collapsed to 8%.

And one change was reverted *on evidence*: adding diagonal primitives and a
fourth condition gave the greedy refiner more ways to over-specialise and
dropped probe F1 from 0.153 to 0.121. The commented-out line is left in
`synthesis.py` with the numbers attached.

### Stage two failed twice, and the failures are the finding

C2 claims that programs which survive replay should become primitives, so the
hypothesis class grows with experience. Two implementations were built and
both were measured and reverted. Neither is in the shipped registry, and the
numbers are here rather than in a drawer.

**Attempt one -- promote surviving programs directly.** A `dsl-library` method
held its library at class level so it outlived the episode: game 26 started
with whatever games 1-25 taught. Result on the development corpus:

| method | F1 | reached |
|---|---|---|
| dsl-synthesis-rel (no library) | **0.204** (0.119-0.286) | **6/25** |
| dsl-library (library carried across games) | 0.105 (0.047-0.183) | 4/25 |

**The library halved performance.** The cause is not a bug, it is the design:
every promoted program was tied to colour literals -- *"when self is 'c' and
ahead2 is 'b'"* -- and a colour means something different in every game. The
library carried 25 games' worth of confident, specific, wrong vocabulary into
each new one.

So: **a library of concrete programs is worse than no library.** That is a real
result about library learning in this setting, and it is not obvious in
advance -- DreamCoder's setting reuses a fixed symbol vocabulary across tasks,
and ARC-AGI-3 does not.

**Attempt two -- make the programs abstract.** If literals do not transfer,
the outcome should be referential: not *"becomes 'b'"* but *"becomes whatever
is behind it"*, which is a statement about movement that survives a change of
palette. Conditions likewise became colour-agnostic tests (`same_as_behind`,
`at_edge`). Result:

| method | F1 | ms/step |
|---|---|---|
| dsl-synthesis-rel (before) | **0.204** | 14 |
| with referential outcomes | 0.087 | 87 |

Worse, and six times slower. Referential rules carry no colour to pin them to,
so they fall out of the prediction index into a scan over every cell, and
without a pinning condition they are general enough to fire almost anywhere
and overwrite what the specific rules got right.

The idea is not refuted -- the implementation is. What the two results together
say is precise: **transferable programs need abstraction, and abstraction
without a constraint that keeps them selective is worse than no abstraction at
all.** That is the problem C2 actually has to solve, stated much more sharply
than it was before either attempt.

The shipped registry is the state that measured best. Nothing that regressed
was kept, and nothing that was tried is unreported.

### Why the engine is domain-agnostic on purpose

The searcher never learns what a primitive means. It takes `(observation,
action, observation')` and a registered primitive set; every fact about grids
lives in `grid_primitives()`. Swapping that set points the same search at UI
traces, tool-use logs, or anything shaped like a transition -- which is the
difference between an ARC-AGI-3 project and a runtime.

## What the current numbers mean

`nyaya-templates` reaches F1 0.185 on 2,907 development transitions and
**0.253** on 3,318 held-out ones -- higher on data it was never developed against, which is
reported as-is rather than smoothed. Nineteen of twenty-five episodes never
cross F1 0.5 at all.

That is not a good score, it is not presented as one, and as the section above
shows it is not even reliably better than a one-line heuristic. It is a floor
with a denominator: the honest measurement of how far a fixed hypothesis class
gets for **zero tokens and 3 milliseconds per step**, against systems that
solve the same games for roughly $119 each. Both ends of that frontier are now
measured, with intervals. The interesting work is everything in between.

Every score here carries a 95% bootstrap interval, resampled over episodes
because transitions inside one episode are not independent. Two methods whose
intervals overlap have not been shown to differ, and this README will say so
rather than reporting the larger number and moving on.

## Licence

MIT, corpus included. The logs were produced with the TAAF/Duck harness
(Apache-2.0, Tufa Labs); no harness code is vendored here.
