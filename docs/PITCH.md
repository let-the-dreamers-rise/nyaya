# The pitch, written the way they would write it

Voice calibrated by [FOUNDERS.md](FOUNDERS.md): person first, mechanism
always, numbers only where instruments exist, India named, no hype words.
The technical spine is [RESEARCH.md](RESEARCH.md) -- read that first if the
reader is on the technical council. Paste into the TypeForm; the submit
button is yours.

> **Who is reading this.** The council includes information theorists who
> wrote the OML papers -- a Princeton professor and an IISc professor. The
> strongest version of this application is therefore a *research proposal
> with falsifiable predictions*, not a product deck. Lead with the mechanism
> and the measurements; the consumer story is the demonstration that the
> mechanism reaches a phone, not the pitch itself.

---

## The claim, in one paragraph

In July 2026 the ARC-AGI-3 benchmark was largely solved -- by putting frontier
language models inside a world model's learning loop. Tycho reaches 100.00
RHAE on the public set; OPINE-World solves 20 of 25 games. In those same
papers, program synthesis without a model in the loop clears **zero levels**.
We are not going to tell you we beat them. **We are going to tell you what it
cost them, because nobody else has.** Tycho's runs are roughly $119 a game and
its authors list the exclusion of inference cost from their own metric as a
limitation; OPINE-World reports no cost and released no code. The curve of
capability against spend has never been drawn, and it is the only curve that
decides whether this kind of intelligence ever reaches a phone in Ghaziabad or
stays a metered service. **We have the cheap end already instrumented at zero
tokens, we have published the corpus and protocol to measure the rest, and we
are asking to draw the whole curve.** Sentient made *weights* loyal with
fingerprinting; affordability is what makes that loyalty reachable, and
readable skills are the same argument one layer up.

## The opening (their person-first pattern)

A woman in Ghaziabad gets a call. The voice is her grandson's, to the
syllable, and he is in trouble and needs money now. Every rupee she loses
will go unreported because shame outlives theft. The intelligence that
could have caught it exists -- but it lives in a datacenter, behind a
meter, reading her most private moment as someone else's training data.
It protects whoever can pay, and it answers to whoever trained it.

The phone in her hand is enough hardware to catch that scam. What is
missing is intelligence that lives there, learns there, and answers to
her. The reason it can live there is the research claim above: take the
model out of the learning loop and learning costs milliseconds of CPU
instead of a frontier call.

## The thesis (their stack, one layer up)

Sentient made **weights** loyal: fingerprinting lets a model be released
openly and still owned. But an agent's behaviour -- what it learns after
deployment -- still lives in opaque context windows and closed fine-tunes
that no user can read and no community can own. The heist has moved up a
layer.

**Nyaya is the loyal behaviour layer.** Our runtime watches an agent act
and compiles what it experiences into small, readable Python programs:
what moves, what blocks, what the goal is, what a scam's shape is. Skills
a person can open, read, edit, carry between models, and truly own --
because a behaviour you cannot read is a behaviour you cannot trust, and
a skill that is a file on your phone is a skill nobody can revoke. This
is EvoSkill's idea -- agents improving from their own attempts and logs
without a new model -- taken where it has not gone: interactive
environments, on-device, with the OML philosophy applied to what the
agent learns.

And it is why small models become enough. The runtime moves the routine
thinking out of tokens into programs, so the model people can actually
run -- on hardware they already own -- does the judging, not the
grinding. Measured, with denominators, because you will check: on
ARC-AGI-3 (a benchmark built to punish memorisation), a stock 27B agent
spent ~441 tokens of reasoning per action and exhausted its ~70k-token
budget in all 25 games; with the runtime carrying physics and search,
actions cost ~zero tokens at 1.4 ms each. The runtime alone -- **no
language model at all** -- clears early levels on 2-4 of the 25 public
games per run, including games the LLM-driven agent never cleared at
all.

And the honest frame around that number, which an earlier draft of this
document got wrong: **this benchmark has been beaten.** Tycho scores 100.00
RHAE on the public set. Our 2-4 games is not competitive and is not offered as
though it were. It is the anchor at the free end of a cost curve whose
expensive end costs $119 a game -- and the distance between those two numbers,
not our position on the leaderboard, is the research. The retraction and what
replaced it are published at [LANDSCAPE.md](LANDSCAPE.md); we would rather you
read our correction than catch it.

## Who pays (the question every investor asks first)

The monetizable claim is the cost collapse, and its buyer exists today:
any team running LLM agents at scale carries an inference bill this
runtime attacks directly. The commercial motion is embarrassingly
conventional -- an open core with paid deployment, integration and
support for agent-running companies (the pattern every funded
open-source infra company uses), priced against the cloud spend it
deletes. The guardian is the mission that motion funds, not the revenue
line: consumer safety in India monetizes through institutions (banks'
fraud programmes, carriers, device makers), never through the
grandmother, and we will not run ads against her fear. Grant capital
bootstraps; deployment revenue sustains; that ordering is stated rather
than hidden.

## Openness as the mechanism (their bar, cleared honestly)

The runtime is MIT, all of it, and the openness is load-bearing: readable
skills ARE the product. Closed weights cannot offer a behaviour you can
audit; we cannot NOT be open. Sustainability the way they demand it: the
company sells deployment and the vertical, never access to the runtime --
and learned skills are a natural OML object (a skill can carry provenance
and be monetizable by its community the way their fingerprinted models
are; that is roadmap, stated as roadmap).

## The wedge (their India, their scam brief)

First vertical: **the Scam Guardian, India-first.** Their RFP frames it
with American numbers; the sharper version of the same wound is Indian --
UPI fraud and digital-arrest scams industrialised against elders in
their own languages. On-device is not a latency preference there; it is
the difference between a guardian and another data harvester.

And this is no longer an analogy -- **the bridge artefact exists and is
measured** (`demo_scam.py`, one command): from 4,459 labelled real SMS
(public UCI corpus) the runtime learns a 46-rule scam-screening skill in
**1.96 seconds on CPU** -- no GPU, no network, no weights. Held out on
1,115 real messages: **precision 100.0%, recall 77.8% (F1 0.875)**.
Applied zero-shot to Indian scam patterns (KYC freeze, digital arrest,
UPI cashback; illustrative seed set, n=64) it degrades honestly to F1
0.81 -- and **32 local examples lift recall from 81% to 94%** (F1 0.88,
n=32). Every rule is a sentence ("asks for a fee to claim a prize", +3);
the skill is one page of Python the user owns; the demo ends with the
user deleting rules from their copy and the verdict actually flipping.

**And we publish the baseline that beats it**, because you would run it in
five minutes: on the identical split, multinomial naive Bayes gets **F1
0.965** to our 0.875, in a thirtieth of the training time
(`python scripts/text_baselines.py`). That is the actual result, and it is a
better sentence than a fake win: *on this dataset, readability costs about
nine points of F1 and sixteen of recall.* Nobody had priced that before. What
7,930 naive-Bayes weights cannot do is be opened, understood, argued with or
edited by the person being protected; forty-six sentences can. Closing that
recall gap while keeping the rules readable is a stated research question, not
a claim already won.

The transparency has a second price and we state that too: a rule-based scorer
can be read around by an adversary who steals the file -- the counterweight is
that adaptation costs 32 examples and two seconds, and the user can see
exactly what their guardian believes, which no black box offers.

**Version 1 scope, stated honestly:** SMS, links, and forwarded
messages/audio -- because Android restricts third-party access to live
call audio, screening live calls is a carrier/OEM/default-dialer
partnership milestone, not an app-store feature, and we name it as such
rather than pitch around it.

**The competition, named:**

| Who | What they have | What they cannot do |
|---|---|---|
| Truecaller | India's default caller-ID; hundreds of millions of users; AI scam hints | Ad-and-data business model -- the guardian IS the harvester; English-first; closed |
| Google (Pixel/Android scam alerts) | On-device Gemini Nano call alerts, shipping | Locked to new Pixels; closed; one company's values baked in; long-tail languages unserved |
| Bank/carrier fraud SMS filters | Network-side blocking at scale | Server-side by definition; no user ownership; opaque appeals |
| EvoSkill ecosystem (Sentient's own) | The skills-from-logs idea, funded | Coding-agent domain; nobody has taken it on-device to interactive/consumer domains |

Our wedge against all four is the same sentence: open, any-phone,
adaptable to any language community from dozens of examples, and the
user owns the beliefs. Distribution hypothesis with a name on it: elder
fraud-awareness programmes run by Indian banks (every major bank runs
one by RBI direction) and state cyber-cell helplines (1930) -- one pilot
letter is the funded quarter-one milestone.

Not education. The tutor RFP is somebody else's to win.

## The research programme (the half a technical council can grade)

Full version in [RESEARCH.md](RESEARCH.md). The short form:

**The open problem.** Every system in this literature reports capability and
none reports cost as a scored axis. Tycho's ~$119 a game sits in a footnote
explicitly outside its own efficiency metric; OPINE-World's cost is absent
entirely. So the field can tell you that programmatic world models work and
cannot tell you what they cost, which is the only fact that determines whether
they are a product for everyone or a service for whoever is billed.

**Three claims, in the order they ship:**

1. **The frontier is measurable and currently blank.** Quality against
   inference spend, every method under one protocol on one corpus, cost as a
   scored column. Two points exist today -- ~$119/game solved, $0/game at F1
   0.253 -- and nothing in between has been measured by anyone. *This is the
   claim that cannot fail wastefully: the curve is useful to the field
   whatever shape it has, including a cliff.*
2. **The curve can be bent, by compiling routine work out of the model.**
   Programs surviving replay become DSL primitives, so the hypothesis class
   grows from the agent's own failures -- EvoSkill's thesis (learn from your
   own attempts, including failures, produce reusable artefacts without
   retraining) taken into online interaction. Measured as cost per level
   cleared, not levels cleared.
3. **The delegation architecture that makes a free end exist at all** --
   measured: ~441 tokens of reasoning per action for the stock 27B agent,
   exhausting its ~70k budget in all 25 games, versus ~0 tokens at 1.4 ms per
   action with physics and search carried by programs.

**The substrate claim 1 needs is already built and public**, before any
funding: `python -m bench.run` runs two 25-episode corpora under a
causal-replay protocol with cost columns, MIT, in the repository today.

**Predictions we will be judged against:** at least one architecture clears
levels at under $1 a game, two orders of magnitude below the published
frontier; synthesis lifts at least three wall-level games above 0.4
changed-cell F1 where templates achieve ~0. Baseline already measured:
aggregate F1 0.253 on 3,318 held-out transitions the learner was never
developed against.

**What would falsify it:** the curve may be a cliff -- WorldCoder clears zero
levels in OPINE-World's own table, which is direct evidence that capability may
not survive the frontier model's departure at all. Enumerative synthesis may
not scale past simple gridworlds (PoE-World's authors report exactly this).
Tycho's code may not adapt to a logged-transition protocol, in which case the
expensive anchor becomes a quoted number rather than a measured one. Each of
these is written down in [RESEARCH.md](RESEARCH.md) with what we would report
if it happened.

**Deliverables:** the runtime and harness under MIT, the transition corpus so
the numbers are contestable, and a paper to the ARC Prize 2026 Paper Track --
whose eligibility rule is worth noting, since the linked code submission need
not achieve a high score for the paper to be considered. The track scores the
research and requires open-sourcing everything, which this proposal does
regardless.

## The founder (merit over pedigree, their pattern)

Solo technical founder, India. No credential theatre: the evidence is the
repo -- the runtime end to end (perception, world-model induction,
planning, sandbox delegation, evaluation harnesses), 87 tests, a
one-command demo where the runtime meets an unseen game, learns its
physics from 8 probes, and clears it with zero LLM calls. Built while
competing on ARC-AGI-3 (Kaggle: letthedreamersrise), instruments first:
every claim above has a harness behind it.

## The honest fields

- **Track:** one application, considered for both. The honest read: the
  *research* is grant-shaped (no equity, open-source, public good, individual
  eligible) and the *runtime plus vertical* is the investment story. Lead with
  the research; note commercial intent rather than manufacturing a company
  that does not exist yet. RFP mapping, reordered to match what the work now
  is: **Part 2 #12 token and economic optimization (primary)** -- the
  cost-capability frontier is literally this brief; Part 3 extension of
  EvoSkill (the library that grows from an agent's own failures); Part 2 #11
  small, fast, cheap models (thesis alignment -- we do not build models, we
  measure how far you get without a big one).
- **Users:** pre-launch; repo public this month; first users from the
  ARC-AGI-3 community where the results were produced.
- **Round:** none committed; bootstrapped; this application anchors it.
  Clean cap table, no obligations.
- **Entity:** incorporating on funding interest; open to grant track as
  interim if an entity is required first.
- **Use of funds:** harden the runtime as an embeddable library for two
  open agent stacks; publish the skills layer with provenance; ship the
  Scam Guardian prototype on a sub-Rs.10,000 Android; publish the
  cost-reduction benchmark others can cite.
- **12 months:** runtime embedded in >=2 frameworks; the benchmark
  public; the guardian screening real calls on a cheap phone in Hindi;
  ARC-AGI-3 results published as the capability demonstration.

## What would make them say no, pre-answered

- "Is the open part load-bearing?" -- it is the product.
- "Phone or vaporware?" -- zero-dependency pure Python, CPU-only; phone
  deployment is a funded milestone, never claimed as current.
- "Why you against labs?" -- labs make models bigger; this makes small
  models sufficient. Different axis, theirs.
- "Why now?" -- open models crossed usefulness this year; the missing
  piece is the layer that makes them affordable agents on real hardware.
  Their own window argument, applied.
