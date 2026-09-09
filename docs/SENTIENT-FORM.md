# The Sentient form, field by field, paste-ready

The TypeForm at sentient.foundation/grants. Fields as they appeared on 6
September 2026; later sections are answered under "If it asks". Everything
in [[double brackets]] is yours. Numbers are as of 9 September and
regenerate from commands in this repo.

---

## Section 1

**Your email address**: ashwinthebest8@gmail.com

**What best describes your primary role?** E, Student.

**Where are you currently based?** [[city]], India

**Who are you?** *(the person, the problems you see, why you care)*

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
> is for cannot open weights, and can open forty-six sentences, and the
> price of that difference had never been written down.

## Section 2

**What problem are you solving, and why now?**

> Every system that learns an unfamiliar environment well today has a
> frontier model inside its learning loop, so every action it takes is
> metered, networked and revocable. Nobody has measured how much of that
> work could move out of the model into something a person can own, or
> what it costs in capability to do so. That curve decides whether
> agents ever run offline on hardware people already have.
>
> Why now: the expensive end became measurable this summer. Tycho is
> Apache-2.0 and solves the public set at about $119 a game, so the top of
> the curve can be run rather than quoted. The cheap end is in my repo at
> $0. And the first honest point between them exists as of this week: with
> no model in the loop, about two percent of an agent's actions on unseen
> games are delegable without error. Gating on per-rule confidence does
> nothing; gating on whether the theory reproduces the action's recent
> history exactly lifts every learner to 20 to 50% right at about one
> percent coverage. The commit criterion is solved and cheap. What limits
> delegation is the completeness of the theory, and that is the research.

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
> phone demonstration in the open since 31 August 2026; 238 tests, standard
> library only, every number regenerable from a command. The reason to
> trust me is the commit log: when my benchmark showed a one-line heuristic
> beating my learner, I published it; when a novelty check refuted my
> headline claim, I retracted it in writing; when the delegation number
> came back at two percent, it went in the README that night. This
> programme says it wants builders with real repos who tell the truth about
> them. That is the whole team.

**What's open about it, and what would get worse if it closed tomorrow, and for whom?**

> All of it is MIT: the corpus, the causal-replay protocol, the runtime,
> the synthesiser, the phone demo, the results including the losing ones.
> The openness is load-bearing, not a licence choice: the product claim is
> readability, and a closed implementation of "a behaviour you can read" is
> incoherent.
>
> If it closed tomorrow: the field loses the only shared scoreboard where
> cost sits next to quality, so every future claim about cheap world models
> goes back to being unfalsifiable; anyone comparing methods loses the
> corpus and the protocol; and the person on the phone loses the one
> version of this where the intelligence is a file nobody can revoke. That
> last one is exactly the loss your "yours to keep" belief exists to
> prevent.

**Please provide demo or trial links**

> https://github.com/let-the-dreamers-rise/nyaya
> `python -m bench.run --corpus bench/corpus-heldout` and `python scripts/delegation.py --complete` reproduce every number above.
> Project site: https://claude.ai/code/artifact/aaf9ecdc-f203-487a-b542-ac370294df33
> Belief ledger, 47 rules, switch any off: https://claude.ai/code/artifact/06089609-fcda-45bc-86f6-e3adf3399c40
> Phone: `nyaya-money serve demo`, or the one-line Termux installer in the README.
> The archive / verify / inherit spec the engine is built toward: https://github.com/let-the-dreamers-rise/auto-evolve

## If it asks

**Track**: Grant first. "The research is a public good and should be funded
as one. There is a commercial path once the runtime has users; I am not
going to describe a company that does not exist yet."

**Which RFPs**: Part Two #12, Token and Economic Optimization for Agents
(primary: delegation is cost routing, with the routing decision measured);
Part Two #11, Make Open Models Small, Fast, and Cheap; Part Two #8, Your AI,
Your Values. Part Three #1 (EvoSkill) is the comparison point, not the
base: their loop and mine on the same unseen games.

**How much, for what, by when**: $30,000, three months, one deliverable:
the cost-capability curve with Tycho at the expensive end measured rather
than quoted, and delegation re-measured with completeness-based commitment.
Prediction on record: over 20% delegable at under $1 a game with precision
above 50%, or a published reason why not. Budget in docs/ASK.md; the
largest line is compute spent running the competitor's method, not mine.

**Team size**: 1. **Entity**: none; open to incorporating if required.
**Raised**: $0.

**What would make you stop**: if no completeness criterion beats the
two-repeat heuristic's 51% at more than its 1% coverage after tranche one,
delegation does not work on this benchmark, and the report says so.

## Before you press submit

1. Never the word "AGI" as a claim. Their programme name uses it; the
   answers do not.
2. Every number above regenerates today; if you change code before
   submitting, re-run and re-paste.
3. The Kaggle token pasted in chat earlier this month: rotate it at
   kaggle.com/settings if you have not.
4. GitHub does not credit you for a single commit on nyaya or auto-evolve:
   ashwinthebest8@gmail.com is not a verified email on the
   let-the-dreamers-rise account, so the author shows unlinked and the
   co-author trailer makes wozcode the only listed contributor. Add and
   verify the email at github.com/settings/emails before anyone on the panel
   opens the repo.
