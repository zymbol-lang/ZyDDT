# SPDX-License-Identifier: AGPL-3.0-only
"""Which surfaces a case may not be judged on.

One table, matched by case id.  See exclusions.toml for why it is a table and
not a directory: the case still runs everywhere it can, and excluding zyjs from
`<\\ shell \\>` is not a reason to stop judging zytw and zyvm on it.
"""

from __future__ import annotations

import fnmatch
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .engines import ROOT


@dataclass(frozen=True)
class Rule:
    match: str
    engines: tuple[str, ...]      # empty tuple = every engine
    tag: str
    reason: str

    def covers(self, case_id: str, engine: str) -> bool:
        if self.engines and engine not in self.engines:
            return False
        return _glob(self.match, case_id)


def _glob(pattern: str, path: str) -> bool:
    """`*` stays inside a path segment, `**` crosses them — the corpus.toml rule.

    fnmatch's `*` crosses `/`, so a rule written `environment/*` would silently
    also catch `environment/db/deep.zy`.  Segment-wise matching is the whole
    difference between a rule that says what it means and one that quietly
    widens.
    """
    if "**" in pattern:
        return fnmatch.fnmatchcase(path, pattern.replace("**", "\x00")
                                   .replace("\x00", "*"))
    pseg, cseg = pattern.split("/"), path.split("/")
    if len(pseg) != len(cseg):
        return False
    return all(fnmatch.fnmatchcase(c, p) for p, c in zip(pseg, cseg))


@dataclass(frozen=True)
class Table:
    rules: tuple[Rule, ...] = ()
    used: set[str] = None  # populated as rules fire; an unused rule is dead

    def excluded(self, case_id: str, engine: str,
                 without: tuple[str, ...] = ()) -> Rule | None:
        for r in self.rules:
            if r.tag in without and not r.engines:
                continue
            if r.covers(case_id, engine):
                if self.used is not None:
                    self.used.add(f"{r.match}|{r.tag}")
                return r
        return None

    def dropped_class(self, case_id: str, without: tuple[str, ...]) -> Rule | None:
        """A whole tag dropped by `--without`, for every engine at once."""
        for r in self.rules:
            if r.tag in without and _glob(r.match, case_id):
                if self.used is not None:
                    self.used.add(f"{r.match}|{r.tag}")
                return r
        return None

    def dead_rules(self) -> list[Rule]:
        """Rules that matched nothing this run.

        `zyq audit` calls these dead rules and it is right to: a rule that
        matches no case is either a case that was deleted without its exclusion,
        or an exclusion written for a case that never existed.  Both are how an
        exclusion list stops describing anything.
        """
        if self.used is None:
            return []
        return [r for r in self.rules if f"{r.match}|{r.tag}" not in self.used]

    @property
    def tags(self) -> list[str]:
        return sorted({r.tag for r in self.rules})


def load(path: Path | None = None) -> Table:
    path = path or (ROOT / "exclusions.toml")
    if not path.exists():
        return Table((), set())
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rules = []
    for i, r in enumerate(data.get("rule", [])):
        if not r.get("reason"):
            # Not a warning. The one thing corpus.toml made non-negotiable.
            raise SystemExit(
                f"zyddt: exclusions.toml rule {i + 1} ({r.get('match')}) has no "
                f"reason. An exclusion whose reason nobody wrote down is "
                f"indistinguishable from a bug somebody hid.")
        rules.append(Rule(r["match"], tuple(r.get("engines", ())),
                          r.get("tag", "UNTAGGED"), r["reason"]))
    return Table(tuple(rules), set())
