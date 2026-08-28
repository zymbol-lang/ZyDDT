# SPDX-License-Identifier: AGPL-3.0-only
"""Printing.  Colour only when a terminal is attached — unlike the CLI under
test, which writes colour into a pipe and ignores NO_COLOR (measured
2026-08-27, and the reason engines.toml has to strip it back out)."""

from __future__ import annotations

import os
import sys

_TTY = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code: str, s: str) -> str:
    return f"\x1b[{code}m{s}\x1b[0m" if _TTY else s


def green(s): return _c("32", s)
def red(s): return _c("31", s)
def yellow(s): return _c("33", s)
def dim(s): return _c("2", s)
def bold(s): return _c("1", s)


VERDICT_COLOUR = {
    "ok": green,
    "warn": yellow,
    "error/static": red,
    "error/runtime": red,
    "BLOCKED": lambda s: bold(red(s)),
}


def verdict(v: str) -> str:
    return VERDICT_COLOUR.get(v, str)(v)
