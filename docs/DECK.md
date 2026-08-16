# Auto Evolve pitch deck — complete outline for NotebookLM

Ten slides. Each has: TITLE (on slide), KEY LINE (the one sentence that
must survive), BULLETS (on-slide copy, keep verbatim where quoted),
VISUAL (what to show), and NOTES (talk track / why the slide exists).
Tone: calm, factual, zero hype. Every number here is measured and real.
Audience: Subspace Foundation grant reviewers scoring Relevance,
Feasibility, Impact, Team Expertise.

---

## Slide 1 — Title

TITLE: Auto Evolve
KEY LINE: Cumulative, verifiable machine learning on Autonomys.
BULLETS:
- Skills that outlive the agent that learned them
- Ashwin Goyal — solo technical founder
- github.com/let-the-dreamers-rise/auto-evolve — engine live, 416 tests, MIT
VISUAL: wordmark + a small lineage-tree glyph (nodes connected
parent-to-child, one node highlighted).
NOTES: The repo link on slide one is deliberate — their programme says
real builders with real repos move fast.

## Slide 2 — The problem

TITLE: Born amnesiac, dies childless
KEY LINE: Every AI agent starts from zero and takes everything it
learned to the grave.
BULLETS:
- What an agent learns lives in a context window or a private fine-tune
- It cannot be inspected, trusted, transferred, or inherited
- Machine learning, as deployed, does not accumulate
VISUAL: two identical robots side by side; the first has a thought-bubble
full of rules, the second an empty one; an X on the arrow between them.
NOTES: One idea only. No solution words yet.

## Slide 3 — The precedent

TITLE: Intelligence compounded once before
KEY LINE: Humanity's capability exploded through culture, not bigger
brains — knowledge written down, verified, inherited, improved.
BULLETS:
- Writing made knowledge permanent
- Verification made it trustworthy
- Inheritance made it cumulative
- No equivalent exists for machine learning — yet
VISUAL: a simple timeline: oral → written → printed → (blank slot with a
question mark labelled "agents?").
NOTES: This is the thesis slide; it reframes the grant from tooling to
infrastructure for a missing layer of machine intelligence.

## Slide 4 — The system

TITLE: Archive → Compile → Verify → Inherit
KEY LINE: Auto Evolve makes learning a permanent, provable, inheritable
object.
BULLETS:
- ARCHIVE experience to permanent content-addressed storage
- COMPILE it into small, human-readable skill programs — files, not weights
- VERIFY by replaying archived evidence — the score is re-derivable by anyone
- INHERIT: new agents import proven skills; improvements anchor as descendants
VISUAL: four boxes in a pipeline; under the fourth, a small family tree
of skill nodes with scores on each node.
NOTES: Emphasise readable: a skill can be opened and audited by a human.
That is what makes verification meaningful.

## Slide 5 — Why Autonomys, and only Autonomys

TITLE: Four properties, one network
KEY LINE: Cumulative learning needs permanence, retrieval, anchoring,
and identity — Autonomys is the only stack that ships all four.
BULLETS:
- Auto Drive / DSN — evidence that cannot be quietly edited
- Content-addressed retrieval — re-verification is routine, not forensic
- Auto EVM — claims anchored where anyone can check them
- Auto ID — attribution across generations of skills
- Anywhere else: three vendors and a trust assumption — which defeats the point
VISUAL: the four Auto-suite logos/labels feeding one lineage tree.
NOTES: This is the Relevance criterion, answered structurally. Their own
announcement calls our category "verifiable, on-chain intelligent
behavior" — quote it verbally, not on the slide.

## Slide 6 — The engine already works

TITLE: Measured, not promised
KEY LINE: The learning core exists today, open source, with the numbers
to show.
BULLETS:
- Learns an unseen environment's rules from single-digit interactions, on CPU
- Replay verifier scores every learned model against held-out evidence
- Clears game levels with no language model in the loop
- Cuts an LLM agent's cost from ~441 tokens per action to ~zero
- Evaluated on ARC-AGI-3 — a benchmark built to resist memorisation
- 416 tests; dependency-free Python; MIT
VISUAL: a terminal screenshot or short embedded clip of `python demo.py`
ending in: LEVEL CLEAR in 27 actions — physics learned from 8 probes.
NOTES: This is the Team Expertise criterion carried by evidence instead
of credentials. If the deck tool allows video, the demo recording
replaces the screenshot.

## Slide 7 — What the grant builds

TITLE: Twenty weeks, four milestones, each independently useful
KEY LINE: Every milestone ships something the ecosystem keeps even if
the world stops there.
BULLETS:
- M1 (6w): auto-evolve-py — the first Python SDK for Auto Drive + the skill compiler
- M2 (5w): provenance contract on Auto EVM + the verify CLI
- M3 (5w): inheritance — hot-start benchmark: inherited beats cold-start, lineage on-chain
- M4 (4w): the Commons — public arena, open submission, live lineage leaderboard
- Acceptance test written into every milestone
VISUAL: horizontal timeline with the four milestones and their acceptance
tests as small captions.
NOTES: Feasibility criterion. Mention the risk posture in one breath:
depends only on Auto Drive and Auto EVM; the experimental agents
framework is an example, never a dependency.

## Slide 8 — What Autonomys gains

TITLE: Workloads, developers, and a story only this network can tell
KEY LINE: Every verified skill is real AI data on the DSN — and the
Python door opens the largest AI ecosystem to Autonomys.
BULLETS:
- Recurring storage demand: evidence sets, not hashes of nothing
- First Python SDK — LangChain and Hugging Face worlds reach Auto Drive
- A first-of-its-kind primitive: proof of learning with lineage
- The Commons doubles as hackathon infrastructure for community programmes
VISUAL: three arrows into the Autonomys logo: workloads / developers /
narrative.
NOTES: Impact criterion, counted the way a foundation counts.

## Slide 9 — The horizon

TITLE: From verified skills to an economy of capability
KEY LINE: Once quality is provable and ancestry is signed, skills can be
licensed, composed, and rewarded — and capability compounds in the
commons instead of inside any one model.
BULLETS:
- Skill marketplace: provable quality + signed lineage = tradable capability
- Agent reputation: verified skill history as the trust layer for delegation
- The AI3.0 thesis as an engineering programme
VISUAL: the lineage tree from slide 1, now large, growing off the top of
the slide.
NOTES: Vision, one slide only, zero promises of tokenomics.

## Slide 10 — The ask

TITLE: USD 55,000 · 20 weeks · milestone-based
KEY LINE: One builder, sequenced scope, acceptance tests — ready to start
on signing.
BULLETS:
- M0 5k · M1 13k · M2 14k · M3 13k · M4 10k
- Covers full-time engineering, storage, gas, hosting; no overhead
- Repo live now: github.com/let-the-dreamers-rise/auto-evolve
- Contact: [email] · Discord: [handle]
VISUAL: clean numbers table; the repo QR code if the tool supports it.
NOTES: End on the repo again. Fill contact placeholders before export.

---

## Design directions for the generator

- Dark background, one accent colour, generous whitespace; no stock
  robots, no glowing brains.
- The lineage tree is the deck's single recurring motif (slides 1, 4, 9).
- Every number stays exactly as written — no rounding up, no invented
  stats. If a number is not in this outline, it does not go on a slide.
- Total length: 10 slides, nothing hidden in appendices.
- Export as PDF under 100 MB for the form upload.
