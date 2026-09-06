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
| M0 | **done** | **C0 shipped before the ask:** repo public, both corpora released, replay harness documented, cost columns live | 50 episodes / 24,499+ transitions, `python -m bench.run`, MIT, 121 tests |
| M1 | 3 | **The curve:** every method with released code under one protocol -- including **Tycho** (Apache-2.0) at the expensive end | Quality against spend, in tokens, dollars and wall-clock. Prediction on record: at least one architecture clears levels under $1/game against the published ~$119 |
| M2 | 5 | E2: DSL synthesis on wall-level games | Prediction on record: at least three wall-level games above 0.4 changed-cell F1 where templates score ~0. Standing counter-evidence: WorldCoder clears zero levels in OPINE-World's table |
| M3 | 8 | E3: library learning across games | Prediction on record: interactions-to-threshold on unseen games falls monotonically as the library grows |
| M4 | 10 | E4 + on-device: active experiment design, phone-class measurements | Actions-to-pin-the-theory vs the ~40-70 the LLM agent spent; wall-clock on a sub-Rs.10,000 device |
| M5 | 12 | Paper submitted (ARC Paper Track + arXiv), full release | All artefacts open, every number reproducible by a third party |

**State the negative-result policy in the application itself.** If M2 or M3
fails its prediction, the finding is published as a negative result and the
remaining funds go to C0 -- the substrate the field keeps either way. Funders
almost never hear this offered, and for a council of academics it is the
sentence that marks you as a researcher rather than a pitchman.

## 3b. Why this is safe to fund, said from their side of the table

The question a grantmaker actually asks is not "is this exciting" but **"what
is my downside, and what do I keep if this person stops?"** Answer it before
they have to ask, and answer it structurally rather than with promises.

**1. The first milestone was delivered before the ask, unpaid.** C0 -- the
corpus, the protocol, the harness, the cost column -- is public, MIT and
runnable today. The single best predictor of whether someone ships funded work
is whether they shipped unfunded work, and that evidence is a `git clone` away.
The request is not for permission to start. It is to continue something already
moving.

**2. Open licensing makes abandonment survivable for the funder.** This is the
structural argument and it is specific to open work. If a closed project is
abandoned at 40%, the funder loses everything. If this one is, the corpus, the
protocol, the harness and every measurement taken up to that point are already
MIT and already published -- the field keeps them, and so does Sentient. There
is no version of this where the money buys nothing.

**3. Tranche it, and we propose the tranches ourselves.** No sensible funder
hands a solo researcher twelve months of budget on day one, and we are not
asking them to:

| Tranche | Released on | Share |
|---|---|---|
| 1 | Signing. Covers M1: the cost curve, every method with public code under one protocol | 35% |
| 2 | M1 published and reproducible by a third party | 30% |
| 3 | M2/M3 reported -- *including if the prediction failed*, which is a delivery, not a default | 20% |
| 4 | Paper submitted, all artefacts released | 15% |

A failed prediction releases its tranche. That is deliberate: paying only for
positive results is how funders buy quiet negative results, and the whole point
of this proposal is that the negative ones get published.

**4. The work is legible while it happens.** Public repo, public corpus, and
every claim regenerable by one command. A funder does not have to trust a
quarterly update; they can run the number. That is a stronger control than any
reporting requirement, and it exists because the project is open, not because
anyone was asked for it.

**5. The risk that remains, named.** Solo, so there is no one to continue if I
stop. A student, so term time is real and I will state my actual weekly hours
rather than round them up. No completed funded project behind me. Those are
true, they are the reason for a small first tranche rather than a large one,
and pretending otherwise would be the first broken promise.

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

> **M0 was delivered on 7 September 2026, before submitting.** The substrate
> the rest of this programme depends on is public, runnable and contestable
> today. A funder is being asked to pay for the curve, not for the ability to
> start measuring it.

## 5. The three questions to answer before submitting

> **Question 1 is answered.** The novelty check was done on 7 September 2026
> and it went against the original framing: OPINE-World does hold the online
> programmatic-world-modelling ground, with a far stronger result, using two
> frontier LLM agents. Tycho then solved the public set outright. The proposal
> was re-scoped in public to the cost-capability frontier -- the axis both leave
> unmeasured -- and the retraction is published at [LANDSCAPE.md](LANDSCAPE.md).
> Questions 2 and 3 below stand.

1. ~~**Has OPINE-World already done C2?**~~ *Answered; see above.* Read it in full. If yes, re-scope to
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
