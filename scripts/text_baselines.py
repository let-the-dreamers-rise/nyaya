"""What a reviewer would run against us, run by us first.

The rule learner's headline number means nothing without the baseline every
reader already has in their head. UCI SMS is a solved dataset; multinomial
naive Bayes has been the standard answer to it for twenty years. If our
readable-rules skill loses to it, that is the honest and interesting result
-- readability has a price and the price should be printed, not implied.

Stdlib only, same 80/20 split and same seed as `nyaya learn`, so the numbers
sit next to each other legitimately.

    python scripts/text_baselines.py data/sms.tsv
"""

from __future__ import annotations

import argparse
import math
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nyaya import sms_rules as sr  # noqa: E402

WORD = re.compile(r"[a-z0-9']+")


def tokens(text):
    return WORD.findall(text.lower())


def confusion(pairs):
    """pairs of (predicted_spam, actually_spam) -> the usual four numbers."""
    tp = sum(1 for said, real in pairs if said and real)
    fp = sum(1 for said, real in pairs if said and not real)
    fn = sum(1 for said, real in pairs if not said and real)
    tn = sum(1 for said, real in pairs if not said and not real)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": (tp + tn) / max(1, len(pairs)),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }


class NaiveBayes:
    """Multinomial naive Bayes with Laplace smoothing. The textbook answer."""

    name = "naive-bayes (bag of words)"

    def fit(self, examples):
        counts = {True: Counter(), False: Counter()}
        totals = {True: 0, False: 0}
        docs = {True: 0, False: 0}
        vocab = set()
        for label, text in examples:
            spam = label == "spam"
            docs[spam] += 1
            for word in tokens(text):
                counts[spam][word] += 1
                totals[spam] += 1
                vocab.add(word)
        self.vocab = vocab
        self.counts = counts
        self.totals = totals
        n = docs[True] + docs[False]
        self.prior = {
            cls: math.log(max(docs[cls], 1) / n) for cls in (True, False)
        }
        return self

    def predict(self, text):
        size = len(self.vocab)
        best, chosen = None, False
        for cls in (True, False):
            score = self.prior[cls]
            denominator = self.totals[cls] + size
            for word in tokens(text):
                if word not in self.vocab:
                    continue
                score += math.log((self.counts[cls][word] + 1) / denominator)
            if best is None or score > best:
                best, chosen = score, cls
        return chosen


class MajorityClass:
    """The floor. Any method that does not beat this is not a method."""

    name = "majority class"

    def fit(self, examples):
        spam = sum(1 for label, _ in examples if label == "spam")
        self.always = spam * 2 > len(examples)
        return self

    def predict(self, text):
        return self.always


class KeywordList:
    """A person's first instinct: a hand-written list of scary words."""

    name = "hand-written keyword list"
    WORDS = (
        "free", "win", "winner", "won", "prize", "cash", "claim", "urgent",
        "congratulations", "txt", "text", "call now", "click", "offer",
    )

    def fit(self, examples):
        return self

    def predict(self, text):
        low = text.lower()
        return any(word in low for word in self.WORDS)


def run(path, seed=7):
    examples = sr.read_tsv(path)
    shuffled = list(examples)
    random.Random(seed).shuffle(shuffled)
    cut = int(0.8 * len(shuffled))
    train, test = shuffled[:cut], shuffled[cut:]

    rows = []

    started = time.perf_counter()
    skill = sr.learn(train)
    train_seconds = time.perf_counter() - started
    stats = sr.evaluate(skill, test)
    rows.append(("nyaya readable rules", stats, train_seconds, len(skill["rules"])))

    for cls in (NaiveBayes, KeywordList, MajorityClass):
        model = cls()
        started = time.perf_counter()
        model.fit(train)
        seconds = time.perf_counter() - started
        pairs = [(model.predict(text), label == "spam") for label, text in test]
        size = len(getattr(model, "vocab", ())) or len(getattr(cls, "WORDS", ()))
        rows.append((cls.name, confusion(pairs), seconds, size))

    print(
        "UCI SMS, {0} train / {1} held out, seed {2}\n".format(
            len(train), len(test), seed
        )
    )
    header = "{0:<28}{1:>10}{2:>9}{3:>7}{4:>10}{5:>8}{6:>10}".format(
        "method", "precision", "recall", "F1", "accuracy", "fit s", "readable"
    )
    print(header)
    print("-" * len(header))
    for name, stats, seconds, size in rows:
        readable = "{0} rules".format(size) if "rules" in name or "keyword" in name else "{0} weights".format(size)
        if name.startswith("majority"):
            readable = "1 constant"
        print(
            "{0:<28}{1:>9.1%}{2:>9.1%}{3:>7.3f}{4:>10.1%}{5:>8.2f}{6:>10}".format(
                name,
                stats["precision"],
                stats["recall"],
                stats["f1"],
                stats["accuracy"],
                seconds,
                readable,
            )
        )
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", default="data/sms.tsv")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args(argv)
    run(args.data, args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
