# The pitch, written the way they would write it

Supersedes the earlier application draft. Voice calibrated by
[FOUNDERS.md](FOUNDERS.md): person first, mechanism always, numbers only
where instruments exist, India named, no hype words. Paste into the
TypeForm; the submit button is yours.

---

## The opening (their person-first pattern)

A woman in Ghaziabad gets a call. The voice is her grandson's, to the
syllable, and he is in trouble and needs money now. Every rupee she loses
will go unreported because shame outlives theft. The intelligence that
could have caught it exists -- but it lives in a datacenter, behind a
meter, reading her most private moment as someone else's training data.
It protects whoever can pay, and it answers to whoever trained it.

The phone in her hand is enough hardware to catch that scam. What is
missing is intelligence that lives there, learns there, and answers to
her. That is what we are building, and the core of it already runs.

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
grinding. Measured, not promised: a stock 27B agent spent ~441 tokens of
reasoning per action and died budget-broke in every game; with the
runtime carrying physics and search, actions cost ~zero tokens at 1.4 ms
each, and the runtime alone -- **no language model at all** -- cleared
levels the LLM-driven agent never reached. Learned from single-digit
interaction counts, offline, CPU-only, on ARC-AGI-3 -- a benchmark built
to punish memorisation and reward exactly the fluid learning this is.

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
the difference between a guardian and another data harvester. The same
sample-efficient modelling that learns a game's physics from ten
interactions learns a scam's shape from few examples, on the phone, in
Hindi first.

Not education. The tutor RFP is somebody else's to win.

## The founder (merit over pedigree, their pattern)

Solo technical founder, India. No credential theatre: the evidence is the
repo -- the runtime end to end (perception, world-model induction,
planning, sandbox delegation, evaluation harnesses), 87 tests, a
one-command demo where the runtime meets an unseen game, learns its
physics from 8 probes, and clears it with zero LLM calls. Built while
competing on ARC-AGI-3 (Kaggle: letthedreamersrise), instruments first:
every claim above has a harness behind it.

## The honest fields

- **Track:** Investment (Part 3 extension: EvoSkill; secondary Part 2:
  token/economic optimization -- their "cheapest path on any agent
  stack" is this mechanism's definition).
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
