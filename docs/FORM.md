# Subspace grant form — final answers, v3 (the cumulative-learning version)

Upgraded after the idea tournament: verification is the floor, inheritance
is the product. Everything between `>>>` markers pastes straight into the
form. Research: [AUTONOMYS.md](AUTONOMYS.md).

---

## Contact fields

| Field | Value |
|---|---|
| Full Name | Ashwin Goyal |
| Email | the address you want grant mail on (form bound to kodezephyr@gmail.com) |
| Discord handle | join their Discord first — the grants team lives there |
| Telegram handle | optional |
| AI3 Wallet Address | Subwallet/Talisman address; needed before Milestone 0 pays |
| Project website | the GitHub repo URL is fine |
| X / LinkedIn | only if active |
| Github link | the public repo — **must be live before submitting** |

**Category:** `AI-Powered dApp`

---

## Field: "Please describe your project and the problem that you are solving"

>>>
Every AI agent today is born with amnesia and dies without heirs. Whatever
it learns lives in a context window or a private fine-tune, cannot be
inspected or trusted by anyone else, and evaporates when the session ends.
Each new agent starts from zero. Machine learning, as deployed, does not
accumulate.

Human intelligence solved this problem once already — not with bigger
brains, but with culture: knowledge that is written down, verified,
inherited, and improved generation after generation. Nothing like that
exists for machines, because it requires four properties no single stack
has offered together: knowledge as portable objects anyone can read,
tamper-proof permanent memory, provenance and identity, and a settlement
layer for claims. Autonomys ships the last three as Auto Drive, Auto ID,
and Auto EVM. We bring the first.

Auto Evolve makes agent learning cumulative and verifiable on Autonomys.
An agent's experience archives to Auto Drive; our engine compiles it into
small, human-readable skill programs; each skill is scored by replaying it
against the archived evidence — not by trusting a claim — and anchored on
Auto EVM with its score, its evidence, and its lineage, attested by Auto
ID. New agents then inherit: they query the commons for proven skills
before learning from scratch, and improved variants are anchored as
descendants of what they improve. The result is a permanent, public,
self-correcting body of machine knowledge — skills that compete on
evidence, survive on merit, and compound across agents — growing on a
network no one can switch off.

The learning engine already exists, is open source (MIT), and is measured:
a dependency-free Python runtime that induces an environment's rules from
a handful of interactions on CPU, a replay verifier, and an evolutionary
search that improves theories against archived evidence. Built and
evaluated on ARC-AGI-3, a benchmark designed to resist memorisation, where
it learns games it has never seen and clears levels with no language model
in the loop — and it is under active development there, so Auto Evolve
inherits every improvement to the engine for free.
>>>

---

## Field: "Project Proposal" (required)

>>>
**Auto Evolve — cumulative, verifiable machine learning on Autonomys**

**1. The gap**

Autonomys has already argued that unverifiable agent memory is a
first-class vulnerability, and answered it with permanent, immutable
context on Auto Drive. But trustworthy inputs do not make trustworthy
conclusions. What an agent learns from its experience remains a black box
— unverifiable, untransferable, and mortal. The network that made agent
memory permanent is the natural home of the next primitive: making agent
LEARNING permanent, provable, and inheritable.

**2. The system (three layers, all MIT, one public repo)**

*Layer 1 — Skill objects.* `auto-evolve-py`, the first Python SDK for Auto
Drive, writes agent experience logs to permanent storage over the
S3-compatible and REST interfaces. The skill compiler turns archived
experience into readable skill programs — plain files a human can audit,
not weight deltas. The replay verifier scores every skill against held-out
archived transitions; the score is reproducible by anyone holding the
evidence CID.

*Layer 2 — Anchored lineage.* A provenance contract on Auto EVM records
skill hash, evidence CID, replay score, and parent-skill hashes, attested
by the agent's Auto ID. Lineage makes the knowledge base self-correcting:
improved variants are anchored as children, compete on the same archived
evidence as their parents, and displace them on merit — a verifiable
evolutionary record of machine knowledge, with a `verify` command anyone
can run to re-derive any score from public data.

*Layer 3 — Inheritance.* The piece that changes what agents are: a query
interface (`inherit(environment_signature)`) that lets any new agent fetch
the best verified skills for its situation before spending a single action
learning what the network already knows. Agent B starts where agent A
left off; the species remembers.

**3. The public demonstration — the Commons**

The final milestone opens the system to everyone: a small public arena of
replayable environments where anyone's agent — any language, any framework
— can play, with experience auto-archived, skills auto-compiled and
anchored, and a live leaderboard showing the lineage tree growing as
submitted agents improve on each other's verified skills. Cumulative
machine learning, visible in public, running on Autonomys rails. It doubles
as hackathon infrastructure for the Foundation's community programs.

**4. Why this must be Autonomys**

Cumulative learning requires permanence (evidence that cannot be edited
after the fact — DSN), cheap content-addressed retrieval (routine
re-verification — Auto Drive), an execution layer for anchored claims
(Auto EVM), and identity for attribution across generations of skills
(Auto ID). No other network ships all four. Anywhere else, this is three
vendors and a trust assumption — which defeats the point.

**5. How it serves the program's objectives**

*Innovation in deAI:* a primitive that exists nowhere — proof of learning
with verifiable lineage. *Scalable AI infrastructure:* every skill puts
real evidence sets onto the DSN; the commons generates continuous storage
workloads by design. *Accessibility:* Python developers get their first
supported path onto Autonomys, and skills are readable files — a builder
can see what an agent knows without specialist tooling. *Interoperability:*
the SDK bridges the Python AI world (LangChain, Hugging Face) to the
network, and inherited skills are portable across agents and frameworks.
*Privacy and security:* evidence can stay encrypted on Auto Drive with
only hashes and scores public — skill quality is provable without
disclosing the data it was learned from.

**6. Risks and how they are managed**

We depend only on stable pieces: Auto Drive and Auto EVM. The Autonomys
Agents Framework is explicitly experimental, so integration with it ships
as an example, never a dependency. If Auto ID public tooling is not ready
in the window, attestation degrades to a plain EVM signature and upgrades
later without redesign. Scope risk is handled by milestone ordering: each
milestone is independently useful — the Python SDK alone (M1) fills a gap
the ecosystem has today, verification (M2) stands without inheritance,
and inheritance (M3) stands without the public arena (M4). As a solo
builder the honest risk is bandwidth, which is why the plan is twenty
weeks of narrow, sequenced scope with acceptance tests rather than a
platform promise.

**7. Long-term vision**

Verified lineage is the precondition for two things the AI3.0 thesis
needs. First, an economy of capability: skills with provable quality and
signed ancestry can be licensed, composed, and rewarded — a market where
contribution to the commons pays, in the network's own spirit of
incentivized participation. Second, and larger: a research path where
capability compounds in the network rather than in any one model —
intelligence that belongs to everyone because it accumulates in a commons
no company controls. That is AI3.0 stated as an engineering program, and
this grant builds its first working organ.

**8. Openness**

MIT for all software, public GitHub from the first commit, documentation
under CC BY 4.0 — compliant with the Terms and Conditions' licence
requirements as written.
>>>

---

## Field: "Milestones and Deliverables"

>>>
**Milestone 0 — on signing.** KYC/KYB and wallet complete; public
repository, project board, and technical specification published.

**Milestone 1 — Archive & Compile (6 weeks).** `auto-evolve-py` on PyPI:
agent experience logs to and from Auto Drive via the S3-compatible and
REST interfaces, integration tests against the live network; the skill
compiler producing readable skill programs from archived experience;
quickstart tutorial and demo recording. *Acceptance: a third-party
developer can archive an agent's experience and compile a skill following
the tutorial alone.*

**Milestone 2 — Anchor & Verify (5 weeks).** Provenance contract on Auto
EVM (testnet then mainnet, verified source) recording skill hash, evidence
CID, replay score, and parent hashes; the `verify` CLI that fetches
evidence, replays it, and compares the re-derived score to the on-chain
claim; Auto ID attestation where tooling permits, EVM-signature fallback
otherwise. *Acceptance: an independent party verifies a published skill
end to end using only the CLI and public data.*

**Milestone 3 — Inherit & Evolve (5 weeks).** The inheritance interface:
query best verified skills by environment signature; import and
hot-start — agent B measurably outperforms from-scratch learning by
starting from agent A's anchored skills; the evolution loop — improved
variants anchored as descendants, competing on shared archived evidence.
*Acceptance: a reproducible benchmark in the repo shows inherited-start
beating cold-start on identical environments, with the full lineage
visible on-chain.*

**Milestone 4 — The Commons (4 weeks).** Public arena: open replayable
environments, open submission for any agent, auto-archival, auto-compile,
auto-anchor, and a live leaderboard rendering the skill lineage tree;
example bridge to the Autonomys Agents Framework; walkthrough article
suitable for the Autonomys blog; complete documentation and final report.
*Acceptance: an external participant completes a submission end to end
without our help, and their skill appears in the public lineage.*

Total duration: 20 weeks from Milestone 0. Monthly written updates within
five days of each month's end, per the Terms and Conditions.
>>>

---

## Field: "Budget Estimation"

>>>
Total requested: USD 55,000, disbursed against milestones.

- Milestone 0 (on signing): USD 5,000 — specification, repository and
  infrastructure setup, Auto Drive and testnet provisioning.
- Milestone 1 (6 weeks): USD 13,000 — Python SDK and skill compiler,
  storage costs, documentation.
- Milestone 2 (5 weeks): USD 14,000 — contract development to audit-ready
  quality, verification tooling, deployment gas, testing.
- Milestone 3 (5 weeks): USD 13,000 — inheritance interface, evolution
  loop, reproducible hot-start benchmark.
- Milestone 4 (4 weeks): USD 10,000 — public arena build and hosting,
  documentation, final reporting.

The budget covers twenty weeks of full-time solo engineering plus storage,
gas, and hosting; no overhead or subcontracting. I am glad to adjust scope
and sizing in the Discovery phase, including the composition of AI3 and
stablecoin components.
>>>

---

## Pitch deck (optional upload — worth doing)

Nine slides: born amnesiac, dies childless (the problem) / how humanity
solved it once (cumulative culture) / the four properties it needs and why
only Autonomys has them / the three layers / the Commons demo / evidence
already measured (ARC-AGI-3, engine live today) / milestones / budget /
founder. Attach a short screen recording of the runtime learning an unseen
game live — it outworks every slide.

## Final checks before submitting

1. **Public repo live** — the form asks for it; the T&Cs require it.
2. **Discord joined**, handle filled in.
3. **AI3 wallet address** ready.
4. **Read the Grant Agreement and T&Cs yourself** — you sign them, and the
   confidentiality clause bars discussing the grant amount publicly.
5. **Raise the liquid/locked split in Discovery** — the T&Cs permit up to
   100% locked AI3 at their discretion; it is the most material term.
6. Expect up to 8 weeks of silence; that is their stated normal.
