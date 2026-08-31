# The ask: what to request, and how to justify every rupee of it

Companion to [RESEARCH.md](RESEARCH.md) (the technical spine) and
[PITCH.md](PITCH.md) (the narrative). This is the part reviewers use to decide
whether you are serious, and the part most solo applicants get wrong in one of
two directions: asking for a number designed to impress, or asking for so
little that the work is obviously unfundable at that price.

**The rule that governs everything below: ask for what the work costs, and
show the arithmetic.** A council of professors reads a budget the way they
read a results table. An unjustified large number reads as naive; a justified
large number reads as planned.

---

## 1. Which track, and therefore which number

Sentient runs one application considered for two tracks. They are different
instruments and the honest mapping is:

| | Grant track | Investment track |
|---|---|---|
| What it funds | research, open-source public goods, individuals | companies scaling open products |
| What they take | nothing -- no equity, no IP claim | equity on founder-friendly terms |
| What you have today | **all of it** -- corpus, harness, runtime, results | a repo and a thesis; no entity, users, or revenue |
| Credible size | $80k-250k for a 12-month research programme | seed round; needs an entity and traction first |

**Recommendation: lead grant, note commercial intent.** Not from modesty --
from fit. On the investment track you are compared against teams with users
and pipelines and you lose on every axis they measure. On the grant track you
are compared on technical merit, mechanism and openness, where the work is
genuinely strong. And the grant deliverables *become* the investment
due-diligence artefacts six months later, so nothing is wasted by that order.

Say it in the form explicitly, because saying it plainly is itself a signal:
*"Applying to the grant track. The research is a public good and should be
funded as one. There is a commercial path -- deployment and support for teams
running agents at scale -- and I would welcome that conversation once the
runtime has users, but I am not going to describe a company that does not yet
exist."*

## 2. The number, built from the work

Twelve-month research programme, one full-time researcher, India-based.

| Line | Amount (USD) | Justification |
|---|---|---|
| Researcher, 12 months full-time | 42,000 | One person at a rate that is real for senior technical work in India and leaves no need for consulting on the side. The programme fails if it is a side project |
| Compute for the head-to-head (E0) | 24,000 | The comparison must run LLM-driven baselines -- WorldCoder, OPINE-World and the executable-world-model line all call frontier models per hypothesis revision. **This is the single largest variable cost and it is spent measuring the competition fairly, not on our own method, which runs on CPU** |
| Corpus expansion and curation | 12,000 | Extending beyond the 25 public games: more environments, more transitions, human-verified labels on a held-out slice so agreement can be checked against ground truth rather than only against a teacher model |
| Hardware: one workstation + phone-class test devices | 6,000 | Local GPU for baseline runs; a sub-Rs.10,000 Android and two mid-tier devices to keep the on-device claim honest and measured rather than asserted |
| Publication, conference travel, one collaboration visit | 8,000 | Paper track submission, arXiv, and being in the room once. Standing in this field is partly social and pretending otherwise is naive |
| Contingency (12%) | 11,000 | Compute overruns on E0 are the likeliest surprise |
| **Total** | **$103,000** | |

**Why this number and not another.** It is large enough to be full-time for a
year, which is what the research honestly requires, and small enough that
every line traces to a deliverable. If they want a smaller programme, the
modular fallback below is already priced.

### The fallback, priced in advance

Offer this unprompted -- it shows the programme is decomposable and that you
have thought about their portfolio, not just your own funding:

- **$35,000 / 4 months -- C0 only.** The shared corpus, the protocol, and the
  head-to-head benchmark published open. Useful to the whole field regardless
  of whether our method wins, and the only component that cannot fail
  wastefully.
- **+$68,000 / 8 months -- C1-C3.** Synthesis, library learning, active
  experiment design, the paper.

## 3. Milestones they can hold you to

Every milestone is a public artefact with a date and a number attached. No
milestone is "make progress on."

| # | Month | Deliverable | The measurable |
|---|---|---|---|
| M0 | 0 | Repo public, corpus released, replay harness documented | 24,499+ transitions, 25 games, one-command reproduction |
| M1 | 3 | **C0 shipped:** head-to-head of every method with released code, one protocol | Per-game F1, interactions-to-threshold, and cost per hypothesis revision in tokens and wall-clock |
| M2 | 5 | E2: DSL synthesis on wall-level games | Prediction on record: at least three wall-level games above 0.4 changed-cell F1 where templates score ~0 |
| M3 | 8 | E3: library learning across games | Prediction on record: interactions-to-threshold on unseen games falls monotonically as the library grows |
| M4 | 10 | E4 + on-device: active experiment design, phone-class measurements | Actions-to-pin-the-theory vs the ~40-70 the LLM agent spent; wall-clock on a sub-Rs.10,000 device |
| M5 | 12 | Paper submitted (ARC Paper Track + arXiv), full release | All artefacts open, every number reproducible by a third party |

**State the negative-result policy in the application itself.** If M2 or M3
fails its prediction, the finding is published as a negative result and the
remaining funds go to C0 -- the substrate the field keeps either way. Funders
almost never hear this offered, and for a council of academics it is the
sentence that marks you as a researcher rather than a pitchman.

## 4. What they get for the money

- A **corpus and protocol** the field currently lacks, open, that makes every
  competing claim contestable.
- The **first honest cost comparison** of programmatic world-model learners --
  including the axis nobody publishes.
- A **runtime** that runs the method on CPU, MIT, dependency-free, on the
  hardware their programme exists to serve.
- A **paper** whose results are reproducible from the released artefacts.
- **EvoSkill extended** into online interactive learning: their own programme,
  taken where it has not gone, with their name on the lineage.

## 5. The three questions to answer before submitting

1. **Has OPINE-World already done C2?** Read it in full. If yes, re-scope to
   C0 plus the cost result and say so in the application. Being the person who
   noticed is better than being the person who did not.
2. **What is the entity answer?** Grant track should not require one. If the
   form insists, say: not incorporated; will incorporate if the funding
   instrument requires it; the research is a public good either way.
3. **What is the honest current status line?** Suggested: *"Repo public,
   95 tests, two one-command demos, a 24,499-transition corpus and a replay
   harness. Pre-users. The ARC-AGI-3 leaderboard score is low and the paper
   track does not require otherwise; the contribution is a mechanism and a
   measurement, not a solved benchmark."*

## 6. One line to keep in view while writing

They funded a programme, not a product line -- and the thing they said they
want is builders who move. The repo is live, the corpus exists, the harness
runs, and the baseline number is already measured. **The application is the
only remaining artefact, and it is the cheapest one to produce.**
