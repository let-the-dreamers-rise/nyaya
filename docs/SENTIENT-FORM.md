# The Sentient form, field by field, paste-ready

The TypeForm at sentient.foundation/grants, fields as they appear on 10
September 2026, in order. Every number regenerates from a command in this
repo; if you change code before submitting, re-run and re-paste.

---

## Section 1

**Who are you?**

> I'm a student in India, and I build. The habit that defines how I work: I
> try to break my own numbers before anyone else gets the chance.
>
> The problem I see is that intelligence is getting rapidly cheaper to
> demonstrate and no cheaper to run. In July a system solved the ARC-AGI-3
> public set outright, all 183 levels. It cost about $119 a game, and the
> paper lists excluding inference cost from its own metric as a limitation.
> That is the field in one sentence: we can prove these systems work, and
> nobody measures what they cost to use. A capability priced like that is
> not a capability for a woman in Ghaziabad being talked out of her savings
> by a voice that sounds like her grandson. It is a service for whoever is
> billed, revocable by whoever bills.
>
> So I built the cheap end of the curve and the instrument to measure the
> rest: a dependency-free runtime that learns an environment's rules on CPU
> for zero tokens and stores them as a page of Python a person can read,
> edit and own; and a public benchmark with cost as a scored column. Then I
> measured how much of an agent that free end can carry today on games it
> has never seen. Two percent. I published that number the day I got it,
> next to the one-line heuristic that beats my own learner and the naive
> Bayes row that beats my readable rules. I care because the people this
> is for cannot open weights, and can open forty-seven sentences, and the
> price of that difference had never been written down.

**Your email address**: ashwingoyal2006@gmail.com

**What best describes your primary role?** E, Student

**Where are you currently based?** India

## Section 2: What are you building?

**What problem are you solving, and why now?**

> Every system that learns an unfamiliar environment well today has a
> frontier model inside its learning loop, so every action it takes is
> metered, networked and revocable. Nobody has measured how much of that
> work could move out of the model into something a person can own, or
> what it costs in capability to do so. That curve decides whether agents
> ever run offline on hardware people already have.
>
> Why now: the expensive end became measurable this summer. Tycho is
> Apache-2.0 and solves the public set at about $119 a game, so the top of
> the curve can be run rather than quoted. The cheap end is in my repo at
> $0. And the first honest points between them exist as of this week. With
> no model in the loop, about two percent of an agent's actions on unseen
> games are delegable without error. Gating on per-rule confidence does
> nothing; gating on whether the theory reproduces the action's recent
> history exactly lifts every learner to 20 to 50% right; the gated
> learners cover different actions, and their union with exact recurrence
> reaches 2.4% delegable at 57% right, above the ungated heuristic with
> seven times its precision. The commit criterion is solved and cheap. What
> limits delegation is the completeness of the theory, and that is the
> research.
>
> And the competitor's row is run, not promised: EvoSkill's loop with an
> open 8B model, on the same games under the same verifier, wrote 107
> programs and none survived, at 156k tokens; with the evaluator's verdict
> fed back, 137 programs and still none. The loop's value is in the model,
> and the model is what costs $119 a game. The curve between those two
> points is what I am asking you to fund.

**Who does this help?**

> First, anyone building agents that must run without an API bill: the
> benchmark gives them one protocol, one corpus, and a cost column nobody
> else publishes, so their method can be placed against Tycho's and mine.
> Adding a method is ten lines. The first users are findable by name: the
> authors of Tycho, OPINE-World and PoE-World, and ARC Prize paper-track
> entrants.
>
> Downstream, the person your six beliefs describe. The same synthesiser
> already reads the bank messages on an Indian phone, on the phone, and
> says "Rs 12,000 went to a first-time recipient nine minutes after a
> message that said KYC and blocked." No server, no model, no network; a
> test asserts the page loads nothing from outside. That is a
> demonstration that the free end of the curve reaches a Rs 8,000 phone,
> not a product I am asking you to fund.

**In one line, what are you building?**

> Skills that outlive the agent that learned them: world models compiled
> into readable programs, verified by replay so anyone holding the evidence
> can rescore them, inherited by the next agent, and a public measurement of
> how much of an agent that lets a person own at $0.

**Who is building this, and why is your team the right one to do it?**

> One person. I built the runtime, the benchmark, the synthesiser and the
> phone demonstration in the open since 31 August 2026; 251 tests, standard
> library only, every number regenerable from a command, and CI regenerates
> the held-out tables on every push. The reason to trust me is the commit
> log: when my benchmark showed a one-line heuristic beating my learner, I
> published it; when a novelty check refuted my headline claim, I retracted
> it in writing; when the delegation number came back at two percent, it
> went in the README that night; when I ran EvoSkill's loop with an open
> model and it produced nothing, that row went in too, with every prompt
> committed. This programme says it wants builders with real repos who tell
> the truth about them. That is the whole team.

**What's open about it, and what would get worse if it closed tomorrow, and for whom?**

> All of it is MIT: the corpus, the causal-replay protocol, the runtime,
> the synthesiser, the phone demo, the results including the losing ones,
> and every prompt the competitor model was sent. The openness is
> load-bearing, not a licence choice: the product claim is readability,
> and a closed implementation of "a behaviour you can read" is incoherent.
>
> If it closed tomorrow: the field loses the only shared scoreboard where
> cost sits next to quality, so every future claim about cheap world models
> goes back to being unfalsifiable; anyone comparing methods loses the
> corpus and the protocol; and the person on the phone loses the one
> version of this where the intelligence is a file nobody can revoke. That
> last one is exactly the loss your "yours to keep" belief exists to
> prevent.

**Please provide demo or trial links** *(one URL field; the site links to everything else)*

> https://let-the-dreamers-rise.github.io/nyaya/

If the field takes text, add:

> Repo: https://github.com/let-the-dreamers-rise/nyaya (`python -m bench.run --corpus bench/corpus-heldout`, `python scripts/delegation.py --corpus bench/corpus-heldout --complete`)
> Belief ledger: https://let-the-dreamers-rise.github.io/nyaya/ledger.html
> CI regenerating the tables on every push: https://github.com/let-the-dreamers-rise/nyaya/actions
> The archive / verify / inherit spec the engine is built toward: https://github.com/let-the-dreamers-rise/auto-evolve

## Section 3: Track and ask

**Grant or investment?** A, Grant

**How much grant funding are you asking for?** B, 25k

**What would the grant unlock?**

> One deliverable in three months that cannot happen without it: the
> cost-capability curve with its expensive end measured rather than
> quoted. Tycho is Apache-2.0 and costs about $119 a game to run; putting
> it under my protocol on 25 held-out games, two configurations, with
> re-runs, is about $10,000 of inference I cannot pay for as a student.
> Every other row on the curve is $0 and already published. Without the
> grant the curve has a measured cheap end and a quoted expensive end, and
> a curve with a quoted end is an opinion.
>
> Concretely, by the end of month three, all MIT: Tycho's row with tokens
> and dollars next to F1 on the same corpus as mine; delegation
> re-measured with completeness-based commitment against a prediction on
> record now (over 20% delegable at under $1 a game with precision above
> 50%, or a published reason why not); the corpus extended past the 25
> public games; and the on-device claim tested on a sub-Rs 10,000 phone
> rather than asserted. Budget: $10,000 compute, $10,500 one researcher
> for three months in India, $2,000 corpus, $1,000 devices, $1,500
> contingency.
>
> What you keep if I stop at any point: everything published to that
> point is already open. There is no version of this where the money buys
> nothing. The remaining programme is $68,000 across three further
> tranches, released on delivery including on a failed prediction, and it
> is an option you hold, not a commitment you make today.

**Supporting documents** *(required, 10 MB limit)*

> Upload `docs/nyaya-sentient.pdf` from the repo: eight pages, the curve,
> the delegation log, both competitor rows, the retractions, the ask.
> Regenerate with `python scripts/make_pdf.py` if numbers change.

## Before you press submit

1. Never the word "AGI" as a claim. Their programme name uses it; the
   answers do not.
2. Every number above regenerates today; if you change code before
   submitting, re-run and re-paste.
3. The Kaggle token pasted in chat earlier this month: rotate it at
   kaggle.com/settings if you have not.
4. Done, 10 Sep: every commit on nyaya and auto-evolve links to
   let-the-dreamers-rise, and the contributors tab lists only you.
