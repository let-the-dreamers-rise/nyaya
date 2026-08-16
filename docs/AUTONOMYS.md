# Autonomys / Subspace Foundation grants: the research, and our proposal

Researched 16 August 2026. Companion to [FOUNDERS.md](FOUNDERS.md) and
[PITCH.md](PITCH.md) (the Sentient application). Different funder, different
temperament, same core repo.

## 1. What Autonomys actually is

Formerly Subspace Network: a modular Layer-1 whose consensus is
Proof-of-Archival-Storage -- farmers pledge disk space rather than burn
energy, and the chain's security IS a permanent storage network (the DSN).
On top of it: **Auto Drive** (content-addressed permanent storage with an
S3-compatible API and api keys from ai3.storage), **Auto EVM** (the EVM
domain), **Auto ID** (self-sovereign identity for humans AND agents, built
for provenance), and the **Autonomys Agents Framework** (TypeScript,
experimental, social-media-first agents whose memories are encrypted blobs
on Auto Drive anchored through an EVM contract). AI3 token generated 2025;
Phase 3 (data sharding, more domains) targeted for 2026. Founders Jeremiah
Wagstaff and Nazar Mokrynskyi have stepped back to R&D under a new
identity-industry CEO -- which explains how central Auto ID and provenance
are to their story. Foundation seat: Zug, Switzerland.

Their ideology, in their words: AI1.0 was centralized ML, AI2.0 centralized
generative AI, **AI3.0 is human-centric decentralized AI** -- billions of
personal agents with verifiable identity, humans as creators not consumers,
sovereignty over data, participation instead of UBI.

## 2. What this program is, decoded

A classic ecosystem grants program, not a VC track: milestone-based
funding (gas credits, AI3, stablecoins, or USD), up to 10% of token supply
reserved, five categories (infrastructure, AI-powered dApps, research,
community, integration), a dedicated admin team, discovery phase, Google
Form application. Temperament differs from Sentient: less crusade, more
ecosystem bootstrap -- what they fund must **use and grow their network**.
Every strong application answers one question: *how does this put real
workloads and developers onto the DSN, Auto Drive, Auto EVM, or the agents
framework?*

Their own example-project list telegraphs the fit for us: "Agent Framework
Enhancements" (AI-dApp category), "Auto Drive SDK Plugins -- LangChain,
Hugging Face" (integration category), "Storage-Compute Separation for AI"
and "Privacy-Preserving AI" (research category).

## 3. The gap we fill: memory is not learning

Their agents framework stores **memories** -- encrypted interaction blobs,
permanently, with provenance of *existence*. What no part of their stack
can do is say what an agent **learned**: the behavioural rules it derived,
whether they are any good, or whether the agent you are about to trust has
the skills it claims. "Verifiable interaction history" verifies that bytes
were stored, not that learning happened.

Nyaya is exactly the missing organ. Our runtime compiles an agent's
experience into small readable programs (world models, skills), and --
critically -- our `wm_verify` already does **replay verification**: run the
archived transitions back through the skill and score its predictions.
Put the two together on their stack and you get something neither has
alone:

> **Proof of Learning.** An agent's experience is archived on Auto Drive
> (their permanence), compiled into a readable skill (our runtime), and
> anchored on Auto EVM: skill hash + evidence hash + replayed trust score,
> signed by the agent's Auto ID. Anyone can fetch the evidence, re-run the
> replay, and check the score. A skill marketplace becomes possible where
> what is traded is *verified capability*, not claims.

This lands on their AI3.0 story exactly: agents that own verifiable
identities (Auto ID) should own verifiable *capabilities* too.

## 4. The proposal: Auto Skills (working name)

An open-source SDK + reference service, MIT like everything else we ship:

- **M1 -- Archive & compile.** Python SDK that writes agent transition
  logs to Auto Drive (S3-compatible API), and compiles archived experience
  into Nyaya skills. Works standalone with any agent loop; example bridge
  for their TypeScript agents framework via the REST API.
- **M2 -- Anchor & verify.** The provenance contract on Auto EVM: content
  hashes of skill + evidence set + trust score; `verify()` tooling anyone
  can run to re-derive the score from the archived evidence (our
  wm_verify, productized). Auto ID signature integration.
- **M3 -- Demonstrate & document.** A public demo agent that learns a task
  live, publishes its skill with proof, and a second agent that *imports*
  the verified skill and performs immediately -- skill portability across
  agents, on their rails. Tutorials + docs (their community category loves
  this; it doubles as adoption material for them).

Category: **AI-Powered dApp Grants** (their "Agent Framework
Enhancements" example) with integration-grant elements (an Auto Drive SDK
plugin for the Python/AI ecosystem they explicitly asked for). If the
admin team prefers, it splits cleanly into two smaller applications.

Why it scores on all five of their objectives: innovation in deAI (novel
verifiable-learning primitive); scalable AI infrastructure (real AI
workloads onto the DSN); accessibility (Python devs get a familiar
SDK onto Auto Drive); interoperability (bridges their TS agents world and
the Python AI world); privacy & security (verifiability is the entire
point; evidence can stay encrypted with only scores public).

## 5. Evidence we bring (measured, replicable)

The same evidence base as the Sentient application, reframed for their
reviewers: a runtime that learns an unseen game's physics from single-digit
interactions on CPU; skills as dependency-free readable Python that can be
injected anywhere; replay verification already implemented and tested
(held-out F1 0.25 aggregate, 0.67 on the best-modelled game); 87 tests; a
one-command demo. The ARC-AGI-3 work is the capability demonstration.

## 6. Application form: draft answers

- **Project name:** Auto Skills -- verifiable agent learning on Autonomys.
- **Category:** AI-Powered dApp (Agent Framework Enhancement), with an
  integration component (Auto Drive Python SDK plugin).
- **Summary:** Agents on Autonomys can already remember permanently; they
  cannot yet prove what they learned. Auto Skills compiles archived agent
  experience from Auto Drive into readable, replay-verifiable skills
  anchored on Auto EVM with Auto ID provenance -- turning permanent memory
  into portable, provable capability.
- **Why Autonomys:** the primitive needs permanence (DSN), cheap
  content-addressed access (Auto Drive), an execution layer for anchoring
  (Auto EVM), and agent identity (Auto ID). No other stack ships all four.
- **Team:** solo technical founder (see repo; 87 tests; measured results);
  milestone-based delivery suits a solo builder and their process.
- **Funding ask:** fill per their guidance in discovery -- milestone-based,
  three milestones as above; accept stablecoins/USD; state openness to
  sizing with the admin team. (Do not invent a number before reading
  their agreement template; the sample agreement and T&Cs are linked on
  the program page.)
- **Timeline:** M1 6 weeks, M2 6 weeks, M3 4 weeks from grant start.

## 7. Honest notes

- Their agents framework is explicitly experimental; we depend only on
  Auto Drive (stable, S3-compatible) and Auto EVM for anchoring -- the
  bridge to their TS framework is an example, not a dependency. Say this;
  reviewers respect risk-managed design.
- This is a grant, not investment: no equity story needed, milestones and
  deliverables instead. It funds exactly the hardening the Sentient
  investment pitch promises -- the two applications compound, and both
  products are MIT so there is no conflict.
- The AGI/ARC work is paused by choice right now; nothing in this proposal
  depends on resuming it, but every improvement there strengthens the
  evidence section here.

## 8. Before submitting (user actions)

1. Read their sample Grant Agreement + T&Cs (linked on the program page)
   -- Swiss foundation, token-denominated payments possible: check tax and
   KYC comfort.
2. Get an Auto Drive API key at ai3.storage (free tier) so the application
   can say the integration is already being prototyped.
3. Approve the public push of the nyaya repo -- both this and the Sentient
   application need the repo URL.
3. Submit via their Google Form; the discovery-phase call is where the
   funding size gets set.
