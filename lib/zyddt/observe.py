# SPDX-License-Identifier: AGPL-3.0-only
"""What an engine said, normalised, and what it means.

Three verdicts, plus the absence of one:

    ok            ran to completion, said nothing
    warn          ran to completion, said something that was not fatal
    error         did not complete — `static` if it was refused before running,
                  `runtime` if it started and died
    BLOCKED       no answer was obtained at all

BLOCKED is deliberately not a verdict.  It is what ZyQuality's governance calls
the one thing a gate may never do: read "nothing ran" as "nothing failed".  It
is never a pass and never an agreement.

The exit code is recorded and is NOT what decides the verdict.  Measured
2026-08-27 on all three engines: a top-level `<~ 3` makes a perfectly healthy
program exit 3 (GAP-ZYB-006).  Exit status is a thing the program may choose, so
classifying on it would call a working program an error and — worse — call a
program that chose `<~ 0` after a diagnostic a success.  The verdict comes from
what the engine said on stderr; the exit code travels beside it as data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .engines import Normalise, RawRun

# ── The shapes on stderr, all measured 2026-08-27 ─────────────────────────────
#
#   error: undefined variable 'noexiste'          ← head, both Rust and zyjs
#     --> /abs/path.zy:2:4                        ← Rust location
#     --> line 2                                  ← zyjs location
#      2 | >> noexiste ¶                          ← Rust source excerpt
#        |    ^^^^^^^^                            ← Rust caret
#     = help: variables must be defined before use
#   Runtime error: division by zero               ← all three, identical prefix
#   Error: failed to read file: /abs/path.zy      ← the CLI failing to start

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
HEAD = re.compile(r"^(error|warning|note)\s*:\s*(.*)$")
LOC_FULL = re.compile(r"^\s*-->\s*(?P<path>.*?):(?P<line>\d+):(?P<col>\d+)\s*$")
LOC_LINE = re.compile(r"^\s*-->\s*line\s+(?P<line>\d+)\s*$")
HELP = re.compile(r"^\s*=\s*help\s*:\s*(.*)$")
EXCERPT = re.compile(r"^\s*(?:\d+\s*)?\|")
RUNTIME = re.compile(r"^Runtime error\s*:\s*(.*)$")
HARNESS = re.compile(r"^Error\s*:\s*(.*)$")  # capital E: the CLI, not a diagnostic


@dataclass(frozen=True)
class Diag:
    severity: str            # error | warning | note
    line: int | None
    col: int | None          # recorded always, compared only under --strict-column
    head: str
    body: tuple[str, ...] = ()
    help: str | None = None

    def key(self, compare_column: bool) -> tuple:
        return (self.severity, self.line,
                self.col if compare_column else None,
                self.head, self.body, self.help)

    def render(self) -> list[str]:
        at = f" @{self.line}" if self.line is not None else ""
        col = f":{self.col}" if self.col is not None else ""
        out = [f"{self.severity}{at}{col}  {self.head}"]
        out += [f"    {b}" for b in self.body]
        if self.help:
            out.append(f"    help: {self.help}")
        return out


@dataclass(frozen=True)
class Observation:
    engine: str
    phase: str
    status: str              # ok | warn | error | BLOCKED | EXCLUDED
    kind: str | None         # for error: static | runtime
    exit: int
    out: str
    diags: tuple[Diag, ...] = ()
    blocked: str | None = None
    leftover: tuple[str, ...] = ()   # stderr lines nothing claimed — see NOTE
    excluded: object | None = None   # the exclusions.toml Rule that applied

    @property
    def verdict(self) -> str:
        return f"{self.status}/{self.kind}" if self.kind else self.status

    # ── Two keys, because there are two kinds of difference ──────────────────
    #
    # The first version of this had one key, and every diagnostic the engines
    # word differently came out RED.  On the first run that was three of eight
    # cells, and two of the three were the same fact stated twice: zytw emits
    # `= help: variables must be defined before use` and zyjs does not.  The
    # engines agree completely about the program — they refuse it, at the same
    # line, before running it — and disagree only about how much they say.
    #
    # Grading those the same colour is how a real divergence gets lost.  The
    # split is the distinction ZyQuality's `messages/` already draws: what the
    # engines DO is a gate, what they SAY is an inventory with a baseline that
    # may fall and may not rise.

    def shape_key(self, compare_column: bool) -> tuple:
        """What the engines DID.  A difference here is a regression.

        `exit` is in it: two engines that print the same thing and leave with
        different statuses have not answered the same question, and a shell
        downstream acts on the difference.  `blocked` is in it so BLOCKED never
        equals anything — including another BLOCKED, because two engines that
        both failed to run have not agreed about the language.
        """
        if self.status in ("BLOCKED", "EXCLUDED"):
            return (self.status, self.engine, self.blocked)
        return (self.verdict, self.exit, self.out,
                tuple((d.severity, d.line, d.col if compare_column else None)
                      for d in self.diags),
                self.leftover)

    def wording_key(self) -> tuple:
        """What the engines SAID.  A difference here is inventory, not a red.

        Only meaningful between observations whose shape_key already matches:
        on its own it would call two engines that refuse and accept the same
        program "a wording difference".
        """
        return tuple((d.head, d.body, d.help) for d in self.diags)


def _strip(text: str, norm: Normalise) -> str:
    return ANSI.sub("", text) if norm.strip_ansi else text


def parse_stderr(text: str, norm: Normalise) -> tuple[list[Diag], list[str], str | None]:
    """→ (diagnostics, unclaimed lines, runtime-fault message or None).

    NOTE on `unclaimed`.  Anything on stderr that no rule recognised is kept and
    compared verbatim, never dropped.  A parser that silently discards what it
    does not understand is how a whole class of message stops being graded — the
    exact failure `zyquality/messages/` was written to catch after a scanner bug
    swallowed Rust source for months.
    """
    diags: list[Diag] = []
    unclaimed: list[str] = []
    fault: str | None = None

    sev = line = col = head = None
    body: list[str] = []
    helptext: str | None = None

    def flush():
        nonlocal sev, line, col, head, body, helptext
        if sev is not None:
            diags.append(Diag(sev, line, col, head, tuple(body), helptext))
        sev = line = col = head = None
        body, helptext = [], None

    for raw in text.splitlines():
        if not raw.strip():
            continue

        if m := RUNTIME.match(raw):
            flush()
            fault = m.group(1).strip()
            continue

        if m := HEAD.match(raw):
            flush()
            sev, head = m.group(1), m.group(2).strip()
            continue

        if m := LOC_FULL.match(raw):
            # The path is machine-dependent and is dropped by keep_location.
            if sev is not None:
                line, col = int(m.group("line")), int(m.group("col"))
            continue

        if m := LOC_LINE.match(raw):
            if sev is not None:
                line = int(m.group("line"))
            continue

        if m := HELP.match(raw):
            if sev is not None:
                helptext = m.group(1).strip()
            else:
                unclaimed.append(raw.strip())
            continue

        if norm.drop_source_excerpt and EXCERPT.match(raw):
            continue

        if m := HARNESS.match(raw):
            flush()
            unclaimed.append(f"harness: {m.group(1).strip()}")
            continue

        if sev is not None:
            body.append(raw.strip())          # a continuation of the message
        else:
            unclaimed.append(raw.strip())

    flush()
    return diags, unclaimed, fault


def classify(run: RawRun, norm: Normalise) -> Observation:
    if run.blocked:
        return Observation(run.engine, run.phase, "BLOCKED", None,
                           run.exit, "", (), run.blocked)

    diags, unclaimed, fault = parse_stderr(_strip(run.stderr, norm), norm)
    out = _strip(run.stdout, norm) if norm.strip_ansi else run.stdout

    # Stderr belongs to the ENGINE, not to the program (REFERENCE.md L37: what
    # the program prints goes to stdout, what the engine says about it goes to
    # stderr).  So text on stderr that no rule recognised, with no diagnostic
    # beside it, means the engine failed in a way this layer does not model —
    # and a verdict read off it would be a guess.
    #
    # Found the hard way: `zyddt ask` on a path that did not exist classified
    # `Error: failed to read file: …` as **ok**, because no rule matched and the
    # exit code is deliberately not the classifier.  A missing file reading as a
    # pass is the exact failure the whole layer is built against.
    if unclaimed and not diags and fault is None:
        return Observation(run.engine, run.phase, "BLOCKED", None, run.exit, out,
                           (), f"unrecognised on stderr: {unclaimed[0]}",
                           tuple(unclaimed))

    # The order is the severity order, and it is the whole classifier.
    if fault is not None:
        # The program started: whatever it printed before dying is real output
        # and stays in the record.  `Runtime error:` is the one prefix all three
        # engines share verbatim, which is why the distinction is observable at
        # all rather than a guess from the exit code.
        diags = (*diags, Diag("error", None, None, fault))
        status, kind = "error", "runtime"
    elif any(d.severity == "error" for d in diags):
        status, kind = "error", "static"
    elif any(d.severity == "warning" for d in diags):
        status, kind = "warn", None
    else:
        status, kind = "ok", None

    return Observation(run.engine, run.phase, status, kind, run.exit, out,
                       tuple(diags), None, tuple(unclaimed))


# ── The record on disk ───────────────────────────────────────────────────────
# Line-oriented and diffable on purpose.  CHARTER § 8.2: an assertion is
# *recorded from a run and reviewed as a diff*, never written by hand from what
# somebody expects — a golden typed from belief encodes the belief.

def render(obs: Observation) -> str:
    lines = [f"status  {obs.verdict}"]
    if obs.status == "EXCLUDED":
        lines.append(f"reason  {obs.excluded.tag}: {obs.excluded.reason}")
        return "\n".join(lines) + "\n"
    if obs.status == "BLOCKED":
        lines.append(f"reason  {obs.blocked}")
        return "\n".join(lines) + "\n"
    lines.append(f"exit    {obs.exit}")
    lines.append("--- out")
    lines += obs.out.splitlines()
    if obs.diags:
        lines.append("--- diag")
        for d in obs.diags:
            lines += d.render()
    if obs.leftover:
        lines.append("--- unclaimed")
        lines += list(obs.leftover)
    return "\n".join(lines) + "\n"
