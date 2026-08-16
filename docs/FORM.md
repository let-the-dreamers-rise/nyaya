# Subspace grant form — final answers, ready to paste

Scored against their four published criteria (Relevance, Feasibility,
Impact, Team Expertise) and written to hit all five program objectives
explicitly. Research: [AUTONOMYS.md](AUTONOMYS.md). Everything between the
`>>>` markers is what you paste.

---

## Contact fields

| Field | Value |
|---|---|
| Full Name | Ashwin Goyal |
| Email | the address you want grant mail on (form is bound to kodezephyr@gmail.com) |
| Discord handle | join their Discord first — the grants team lives there |
| Telegram handle | optional |
| AI3 Wallet Address | Subwallet/Talisman address; needed before Milestone 0 pays |
| Project website | the GitHub repo URL is fine |
| X / LinkedIn | only if active; a dormant link is worse than blank |
| Github link | the public repo — **must be live before you submit** |

**Category:** `AI-Powered dApp`

---

## Field: "Please describe your project and the problem that you are solving"

>>>
Agents on Autonomys can already remember permanently. They cannot prove
what they learned.

Auto Drive solved the first half of agent trust: memory that cannot drift,
be poisoned, or vanish between calls. The second half is still missing.
The rules an agent derives from its experience — the part that actually
determines what it does next — live in opaque context windows or closed
fine-tunes. So when an agent delegates to another agent, or a person
delegates money and identity to one, the question that matters most has no
answer: what has this agent actually learned, and is it any good?

Auto Skills makes learning verifiable. It compiles an agent's archived
experience into small, human-readable skill programs; scores each one by
replaying it against the recorded evidence rather than trusting a claim;
and anchors the result on Auto EVM as skill hash + evidence CID + replay
score, attested by Auto ID. Anyone can fetch the evidence from Auto Drive,
re-run the replay, and independently confirm the score. Learning becomes a
portable, provable object — so a skill proven once can be imported by
another agent instead of relearned from scratch.

The learning engine already exists, is open source (MIT), and is measured.
It is a dependency-free Python runtime that learns an environment's rules
from a handful of interactions on CPU, plus a replay verifier that scores
a learned model against held-out recorded transitions. It was built and
evaluated on ARC-AGI-3, a benchmark designed to resist memorisation: the
runtime learns games it has never seen and clears levels with no language
model in the loop. This grant puts that engine on Autonomys rails.
>>>

---

## Field: "Project Proposal" (required)

>>>
**Auto Skills — verifiable agent learning on Autonomys**

**1. The gap**

Autonomys already argues that unverifiable agent memory is a first-class
vulnerability, and Auto Drive answers it with permanent, immutable
context. But an agent's inputs being trustworthy does not make its
conclusions trustworthy. Nothing in the stack — or in any other agent
stack — can attest to what an agent learned from those inputs, or how well
it learned it. Auto Skills supplies that missing layer, and it is the
natural next primitive beside Auto Drive, Auto EVM and Auto ID.

**2. What we build (three artefacts, all MIT, one public repo)**

*auto-skills-py — the first Python SDK for Auto Drive.* The Auto SDK today
is TypeScript/JavaScript, while the AI ecosystem the Foundation's own
example-projects page targets (LangChain, Hugging Face) is Python-native.
This package writes agent transition logs to Auto Drive over the
S3-compatible and REST interfaces and reads them back for verification,
giving Python AI developers a front door to the network for the first
time.

*The skill compiler and replay verifier.* Archived experience goes in; a
small, readable skill program comes out — a plain file a human can open
and audit, not a weight update. The verifier then replays held-out
recorded transitions through that skill and scores its predictions. The
score is evidence-backed and reproducible by anyone holding the evidence,
which is precisely what makes it worth anchoring.

*The provenance contract on Auto EVM.* Publishes skill hash, evidence CID,
and replay score, attested by the agent's Auto ID, with a `verify` command
that re-derives the score from the archived evidence and compares. A claim
anyone can check is a claim that does not need to be trusted.

**3. Why this must be Autonomys**

The primitive needs four properties simultaneously: permanence, so
evidence cannot be quietly edited after a claim is made (DSN);
content-addressed retrieval cheap enough that re-verification is routine
(Auto Drive); an execution layer to anchor claims (Auto EVM); and agent
identity to sign them (Auto ID). No other stack ships all four. Built
anywhere else, this project would need three vendors and a trust
assumption at the centre — which would defeat its purpose.

**4. How it serves the program's objectives**

*Innovation in deAI:* a new primitive — proof of learning — that does not
exist on any network today. *Scalable AI infrastructure:* every verified
skill puts real AI workloads and evidence sets onto the DSN, exercising
high-throughput storage as intended rather than storing hashes of nothing.
*Accessibility:* Python developers get a supported path onto Autonomys,
and skills are readable files rather than opaque models, so a builder can
understand what an agent knows without specialist tooling. *Interoperability:*
the SDK bridges the Python AI world (LangChain, Hugging Face) to the
network, and verified skills are portable between agents and frameworks.
*Privacy and security:* evidence can remain encrypted on Auto Drive with
only hashes and scores public, so a skill's quality is provable without
exposing the data it was learned from — verifiability without disclosure.

**5. Risks and how they are managed**

The Autonomys Agents Framework is explicitly experimental, so we depend on
it for nothing: integration ships as an example, while the project depends
only on Auto Drive and Auto EVM, both stable. If Auto ID's public tooling
is not ready within the grant window, attestation degrades gracefully to a
plain EVM signature and upgrades later without redesign. Scope risk is
handled by milestone ordering: Milestone 1 is independently useful (a
Python SDK the ecosystem lacks) even if later work were to stall. As a
solo builder the honest risk is bandwidth, which is why the plan is four
months of narrow, sequenced scope rather than a platform.

**6. Long-term vision**

Proof of learning is the precondition for a market in capability. Once a
skill's quality is provable and its provenance is signed, agents can buy,
sell, and compose skills instead of every agent relearning the same lesson
privately — an economy of verified capability running on permanent
storage. Autonomys is the only network positioned to host it, and this
grant builds the first working piece.

**7. Openness**

MIT, public GitHub from the first commit, documentation under CC BY 4.0 —
already aligned with the Terms and Conditions' licence requirements with
no change needed.
>>>

---

## Field: "Milestones and Deliverables"

>>>
**Milestone 0 — on signing.** KYC/KYB and wallet complete. Public
repository, project board, and technical specification published.

**Milestone 1 — Archive & Compile (6 weeks).**
Deliverables: `auto-skills-py` published to PyPI — upload and retrieval of
agent experience logs to Auto Drive via the S3-compatible and REST
interfaces, with an integration test suite running against the live
network; the skill compiler turning archived experience into readable
skill programs; developer documentation and a quickstart tutorial; a short
demo recording. Acceptance: a third-party developer can install the
package, archive an agent's experience to Auto Drive, and compile a skill
by following the tutorial alone.

**Milestone 2 — Anchor & Verify (6 weeks).**
Deliverables: the provenance contract deployed to Auto EVM (testnet, then
mainnet) with verified source; the `verify` CLI that fetches evidence by
CID from Auto Drive, replays it, re-derives the score, and compares it to
the on-chain claim; Auto ID attestation where public tooling permits, with
EVM-signature fallback; contract tests and documentation. Acceptance: an
independent party can verify a published skill end to end using only the
CLI and public data.

**Milestone 3 — Demonstrate & Document (4 weeks).**
Deliverables: a public demo in which Agent A learns a task live, publishes
a proven skill, and Agent B imports the verified skill and performs
immediately — portable, provable capability on Autonomys rails; an example
bridge to the Autonomys Agents Framework; a walkthrough article suitable
for the Autonomys blog; complete documentation; final project report.
Acceptance: the demo is publicly reachable and reproducible from the repo.

Total duration: 16 weeks from Milestone 0. Monthly written updates within
five days of each month's end, per the Terms and Conditions.
>>>

---

## Field: "Budget Estimation"

>>>
Total requested: USD 45,000, disbursed against milestones.

- Milestone 0 (on signing): USD 5,000 — specification, repository and
  infrastructure setup, Auto Drive and testnet provisioning.
- Milestone 1 (6 weeks): USD 12,000 — full-time development of the Python
  SDK and skill compiler, storage costs, documentation.
- Milestone 2 (6 weeks): USD 15,000 — contract development to audit-ready
  quality, verification tooling, deployment gas, testing.
- Milestone 3 (4 weeks): USD 13,000 — demonstration build, hosting,
  documentation, final reporting.

The budget covers sixteen weeks of full-time solo engineering plus
storage, gas, and hosting. No overhead or subcontracting is included. I am
glad to discuss scope and sizing in the Discovery phase, including the
composition of AI3 and stablecoin components.
>>>

---

## Pitch deck (optional upload — worth doing)

Eight slides: the problem in their own framing (memory is not learning) /
the mechanism / the three artefacts / why Autonomys specifically / evidence
already measured / milestones / budget / founder. Attach or link a short
screen recording of the runtime learning an unseen game live — it does more
work than any slide.

## Final checks before submitting

1. **Public repo live** — the form asks for it and the T&Cs require
   publication regardless.
2. **Discord joined**, handle filled in.
3. **AI3 wallet address** ready.
4. **Read the Grant Agreement and T&Cs yourself** — you are signing them,
   and the confidentiality clause means the grant amount cannot be
   discussed publicly afterwards.
5. **Raise the liquid/locked split in Discovery** — the T&Cs permit up to
   100% of the grant to arrive as locked AI3 at the Foundation's sole
   discretion. This is the single most material commercial term.
6. Expect up to 8 weeks of silence. That is their stated normal.
