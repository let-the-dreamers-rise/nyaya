"""A shared evaluation substrate for world-model learners.

Every programmatic world-model system published so far is evaluated on its own
setup, with its own protocol, against its own baseline -- so the field cannot
answer a simple question: for a given interaction budget, which learner
predicts best, and where does each break?

This package is the attempt to make that question answerable: a compact
corpus of real recorded transitions, one causal-replay protocol, and a
registry any method can enter.
"""
