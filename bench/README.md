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
