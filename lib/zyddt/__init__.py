# SPDX-License-Identifier: AGPL-3.0-only
"""ZyDDT — the verification layer for Zymbol.

The runner is deliberately small and in Python: it has no build step, `tomllib`
is in the standard library, and every instrument this layer inherits from
ZyQuality that was worth inheriting (`messages/extract.py`,
`docs/guide_verify.py`) is already Python.  The compiled OCaml runner ZyQuality
grew is what a corpus of 661 hand-written files needs; a layer whose cases are
generated needs a generator more than it needs a fast comparator.
"""
