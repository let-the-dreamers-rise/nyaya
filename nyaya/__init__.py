"""Nyaya: agents that compile experience into rules.

A small open runtime for sample-efficient agents on cheap hardware. A local
language model proposes goals; learned symbolic world-models verify, plan and
execute. Skills persist as plain, inspectable Python instead of weights.

Named for the Indian school of logic -- nyaya, literally "method, rule".
"""
from .world_model import wm_new, wm_observe, wm_predict, wm_summary  # noqa: F401
