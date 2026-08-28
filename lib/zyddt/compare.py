# SPDX-License-Identifier: AGPL-3.0-only
"""Deciding whether a set of observations is an agreement.

Five outcomes.  Only one of them is a pass.

    AGREE       every engine that may be judged did the same thing and said
                the same words
    WORDING     every engine did the same thing; the words differ.  Counted
                against a baseline that may fall and may not rise — it is the
                message inventory, not a regression
    DIVERGE     the engines did different things.  Red
    PARTIAL     the answering engines agreed, but not all of them answered
    NO_VERDICT  fewer than two engines answered.  An agreement of one is not an
                agreement

An EXCLUDED engine is none of those.  It is a declared, reasoned absence
(exclusions.toml) rather than a failure to answer, so it does not make a run
PARTIAL — but it is counted and printed, because a green row over a two-engine
agreement is not the same fact as one over three.

That distinction has teeth for exactly one pair: `zytw` and `zyvm` share the
lexer, the parser and the semantic analyser, so they can only disagree about
EXECUTION.  When zyjs is excluded, the whole front-end question goes unasked and
the row is weaker than its colour suggests.  `coverage` on the Consensus says
how many of the declared engines actually answered, so the report can say so.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .observe import Observation

AGREE, WORDING, DIVERGE, PARTIAL, NO_VERDICT = (
    "AGREE", "WORDING", "DIVERGE", "PARTIAL", "NO_VERDICT")


@dataclass(frozen=True)
class Consensus:
    outcome: str
    answered: list[Observation] = field(default_factory=list)
    blocked: list[Observation] = field(default_factory=list)
    shape_groups: list[list[Observation]] = field(default_factory=list)
    wording_groups: list[list[Observation]] = field(default_factory=list)
    excluded: list[Observation] = field(default_factory=list)
    declared: int = 0

    @property
    def is_pass(self) -> bool:
        return self.outcome == AGREE

    @property
    def verdict(self) -> str | None:
        return self.answered[0].verdict if self.answered else None

    @property
    def coverage(self) -> str:
        """`3/3`, or `2/3` when a rule excused an engine. Printed on every row
        that is not full, so a narrowed question never looks like a whole one."""
        return f"{len(self.answered)}/{self.declared}"

    @property
    def full(self) -> bool:
        return len(self.answered) == self.declared


# Outcomes in which every answering engine produced the SAME stdout — they share
# one `shape_key`, and stdout is part of it.  An oracle may be run against any of
# them, and must be: the oracle sat after the WORDING branch at first, so a cell
# whose engines split only on the wording of a diagnostic silently stopped having
# its answer verified at all.  A known, baselined wording split would have
# switched off the correctness check underneath it.
#
# DIVERGE and NO_VERDICT are excluded deliberately.  There is no single answer to
# check, and an oracle run there answers a question nobody asked — "which of them
# is right" — when the finding is that they differ at all.
SHAPE_AGREED = (AGREE, WORDING, PARTIAL)


def oracle_applies(outcome: str) -> bool:
    return outcome in SHAPE_AGREED


def _group(obs: list[Observation], keyfn) -> list[list[Observation]]:
    buckets: dict = {}
    for o in obs:
        buckets.setdefault(keyfn(o), []).append(o)
    return list(buckets.values())


def consensus(obs: list[Observation], compare_column: bool = False) -> Consensus:
    excluded = [o for o in obs if o.status == "EXCLUDED"]
    blocked = [o for o in obs if o.status == "BLOCKED"]
    answered = [o for o in obs if o.status not in ("BLOCKED", "EXCLUDED")]
    n = len(obs)

    def make(outcome, *rest):
        return Consensus(outcome, answered, blocked, *rest,
                         excluded=excluded, declared=n)

    if len(answered) < 2:
        return make(NO_VERDICT)

    shape = _group(answered, lambda o: o.shape_key(compare_column))
    if len(shape) > 1:
        return make(DIVERGE, shape)

    # Same shape. Now, and only now, is a text difference a wording difference.
    words = _group(answered, lambda o: o.wording_key())
    if len(words) > 1:
        return make(WORDING, shape, words)
    if blocked:
        return make(PARTIAL, shape, words)
    return make(AGREE, shape, words)


# ── Combining outcomes ───────────────────────────────────────────────────────
GREEN, RED, NOVERDICT = 0, 1, 2

# Severity order, which is NOT the numeric order of the exit codes.  A run that
# both found a divergence and failed to judge something exits 1, not 2: exit 2
# tells a CI "the harness could not run", and reporting that when the harness
# ran fine and the code diverged points the reader at the wrong thing entirely.
# A plain `max()` over the raw codes had it backwards.
_RANK = {GREEN: 0, NOVERDICT: 1, RED: 2}


def worse(a: int, b: int) -> int:
    return a if _RANK[a] >= _RANK[b] else b


def offenders(obs: list[Observation], expect: str) -> list[Observation]:
    """Which engines failed to reach the category the axis requires.

    Evaluated PER ENGINE and on every outcome, DIVERGE included.  It used to run
    only after the engines agreed, so the one case where naming a culprit matters
    most — they disagree, and one of them is out of compliance — reported
    "DIVERGE" and stopped there.  "They differ" is a fact about a pair; "zyjs
    answered `warn` where the axis requires `error`" is a fact about an engine,
    and only the second one routes to a findings file.

    BLOCKED and EXCLUDED are never offenders: neither of them answered.
    """
    return [o for o in obs
            if o.status not in ("BLOCKED", "EXCLUDED") and o.status != expect]
