# Subspace Foundation grant form: paste-ready answers

Written against the real form fields. Research behind every choice:
[AUTONOMYS.md](AUTONOMYS.md). Idea locked: **Auto Skills**.

**Why this idea, in one line:** their own announcement defines the
AI-powered dApps & Agents category as *applications enabling verifiable,
on-chain intelligent behavior* -- and their homepage argues unverifiable
agent memory is a first-class vulnerability. They made an agent's inputs
trustworthy. Nothing yet makes its conclusions trustworthy. Auto Skills is
that missing half, named to sit beside Auto Drive, Auto EVM, Auto ID.

---

## Contact fields

- **Full Name:** Ashwin Goyal
- **Email:** (the account you submit from -- note the form is bound to
  kodezephyr@gmail.com; use whichever address you want grant mail on)
- **Discord / Telegram:** join their Discord before submitting; the grants
  team works there and a handle makes you reachable
- **AI3 Wallet Address:** optional now, required before Milestone 0 is
  paid -- a Subwallet/Talisman address for Autonomys works
- **Project website:** optional; the GitHub repo is enough at this stage
- **GitHub link:** the public nyaya repo (must be public before you
  submit -- their T&C requires publication anyway)
- **X / LinkedIn:** whatever you actually use; leave blank rather than
  linking something dormant

## Category

**AI-Powered dApp** (their announcement: "AI-powered dApps & Agents --
verifiable, on-chain intelligent behavior"). Mention in the proposal that
it also delivers an Integration-category artefact (the first Python SDK
for Auto Drive), so a reviewer can reclassify without rejecting.

## Project description / problem

Agents on Autonomys can already remember permanently. They cannot prove
what they learned.

Auto Drive gives an agent immutable context -- memory that cannot drift,
be poisoned, or vanish between calls. But the step that turns memory into
behaviour is still a black box: the rules an agent derives from experience
live in opaque context windows or closed fine-tunes. When one agent hands
work to another, or a user delegates money and identity to one, there is
no way to ask the only question that matters -- what has this agent
actually learned, and is it any good?

Auto Skills closes that gap. It compiles an agent's archived experience
into small, human-readable skill programs, scores each one by replaying it
against the recorded evidence, and anchors the result on-chain: skill hash
+ evidence hash + replay score, signed by the agent's Auto ID. Anyone can
fetch the evidence from Auto Drive, re-run the replay, and independently
verify the score. Learning becomes a first-class, portable, provable
object -- and skills can be shared between agents instead of every agent
relearning the same lesson.

The learning engine already exists and is open source (MIT): a
dependency-free runtime that learns an environment's rules from a handful
of interactions on CPU, and a replay verifier that scores a learned model
against recorded transitions. It was built and measured on ARC-AGI-3, a
benchmark designed to resist memorisation; the runtime learns unseen games
and solves levels with no language model in the loop. This grant puts that
engine on Autonomys rails.

## Project Proposal (the required long answer)

**What we build.** Three artefacts, all MIT, all in one public repo:

1. **auto-skills-py** -- the first Python SDK for Auto Drive. Their Auto
   SDK is TypeScript/JavaScript only, while the AI ecosystem their own
   example-projects page asks to reach (LangChain, Hugging Face) is
   Python-native. This writes agent transition logs to Auto Drive over the
   S3-compatible/REST interface, and reads them back for replay.
2. **The skill compiler and verifier.** Turns archived experience into a
   readable skill program, then scores it by replay against held-out
   recorded transitions -- honest evidence, not self-report.
3. **The provenance contract on Auto EVM.** Publishes skill hash, evidence
   CID, and replay score, with Auto ID attestation. A `verify` command
   anyone can run to re-derive the score from the archived evidence.

**Why it must be Autonomys.** The primitive needs four things at once:
permanence so evidence cannot be quietly edited (DSN), cheap
content-addressed retrieval so anyone can re-verify (Auto Drive), an
execution layer to anchor claims (Auto EVM), and agent identity to sign
them (Auto ID). No other stack ships all four. On any other chain this
project would need three vendors and a trust assumption.

**What it gives the ecosystem.** Real AI workloads onto the DSN (every
verified skill is archived evidence, not a hash of nothing); the Python
front door their SDK currently lacks; and a reason for agent builders
outside web3 to touch Autonomys at all -- verifiable capability is useful
whether or not you care about blockchains.

**Risk management.** We depend only on stable pieces: Auto Drive and Auto
EVM. Their Agents Framework is marked experimental, so integration with it
ships as an example, never as a dependency. If Auto ID's public tooling is
not ready in the grant window, attestation degrades gracefully to a plain
EVM signature and upgrades later.

**Openness.** MIT, public GitHub from day one, docs under CC BY 4.0 --
already compliant with the T&C's licence list with no changes required.

## Milestones and Deliverables

**Milestone 0 -- on signing.** Wallet and KYC complete; public repo,
project board, and technical spec published.

**Milestone 1 (6 weeks) -- Archive & Compile.**
- `auto-skills-py`: upload/download agent experience logs to Auto Drive,
  with tests against the live network and published docs.
- Skill compiler: archived experience in, readable skill program out.
- Deliverable: working package, public repo, tutorial, demo video.

**Milestone 2 (6 weeks) -- Anchor & Verify.**
- Provenance contract deployed on Auto EVM (testnet then mainnet).
- `verify` tooling: fetch evidence by CID, replay, re-derive score,
  compare against the anchored claim.
- Auto ID attestation where the public tooling permits.
- Deliverable: deployed contract with verified source, CLI, docs, tests.

**Milestone 3 (4 weeks) -- Demonstrate & Document.**
- Public demo: agent A learns a task live, publishes a proven skill; agent
  B imports the verified skill and performs immediately -- portable,
  provable capability on their rails.
- Example bridge to the Autonomys Agents Framework.
- Deliverable: hosted demo, walkthrough article for their blog, full
  documentation, final report.

## Budget Estimation

Proposed total **USD 45,000**, milestone-weighted. They do not publish
ranges, so treat this as an opening position for the discovery call, not a
fixed demand:

| Milestone | Amount | Covers |
|---|---|---|
| M0 on signing | 5,000 | setup, spec, infrastructure |
| M1 archive & compile | 12,000 | ~6 weeks build, Auto Drive costs |
| M2 anchor & verify | 15,000 | ~6 weeks build, audit-quality contract work, gas |
| M3 demo & docs | 13,000 | ~4 weeks build, hosting, documentation |

Solo founder, four months of full-time work plus storage, gas and hosting.
**Ask about the liquid/locked split in the discovery call** -- the T&C
allows up to 100% of the grant to arrive as locked AI3 at their sole
discretion, which materially changes what this budget is worth.

## Pitch deck upload

Optional but worth doing -- eight slides: the problem (memory is not
learning, in their own words), the mechanism, the three artefacts, why
Autonomys specifically, evidence already measured, milestones, budget,
founder. A short screen recording of the runtime learning a game live is
worth more than any slide.

## Before you press submit

1. Public repo live (their T&C requires it; the form asks for the link).
2. Discord joined, handle in the form.
3. AI3 wallet address ready.
4. Read the Grant Agreement and T&Cs yourself -- you are signing them, and
   the confidentiality clause means you cannot publicly discuss the grant
   amount afterwards.
5. Expect up to 8 weeks of silence. That is their stated normal, not a
   rejection.
