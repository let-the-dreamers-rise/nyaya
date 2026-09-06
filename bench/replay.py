"""The causal-replay protocol: predict before learning, learn after.

One rule governs the whole benchmark and it is the reason the numbers mean
anything: **at transition i, a method may use only transitions 0..i-1.** It
predicts, is scored, and only then observes. No method ever sees the frame it
is being scored on, so nothing here can be won by memorisation.

What is scored:

- `exact` -- the predicted frame is identical to the real one. Easy to inflate
  on boards that are mostly background; reported, never headlined.
- `f1` -- precision and recall over **cells that actually changed**. Copy-
  forward scores 0 here by construction, so this isolates learned dynamics
  from scenery. This is the headline number.
- `tokens` and `seconds` -- cost per hypothesis revision. Published because
  the literature does not, and because methods that are close on quality can
  differ by orders of magnitude here.
- `to_threshold` -- transitions observed before the method's trailing
  prediction quality first crosses a bar. This is the sample-efficiency
  number, and it is what "learns from a handful of interactions" has to mean
  if the claim is going to be checkable.
"""
from __future__ import annotations

import time


def score_step(predicted, before, after):
    """(exact, tp, fp, fn) for one transition, over changed cells only."""
    exact = predicted == after
    tp = fp = fn = 0
    for r in range(len(after)):
        row_p = predicted[r] if r < len(predicted) else ""
        row_b = before[r] if r < len(before) else ""
        for c in range(len(after[r])):
            real = after[r][c]
            was = row_b[c] if c < len(row_b) else ""
            said = row_p[c] if c < len(row_p) else was
            real_changed = real != was
            said_changed = said != was
            if said_changed and real_changed and said == real:
                tp += 1
            elif said_changed and (not real_changed or said != real):
                fp += 1
            elif real_changed and not said_changed:
                fn += 1
    return exact, tp, fp, fn


def f1_of(tp: int, fp: int, fn: int) -> float:
    return 2 * tp / (2 * tp + fp + fn) if (tp + fp + fn) else 0.0


def replay(method, chain, threshold: float = 0.5, window: int = 25) -> dict:
    """Run one method over one episode under the protocol. Returns metrics."""
    exact = tp = fp = fn = 0
    predict_s = observe_s = 0.0
    recent: list = []
    to_threshold = None

    for index, (before, action, after) in enumerate(chain):
        started = time.perf_counter()
        predicted = method.predict(before, action)
        predict_s += time.perf_counter() - started

        hit, a, b, c = score_step(predicted, before, after)
        exact += hit
        tp += a
        fp += b
        fn += c

        # Trailing quality over a window, so a method that learns late is
        # not credited for its early ignorance.
        recent.append((a, b, c))
        if len(recent) > window:
            recent.pop(0)
        if to_threshold is None and len(recent) == window:
            w_tp = sum(x[0] for x in recent)
            w_fp = sum(x[1] for x in recent)
            w_fn = sum(x[2] for x in recent)
            if f1_of(w_tp, w_fp, w_fn) >= threshold:
                to_threshold = index + 1

        started = time.perf_counter()
        method.observe(before, action, after)
        observe_s += time.perf_counter() - started

    n = len(chain)
    return {
        "transitions": n,
        "exact": exact / n if n else 0.0,
        "f1": f1_of(tp, fp, fn),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "to_threshold": to_threshold,
        "tokens": int(getattr(method, "tokens", 0)),
        "seconds": predict_s + observe_s,
        "ms_per_step": 1000 * (predict_s + observe_s) / n if n else 0.0,
    }


def aggregate(rows: list) -> dict:
    """Pool across episodes. Cells are pooled, not averaged over episodes:
    averaging per-episode F1 would let a 20-transition episode outvote a
    400-transition one."""
    tp = sum(r["tp"] for r in rows)
    fp = sum(r["fp"] for r in rows)
    fn = sum(r["fn"] for r in rows)
    n = sum(r["transitions"] for r in rows)
    reached = [r["to_threshold"] for r in rows if r["to_threshold"] is not None]
    return {
        "episodes": len(rows),
        "transitions": n,
        "exact": sum(r["exact"] * r["transitions"] for r in rows) / n if n else 0.0,
        "f1": f1_of(tp, fp, fn),
        "tokens": sum(r["tokens"] for r in rows),
        "seconds": sum(r["seconds"] for r in rows),
        "ms_per_step": 1000 * sum(r["seconds"] for r in rows) / n if n else 0.0,
        "reached_threshold": len(reached),
        "median_to_threshold": sorted(reached)[len(reached) // 2] if reached else None,
    }
