# Nyaya

**Agents that compile experience into rules.**

A small, dependency-free runtime for sample-efficient agents on hardware
people actually own. A local language model proposes goals; learned symbolic
world-models verify, plan, and execute. Skills persist as plain, inspectable
Python -- no retraining, no cloud, auditable by reading them.

Named for the Indian school of logic: *nyaya*, literally "method, rule".

## Why

Agent inference cost is dominated by making a language model think about
things a program could carry. Measured on ARC-AGI-3 (a fluid-intelligence
benchmark of unseen interactive games, run fully offline):

- A stock LLM agent spent **~441 tokens of reasoning per environment
  action** and exhausted its budget in every game it played.
- Moving physics, search, and execution into injected programs cut that to
  **~zero tokens per action** (0.5 ms each): one tool call buys hundreds of
  verified actions, with the model reduced to naming goals and reading
  anomalies.
- The symbolic world-model learns an unseen game's physics -- the controlled
  body, per-action displacements, walls, click effects, timers -- from **a
  handful of interactions, on CPU**. On one benchmark game its dynamics
  predictions reach F1 0.67 from body-and-blocking rules alone.
- Running by itself, with **no language model at all**, the runtime clears
  levels that the LLM-driven agent never cleared inside its token budget.

The cheapest way to make a small model act intelligent is to stop making it
think about what programs can carry.

## What is in the box

- `nyaya/world_model.py` -- the theory learner: a factored, program-like
  world model (body, movement, blocking with an exoneration rule, click
  effects, autonomous movers, decay) learned online by voting, one
  transition at a time. Pure Python, zero imports, so it can be injected
  into restricted sandboxes as source.
- `nyaya/executor.py` -- policies an agent names instead of moves:
  `learn_controls`, `auto_route`, `auto_repeat`, `auto_click_all`,
  `auto_sweep`. Each runs many environment actions in one call and returns
  a compact report.
- `nyaya/sandbox_helpers.py` -- grid perception primitives: object tracking
  by rigid translation, HUD detection, breadth-first routing.
- `nyaya/delegation.py` -- the adapter that injects all of the above into a
  harness's Python-tool sandbox and corrects its prompt.

## Try it

```
python demo.py
```

Watch the runtime meet a game it has never seen, learn its physics from
probes, and clear the level by planning inside its own theory -- no language
model involved.

```
python -m pytest tests -q
```

## Where this is going

- The skills library: rules mined from experience logs, carried across
  tasks as inspectable programs (the depletion-goal discovery in our
  ARC-AGI-3 work was learned this way -- from the agent's own failure logs).
- On-device verticals that inherit the efficiency: real-time scam and fraud
  screening is the first candidate.

## Licence

MIT. The ARC-AGI-3 measurements were made with the TAAF/Duck harness
(Apache-2.0, Tufa Labs) driving a Qwen model on a single GPU; this runtime
contains none of that code and runs anywhere Python runs.
