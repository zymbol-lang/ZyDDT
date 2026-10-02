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
