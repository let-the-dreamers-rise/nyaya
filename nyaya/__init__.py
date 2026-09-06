"""Nyaya: agents that compile experience into rules.

A small open runtime for sample-efficient agents on cheap hardware, and the
free end of a cost curve the field has never drawn: learning that costs zero
tokens and milliseconds of CPU, against published systems that solve the same
benchmark for roughly $119 a game.

Two learners live here -- one watches an agent interact, one reads labelled
text -- and they return the same thing: a `Skill`, a set of beliefs each
written as a human sentence carrying the evidence that earned it, renderable
as Python a person can open, disagree with and edit. Skills persist as source,
not weights.

Named for the Indian school of logic -- nyaya, literally "method, rule".
"""
from .skill import Rule, Skill, from_text_rules, from_world_model  # noqa: F401
from .world_model import wm_new, wm_observe, wm_predict, wm_summary  # noqa: F401
from .sms_rules import (  # noqa: F401
    learn,
    classify,
    score,
    evaluate,
    render_skill,
    load_skill,
    read_tsv,
)
