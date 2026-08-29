"""The bridge demo: a scam-screening skill learned on CPU, readable, yours.

Runs the whole product claim end to end on real data:

  1. learn a skill from 4,459 labelled SMS (public UCI corpus) on CPU
  2. measure it on 1,115 held-out real messages
  3. show the skill is PORTABLE evidence, not a black box: apply it to
     Indian scam patterns (KYC freeze, digital arrest, UPI cashback --
     an illustrative seed set), watch it degrade honestly
  4. adapt with just 32 local examples and measure the recovery
  5. write the skill to skills/sms_scam_skill.py -- a Python file a person
     can open, edit and own -- then edit it live and watch the guardian
     change its mind

    python demo_scam.py
"""
from __future__ import annotations

import random
import time
from pathlib import Path

from nyaya import sms_rules as sr

HERE = Path(__file__).parent


def pct(x):
    return f"{100 * x:.1f}%"


def show(name, stats, n):
    print(
        f"  {name:<34} precision {pct(stats['precision'])}  "
        f"recall {pct(stats['recall'])}  F1 {stats['f1']:.3f}   (n={n})"
    )


def main():
    print(__doc__)

    uci = sr.read_tsv(HERE / "data" / "sms.tsv")
    india = sr.read_tsv(HERE / "data" / "india_seed.tsv")
    random.Random(7).shuffle(uci)
    cut = int(0.8 * len(uci))
    train, held = uci[:cut], uci[cut:]
    adapt_in = india[0::2]
    adapt_out = india[1::2]

    started = time.perf_counter()
    skill = sr.learn(train)
    elapsed = time.perf_counter() - started
    print(
        f"learned {len(skill['rules'])} readable rules from {len(train)} "
        f"messages in {elapsed:.2f}s on CPU -- no GPU, no network, no weights"
    )
    print("\nthe strongest rules it chose for itself:")
    for desc, _, _, weight, s, h in sorted(
        skill["rules"], key=lambda r: -abs(r[3])
    )[:8]:
        side = "accuses" if weight > 0 else "vouches"
        print(f"  {weight:+d}  {desc}  ({side}; saw it in {s} scams, {h} normal)")

    print()
    show("held-out real SMS (UCI)", sr.evaluate(skill, held), len(held))
    show("Indian patterns, zero-shot", sr.evaluate(skill, india), len(india))

    adapted = sr.learn(train + adapt_in)
    show(
        f"after adapting on {len(adapt_in)} local examples",
        sr.evaluate(adapted, adapt_out),
        len(adapt_out),
    )

    out = HERE / "skills" / "sms_scam_skill.py"
    provenance = (
        f"\nLearned {time.strftime('%Y-%m-%d')} from {len(train)} UCI SMS + "
        f"{len(adapt_in)} Indian seed examples, on CPU, in under a second."
    )
    out.write_text(sr.render_skill(adapted, provenance), encoding="utf-8")
    print(f"\nskill written to {out.relative_to(HERE)} -- open it; it is a page of Python")

    message = (
        "Congratulations! Your number won Rs 25,00,000 in the lucky draw. "
        "To claim call 8745120369 and pay processing fee Rs 6500 today"
    )
    total, fired = sr.score(adapted, message)
    print(f"\nincoming: {message[:70]}...")
    print(f"verdict: {'SCAM' if total >= adapted['threshold'] else 'ok'} (score {total}, threshold {adapted['threshold']})")
    for desc, weight in fired:
        print(f"    {weight:+d} {desc}")

    # Ownership demo: the user opens THEIR copy of the skill file and
    # deletes the beliefs that fired. The verdict must actually flip --
    # editability that changes nothing would be a lie in a demo about
    # editability.
    namespace: dict = {}
    exec(out.read_text(encoding="utf-8"), namespace)
    owned = sr.load_skill(namespace)
    accusing = {desc for desc, weight in fired if weight > 0}
    owned["rules"] = [r for r in owned["rules"] if r[0] not in accusing]
    total2, _ = sr.score(owned, message)
    flipped = total2 < owned["threshold"]
    print(
        f"\nthe user deletes the {len(accusing)} accusing rules from THEIR "
        f"copy of the file: score {total} -> {total2}, verdict "
        f"{'SCAM' if not flipped else 'ok'}. The guardian changed its mind "
        "because its owner edited its beliefs. That is the product."
    )


if __name__ == "__main__":
    main()
