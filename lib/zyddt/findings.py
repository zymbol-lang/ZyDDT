# SPDX-License-Identifier: AGPL-3.0-only
"""Reading the state of a ficha from its own **Estado** line.

The index of HALLAZGOS/ is computed, not kept: two hand-kept indexes rotted
(the table atop GLOBAL.md stopped at GLB-007; INDICE.md § 0 counted 2026-08-30),
and six fichas went on saying «abierto» weeks after their last part was fixed.
"""

from __future__ import annotations

import re

ESTADO = re.compile(r"^\*\*Estado:?\*\*:?\s*(.*)$", re.M)

# The first words of an Estado line, in the forms the fichas actually use.
# INDICE.md § 6 declares «abierto | corregido AAAA-MM-DD | desestimado»; the
# fichas also write «cerrado», «decidido y corregido», «implementado» and
# «reencaminado», and an index that read only the declared three printed 18
# fichas as unreadable.
_STARTS = (("abierto", "open"), ("decidido y corregid", "closed"),
           ("corregid", "closed"), ("cerrad", "closed"), ("implementad", "closed"),
           ("desestimad", "dismissed"), ("rechazad", "dismissed"),
           ("reencaminad", "rerouted"))


def state_of(estado: str) -> str:
    """→ open | closed | dismissed | rerouted | other, from an Estado line."""
    s = estado.lower().lstrip("* ")
    for word, state in _STARTS:
        if s.startswith(word):
            return state
    return "other"


# ── the hand-kept summary above the fichas ───────────────────────────────────
#
# Each engine's file opens with a table of its fichas and a sentence counting
# the open ones. Nothing read them, and on 2026-10-10 they named seven fichas
# «abierto» that had been closed for up to four weeks — the same rot that
# retired the table of GLOBAL.md, in the three files that kept theirs. They are
# allowed to be INCOMPLETE (a row nobody added says nothing false); what they
# may not do is contradict the ficha they point at.

HEAD = re.compile(r"^##\s+([A-Z]{2,6}-\d+)\s+—", re.M)
_ROW = re.compile(r"^\|\s*(?:~~)?\[?`([A-Z]{2,6}-\d+)`[^|]*\|([^|]*)\|")
# «abiertos: `X-1`», and as the headers write it: in bold, «**Uno abierto:**
# `ZYVM-022`», or with a comma, «**Uno abierto, `ZYTW-016`**». The bold form
# let a header name a fixed finding as open for a day (2026-10-19).
_SAID_OPEN = re.compile(r"abiert[oa]s?\**\s*[:,]\s*\**\s*((?:`[A-Z]{2,6}-\d+`(?:\s*,\s*|\s+y\s+)?)+)")
_ID = re.compile(r"`([A-Z]{2,6}-\d+)`")


def stale_summary(text: str, states: dict[str, str]) -> list[tuple[int, str, str, str]]:
    """→ [(line, id, summary says, ficha says)] for every row or «abiertos: …»
    sentence above the first ficha of `text` that disagrees with `states`."""
    first = HEAD.search(text)
    out = []
    for n, line in enumerate(text[: first.start() if first else len(text)].splitlines(), 1):
        claims = []
        row = _ROW.match(line)
        if row:
            claims.append((row.group(1), state_of(row.group(2).strip())))
        for m in _SAID_OPEN.finditer(line):
            claims += [(fid, "open") for fid in _ID.findall(m.group(1))]
        for fid, said in claims:
            real = states.get(fid, "other")
            if "other" not in (said, real) and said != real:
                out.append((n, fid, said, real))
    return out
