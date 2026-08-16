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

## 2.5 The legal terms, read in full (from the actual PDFs)

Both documents were downloaded and text-extracted, not skimmed. What they
actually say:

**Eligibility.** Open to applicants from any country except sanctioned
territories or where crypto is banned. The excluded list is Afghanistan,
Belarus, Myanmar, CAR, Cuba, DRC, Iran, Iraq, Lebanon, Libya, Mali,
Nicaragua, North Korea, Russia, Somalia, South Sudan, Sudan, Syria,
occupied regions of Ukraine, Venezuela. **India is not excluded** and
crypto is not banned there, so a solo Indian founder is eligible.
Individuals qualify -- no company required. Legal majority, no fraud
history, no pending proceedings.

**KYC/KYB is mandatory** for successful applicants, plus sanctions
screening and possible verification of credentials or references.

**IP: the good news.** All IP created under the grant **belongs to the
Grantee**. The obligation is to open-source it: code must be published to
a designated public GitHub repo under 0BSD, BSD, MIT, or Apache 2.0 (or
another licence pre-approved in writing). Non-software deliverables go
under CC BY 4.0. Nyaya is already MIT, so we comply with no change.
Breaching the open-source requirement lets them demand repayment or take
assignment of the IP -- fair, and irrelevant if we ship open anyway.

**Payment, and the one real risk.** Milestone-based, with a **Milestone 0
initial disbursement paid on signing** (before any work). Currencies: AI3
tokens, stablecoins, or USD, *at the Foundation's sole discretion*. The
clause to negotiate: the **Locked AI3 portion may be up to 100% of the
total grant**, locked for a period they set at their sole discretion. A
grant could therefore arrive entirely as illiquid tokens. Raise the
liquid/locked split explicitly in the discovery call -- it is the single
most material commercial term.

**Obligations.** Monthly updates within 5 days of each month's end (with
a financial summary), a milestone report per milestone, and a final
narrative plus financial report within 30 days of completion. Unspent
funds must be returned. **Confidentiality: the grant amount and terms are
confidential** unless they authorise disclosure.

**Jurisdiction.** Swiss law, exclusive courts of Zug. Signed for the
Foundation by Markus Spillmann, Council President. Grantee bears their own
tax liability -- worth an accountant's opinion on Indian treatment of
token grants.

**Process reality.** Up to **8 weeks** for a first response, then a
discovery deep-dive call, then 2-4 weeks to decision. Evaluated on
mission relevance, technical feasibility, ecosystem impact, and team
capability. Their own words in the T&C: applications should be rich in
technical detail. The form itself sits behind a Google sign-in, so
submission needs a logged-in Google account.

**Precedent.** They have already funded **Momento** -- a protocol for
capturing and verifying content as tamper-proof, user-owned records on
Auto Drive + Auto EVM. Provenance-and-verification projects are exactly
what this program has been buying.

## 3. The gap we fill: memory is not learning

Their agents framework stores **memories** -- encrypted interaction blobs,
permanently, with provenance of *existence*. What no part of their stack
can do is say what an agent **learned**: the behavioural rules it derived,
whether they are any good, or whether the agent you are about to trust has
the skills it claims. "Verifiable interaction history" verifies that bytes
were stored, not that learning happened.

And this is their own framing, not ours imposed on them. Their homepage
argues that **unverifiable agent memory** is a first-class vulnerability
alongside hallucination, and sells Auto Drive as immutable context that
cannot drift, be poisoned, or vanish between calls. They have made the
agent's *inputs* trustworthy. Nobody has made the agent's *conclusions*
trustworthy. Pitch it in exactly that sequence: you fixed memory drift;
this fixes learning drift. It is the next sentence of their own argument.

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

1. **Get an Auto Drive API key** at ai3.storage (free tier) so the
   application can honestly say the integration is already prototyped.
   Their SDK is TypeScript-only but Auto Drive is S3-compatible with a
   REST API, so Python works today -- and *that gap is itself part of the
   pitch* (they explicitly ask for LangChain / Hugging Face plugins, which
   are Python-native, while shipping no Python SDK).
2. **Approve the public push of the nyaya repo.** Their T&C requires
   publication to a designated public GitHub repo; both this and the
   Sentient application need the URL. MIT already satisfies their licence
   list.
3. **Decide your KYC and tax comfort**: KYC/KYB is mandatory, payment may
   be up to 100% locked AI3 at their discretion, and grantees carry their
   own tax liability. Worth an accountant's view on Indian treatment of
   token grants before signing.
4. **Be ready for a Google sign-in** -- the form requires one.
5. Submit; expect up to 8 weeks to first response. Negotiate the
   liquid/locked split and milestone sizing in the discovery call.

## 9. What I read to write this

Every link on their program page, plus the primary documents: the AI3.0
thesis post; example-projects; application-process; the program page;
tokenomics (1B supply, Foundation treasury 15.68%, 48-month vesting with
12-month cliff, TGE at Phase-2); the **Sample Grant Agreement (20 pages,
text-extracted)**; the **Grant Program T&C (14 pages, text-extracted)**;
autonomys.xyz (182 nodes, 21.71 PB pledged, 240 ms retrieval, 256x
replication, mainnet since Q4 2024); academy and docs sites;
develop.autonomys.xyz (Auto SDK is TypeScript/JavaScript; Auto Drive has
REST + S3 + rclone; Auto EVM with MetaMask/Foundry/Hardhat; Auto ID
documented but thin); the agents framework repo (TypeScript, MIT,
explicitly experimental); and the news page (Momento grant, Guardians of
Growth staking seasons). The only thing I could not read is the form's own
questions -- it sits behind a Google login, and the process page
enumerates them instead.
