"""Build docs/nyaya-sentient.pdf, the supporting document for the Sentient form.

Eight pages, every number copied from the README tables of the day it was
built. Needs reportlab (`pip install reportlab`); the package itself stays
standard-library only, this is a build script.

    python scripts/make_pdf.py
"""
from __future__ import annotations

from pathlib import Path

from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).resolve().parents[1] / "docs" / "nyaya-sentient.pdf"
INK = colors.HexColor("#111827")
MUTED = colors.HexColor("#5B6470")
ACCENT = colors.HexColor("#2457D6")
HAIR = colors.HexColor("#D8DDE3")
SOFT = colors.HexColor("#EDF0F3")

H1 = ParagraphStyle("h1", fontName="Times-Roman", fontSize=30, leading=34, textColor=INK, spaceAfter=10)
H2 = ParagraphStyle("h2", fontName="Times-Roman", fontSize=21, leading=25, textColor=INK, spaceAfter=8)
EYE = ParagraphStyle("eye", fontName="Courier", fontSize=8.5, leading=11, textColor=MUTED, spaceAfter=6)
BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK, spaceAfter=8, alignment=TA_LEFT)
LEDE = ParagraphStyle("lede", parent=BODY, fontSize=12, leading=17)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=9, leading=12.5, textColor=MUTED)
BIG = ParagraphStyle("big", fontName="Times-Roman", fontSize=40, leading=44, textColor=INK)


def p(text, style=BODY):
    return Paragraph(text, style)


def table(rows, widths, highlight=None):
    t = Table(rows, colWidths=widths, hAlign="LEFT")
    style = [
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
        ("FONT", (0, 1), (-1, -1), "Courier", 9),
        ("FONT", (0, 1), (0, -1), "Helvetica", 9.5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, HAIR),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, HAIR),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if highlight is not None:
        style.append(("BACKGROUND", (0, highlight), (-1, highlight), colors.HexColor("#E4ECFB")))
    t.setStyle(TableStyle(style))
    return t


def curve():
    """Capability against cost per game: two measured points, one at $0, and the gap."""
    w, h = 470, 230
    d = Drawing(w, h)
    x0, y0, x1, y1 = 40, 30, 450, 210

    def X(dollars):
        return x0 + (x1 - x0) * dollars / 200

    def Y(rhae):
        return y0 + (y1 - y0) * rhae / 100

    d.add(Polygon([X(0), Y(3.4), X(119), Y(100), X(119), Y(0), X(0), Y(0)], fillColor=SOFT, strokeColor=None))
    d.add(Line(X(0), Y(3.4), X(119), Y(100), strokeColor=colors.HexColor("#9AA3AE"), strokeWidth=1.2, strokeDashArray=[5, 5]))
    d.add(Line(x0, y0, x1, y0, strokeColor=HAIR))
    d.add(Line(x0, y0, x0, y1, strokeColor=HAIR))
    for v in (0, 25, 50, 75, 100):
        d.add(String(x0 - 6, Y(v) - 3, str(v), fontName="Courier", fontSize=7, fillColor=MUTED, textAnchor="end"))
    for v in (0, 50, 100, 150, 200):
        d.add(String(X(v), y0 - 12, f"${v}", fontName="Courier", fontSize=7, fillColor=MUTED, textAnchor="middle"))
    d.add(String(x0, y1 + 8, "capability (RHAE, public set)", fontName="Helvetica", fontSize=7.5, fillColor=MUTED))
    d.add(String(x1, y0 - 24, "inference cost per game", fontName="Helvetica", fontSize=7.5, fillColor=MUTED, textAnchor="end"))
    d.add(String((X(0) + X(119)) / 2 - 20, (Y(3.4) + Y(100)) / 2 - 30, "unmeasured", fontName="Times-Italic", fontSize=14, fillColor=MUTED, textAnchor="middle"))
    for dollars, rhae, label, sub, anchor, dy in (
        (0, 3.4, "nyaya runtime", "$0, ~3.4 RHAE, no model in the loop", "start", 6),
        (119, 100, "Tycho, Opus 5", "~$119, 100 RHAE", "middle", -22),
        (179, 100, "Tycho, GPT-5.6 Sol", "~$179, 100 RHAE", "middle", -22),
    ):
        d.add(Circle(X(dollars), Y(rhae), 4.5, fillColor=ACCENT, strokeColor=colors.white, strokeWidth=1.5))
        lx = X(dollars) + (10 if anchor == "start" else 0)
        d.add(String(lx, Y(rhae) + dy, label, fontName="Helvetica-Bold", fontSize=8, fillColor=INK, textAnchor=anchor))
        d.add(String(lx, Y(rhae) + dy - 10, sub, fontName="Courier", fontSize=6.5, fillColor=MUTED, textAnchor=anchor))
    return d


def build():
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
                            topMargin=20 * mm, bottomMargin=18 * mm,
                            title="Nyaya: the price of a world model", author="Ashwin Goyal")
    s = []

    # 1. cover
    s += [p("NYAYA  ·  SENTIENT OPEN SOURCE AGI GRANT PROGRAMME  ·  10 SEPTEMBER 2026", EYE),
          p("The price of a world model", H1),
          p("ARC-AGI-3 was solved on its public set this year for about <b>$119 a game</b>. Nobody has "
            "measured what happens when you spend less. This is the substrate to find out, the runtime at the "
            "free end of the curve, and the first results, including the ones that went against us.", LEDE),
          Spacer(1, 10), curve(), Spacer(1, 6),
          p("Every point is someone's published number, plotted on one axis nobody else uses. Tycho reports its "
            "cost in a footnote and lists excluding it from the efficiency metric as a limitation. OPINE-World "
            "reports no cost at all, so it cannot be placed.", SMALL),
          Spacer(1, 14),
          table([["", "", ""],
                 ["$0", "2.4%", "0 of 244"],
                 ["per game, no model in the loop", "of actions delegable today, 57% right", "programs an 8B model wrote that survived the verifier"]],
                [150, 150, 166]),
          Spacer(1, 18),
          p("Ashwin Goyal, student, India  ·  ashwingoyal2006@gmail.com  ·  github.com/let-the-dreamers-rise/nyaya  ·  MIT", SMALL),
          PageBreak()]

    # 2. the question
    s += [p("1 / THE QUESTION MOVED, SO WE MOVED WITH IT", EYE), p("Capability is answered. Price is not.", H2),
          p("In July 2026 two systems put frontier language models inside a world model's learning loop and largely "
            "closed the benchmark. In their own tables, program synthesis <i>without</i> a model in the loop clears "
            "zero levels. So capability is answered, and not in our favour. <b>Price is not answered by anyone.</b>", LEDE),
          p("The difference between $119 a game and $0 a game is the whole difference between a demonstration and "
            "something that runs on a phone, offline, for a person nobody is billing. That is the axis this "
            "programme measures, and then tries to move along."),
          Spacer(1, 6),
          table([["system", "model in loop", "result", "cost / game", "code"],
                 ["Tycho", "Opus 5", "100.00 RHAE, 183/183", "~$119", "Apache-2.0"],
                 ["Tycho", "GPT-5.6 Sol", "100.00 RHAE, 183/183", "~$179", "Apache-2.0"],
                 ["OPINE-World", "Opus 4.8", "20/25 games, 160/183", "not reported", "none"],
                 ["WorldCoder (run by OPINE)", "--", "0 levels", "--", "public"],
                 ["nyaya", "none", "2-4 early levels", "$0", "MIT"]],
                [120, 80, 130, 80, 56], highlight=5),
          Spacer(1, 10),
          p("What exists today, not what is promised: 50 episodes across two corpora, 24,499+ transitions, a "
            "causal-replay protocol (predict, be scored, then observe) with cost reported next to every score; a "
            "synthesiser that searches for programs on CPU with no model called, ever; 251 tests, standard library "
            "only; CI that regenerates every held-out table on every push."),
          PageBreak()]

    # 3. results
    s += [p("2 / THE RESULTS, WITH THE INTERVALS WE WERE TEMPTED TO LEAVE OUT", EYE),
          p("No method dominates and every interval overlaps.", H2),
          p("Five methods, one protocol, two corpora. The second corpus was never developed against. Every score "
            "carries a 95% bootstrap interval over episodes, and where intervals overlap we say <i>not shown to "
            "differ</i> rather than quoting the larger number."),
          table([["method", "dev F1", "reached", "held-out F1", "reached", "ms/step"],
                 ["copy-forward (null)", "0.000", "0/25", "0.000", "0/25", "0.00"],
                 ["memorise (lookup table)", "0.048", "3/25", "0.024", "0/25", "0.01"],
                 ["last-effect (one line)", "0.228  .136-.316", "11/25", "0.151  .065-.289", "6/25", "0.09"],
                 ["nyaya-templates", "0.185  .043-.355", "6/25", "0.253  .039-.490", "5/25", "3.8"],
                 ["dsl-synthesis-rel", "0.204  .119-.286", "6/25", "0.237  .134-.348", "7/25", "7.9"]],
                [118, 96, 50, 96, 50, 56], highlight=5),
          Spacer(1, 8),
          p("Two things are still visible. <b>memorise</b> scores near zero, so the corpus is genuinely novel: the "
            "benchmark measures generalisation, and that is now a measured fact rather than a hope. And the "
            "synthesis engine is the only method never worst on either corpus, with an interval a third the width "
            "of the template learner it replaces. It got there by changing the hypothesis class in response to a "
            "diagnosis, twice, which is the mechanism this whole programme is about."),
          p("A program the search found on its own, precision 1.00 over 90 examples:", SMALL),
          p("<font face='Courier'>when action is 'RIGHT' and right2 is 'b' and self is 'c', it becomes 'b'</font>", SMALL),
          PageBreak()]

    # 4. delegation
    s += [p("3 / HOW MUCH OF AN AGENT CAN YOU OWN AT $0?", EYE), p("Two percent, today. Measured, then moved.", H2),
          p("The delegation architecture says a frontier model proposes goals and reads anomalies while a world "
            "model that costs nothing handles the steps it has already learned. Nobody had measured how many "
            "steps the free end could take. So we did, on 3,318 transitions of games the learners had never seen, "
            "scored after the fact. An action is <i>delegable</i> when the model committed to a prediction and the "
            "whole frame was right."),
          table([["method (held-out, 3,318 actions)", "commits", "commit right", "delegable"],
                 ["last-effect", "22.7%", "8.6%", "2.0%"],
                 ["nyaya-templates", "38.1%", "2.5%", "0.9%"],
                 ["dsl-synthesis-rel", "59.0%", "0.7%", "0.4%"],
                 ["last-effect, completeness gate", "1.2%", "50.0%", "0.6%"],
                 ["nyaya-templates, completeness gate", "1.0%", "32.4%", "0.3%"],
                 ["dsl-synthesis-rel, completeness gate", "0.6%", "21.1%", "0.1%"],
                 ["union of the three gates", "2.7%", "38.5%", "1.1%"],
                 ["memorise (exact recurrence)", "1.5%", "90.0%", "1.4%"],
                 ["union of the gates and memorise", "4.2%", "56.7%", "2.4%"]],
                [220, 80, 90, 76], highlight=9),
          Spacer(1, 8),
          p("The learners over-commit: synthesis claims 59% of actions and is right on under one percent. Gating on "
            "per-rule evidence changes nothing. Gating on <b>completeness</b>, committing only when the current "
            "theory reproduces the action's last frames exactly, lifts every learner to 20 to 50% right. The gated "
            "learners cover different actions, so their union with exact recurrence reaches 2.4% delegable at 57% "
            "right, above the ungated heuristic with seven times its precision. 1.4 of the 2.4 points are recall, "
            "not generalisation, and are labelled so. <b>The commit criterion is solved and cheap. The theories are "
            "what is incomplete. That is the research.</b>"),
          p("The log, so the slope is visible and not only the level: 9 Sep morning, first measurement, 0.4 to 2.0% "
            "delegable. 9 Sep afternoon, whole-effect gate, precision 8.6 to 51.4%. 9 Sep evening, completeness gate "
            "on every learner. 10 Sep, union 1.1%; with exact recurrence 2.4% at 56.7%. The delegable number moved "
            "from 0.6% to 2.4% in a day without touching a learner.", SMALL),
          PageBreak()]

    # 5. competitor
    s += [p("4 / THE COMPETITOR'S ROW, RUN BY US", EYE), p("EvoSkill's loop, an open model, the same verifier.", H2),
          p("Sentient's EvoSkill loop is propose, generate, evaluate: a model reads what went wrong, writes a skill "
            "as code, and the skill is kept if it survives evaluation. We put that loop on the benchmark's interface "
            "with the same replay verifier every $0 method faces: the program is kept only if it reproduces every "
            "example it was shown. The model is the open 8B model on the author's laptop (granite3.2:8b), so the "
            "row is priced in tokens and minutes. First five held-out games, 709 transitions:"),
          table([["method", "commits", "delegable", "changed-cell F1", "tokens"],
                 ["llm-skill (one prompt)", "0.0%", "0.0%", "0.000", "156,438"],
                 ["llm-skill-feedback (verdict fed back once)", "0.0%", "0.0%", "0.000", "179,864"],
                 ["last-effect ($0)", "24.1%", "2.8%", "0.181", "0"],
                 ["dsl-synthesis-rel ($0)", "45.1%", "1.3%", "0.130", "0"]],
                [210, 60, 66, 80, 60]),
          Spacer(1, 8),
          p("The model wrote 107 programs in about a hundred minutes, then 137 more with the evaluator's failing "
            "cells named. Every one was a syntactically valid <font face='Courier'>predict</font>. None reproduced "
            "the two frames it had just been shown, so none was ever allowed to commit. Every prompt and reply is "
            "committed under <font face='Courier'>bench/llm-cache/</font>, so the row replays without a model and "
            "anyone can read what the model wrote."),
          p("<b>What this row says and does not say.</b> It is the floor of the loop, not its ceiling: at most two "
            "prompts, a small model. It does not say the loop is useless; Tycho's version of it clears the public "
            "set with a frontier model. It says the loop's value is in the model, and the model is what costs $119 "
            "a game. Between an 8B model that produces nothing and a frontier model that produces everything, "
            "nobody has measured the curve. Measuring it is what the grant buys."),
          PageBreak()]

    # 6. retractions
    s += [p("5 / WHAT WE GOT WRONG, IN THE ORDER WE FOUND OUT", EYE), p("The strongest thing in this document.", H2),
          p("A funder is not buying a result. They are buying what a person does when the evidence goes against "
            "them. Here is the record.", LEDE)]
    for when, was, now in (
        ("7 Sep 2026", "Precision 100%, recall 78%, F1 0.875 on real messages.",
         "True, and beside the point: naive Bayes gets 0.965 on the identical split in a thirtieth of the time. "
         "Published in the README above our own number. The honest claim became <i>readability costs nine points "
         "of F1</i>, which nobody had priced before."),
        ("7 Sep 2026", "Nobody has beaten this benchmark.",
         "False since July. Tycho hit 100.00 RHAE. The proposal was re-scoped in public from <i>a better learner</i> "
         "to <i>the price of a world model</i>, and the retraction has its own file."),
        ("7 Sep 2026", "The template learner reaches F1 0.253 held out.",
         "Adding a one-line baseline, replay whatever this action did last time, showed it beats the template "
         "learner outright on development data. Nobody made us run that comparison. The registry did."),
        ("8 Sep 2026", "Programs that survive replay become primitives, and the library transfers.",
         "A library of concrete programs halved performance (0.204 to 0.105). Making programs abstract made them "
         "transferable and too general to be selective (0.087). Both reverted, both published. Abstraction is "
         "necessary for transfer and insufficient for selectivity. That is what the funded work is for."),
        ("9 Sep 2026", "The free end of the curve can carry an agent's routine steps.",
         "Two percent of them, and only with a completeness gate does any learner get its commits right more than "
         "half the time. Published the day it was measured."),
    ):
        s += [p(when, EYE), p(f"<i>“{was}”</i>", BODY), p(now, SMALL), Spacer(1, 4)]
    s += [PageBreak()]

    # 7. ask
    s += [p("6 / THE ASK, AND WHAT YOU KEEP IF I STOP", EYE), p("$25,000, three months, one deliverable.", H2),
          p("<b>The deliverable is the cost-capability curve with its expensive end measured rather than quoted.</b> "
            "Tycho is Apache-2.0 and costs about $119 a game to run; putting it under this protocol on 25 held-out "
            "games, two configurations, with re-runs, is about $10,000 of inference a student cannot pay for. Every "
            "other row on the curve is $0 and already published. A curve with a quoted end is an opinion."),
          table([["line", "USD", "why"],
                 ["Compute for the head-to-head", "10,000", "spent running the competitor's method, not ours"],
                 ["Researcher, 3 months, India", "10,500", "one person, full time, not a side project"],
                 ["Corpus extension and curation", "2,000", "beyond the 25 public games, human-verified labels"],
                 ["Phone-class test devices", "1,000", "a sub-Rs 10,000 Android, so on-device stays measured"],
                 ["Contingency (6%)", "1,500", "compute overruns are the likeliest surprise"],
                 ["Tranche one", "25,000", ""]],
                [150, 50, 266]),
          Spacer(1, 8),
          p("<b>Prediction on record now</b>, to be held to: over 20% of actions delegable at under $1 a game with "
            "precision above 50%, or a published reason why not. Paid on delivery either way, because paying only "
            "for wins is how funders buy quiet negative results."),
          p("<b>What you keep if I stop at any point:</b> everything published to that point is already MIT. The first "
            "milestone, the substrate, was delivered before this ask, unpaid. The remaining programme is $68,000 "
            "across three further tranches, released on delivery. It is an option you hold, not a commitment you "
            "make today."),
          p("Mapping to the programme's requests: Part Two #12 (token and economic optimisation for agents; "
            "delegation is cost routing with the routing decision measured), #11 (offline ownership over rental), "
            "#8 (portable skills without retraining). Part Three #1 (EvoSkill) is the comparison point, and that row "
            "is run.", SMALL),
          PageBreak()]

    # 8. who
    s += [p("7 / WHO IS ASKING", EYE), p("One person, and the commit log is the team.", H2),
          p("A student in India, working solo. No lab, no cofounder, no credential worth listing, so the argument is "
            "the artefact: the runtime, the substrate, the engine, 251 tests, five retractions of our own claims, "
            "and both competitor rows, all in eleven days of a public repository.", LEDE),
          p("The reason nobody has measured the cost of these systems is that everyone positioned to is a funded lab "
            "with API credits. If your compute is free at the margin, price is not a variable you notice. Mine was "
            "never free, so the runtime was instrumented for tokens and milliseconds before I knew that was the "
            "interesting part."),
          p("All of it is open: the corpus, the protocol, the runtime, the synthesiser, the phone demo, the results "
            "including the losing ones, and every prompt the competitor model was sent. The openness is "
            "load-bearing: the product claim is readability, and a closed implementation of a behaviour you can "
            "read is incoherent. If it closed tomorrow the field loses the only scoreboard where cost sits next to "
            "quality, and the person on the phone loses the one version of this where the intelligence is a file "
            "nobody can revoke."),
          Spacer(1, 10),
          table([["", ""],
                 ["Site", "let-the-dreamers-rise.github.io/nyaya"],
                 ["Repository, MIT", "github.com/let-the-dreamers-rise/nyaya"],
                 ["Belief ledger, 47 rules, switch any off", "let-the-dreamers-rise.github.io/nyaya/ledger.html"],
                 ["CI regenerating every table on every push", "github.com/let-the-dreamers-rise/nyaya/actions"],
                 ["Reproduce the held-out table", "python -m bench.run --corpus bench/corpus-heldout"],
                 ["Reproduce delegation", "python scripts/delegation.py --corpus bench/corpus-heldout --complete"],
                 ["The spec the engine is built toward", "github.com/let-the-dreamers-rise/auto-evolve"]],
                [190, 276]),
          Spacer(1, 12),
          p("Ashwin Goyal  ·  ashwingoyal2006@gmail.com  ·  India  ·  10 September 2026", SMALL)]

    doc.build(s)
    return OUT


if __name__ == "__main__":
    print(build())
