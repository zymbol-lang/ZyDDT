# ZyDDT

**The verification layer for Zymbol: the known-knowns, held cheaply and forever.**

Zymbol has three engines — `zytw` (tree-walker), `zyvm` (register VM), `zyjs`
(browser) — plus two more lexers that nobody counted as engines until they
diverged: the playground highlighter and the VS Code grammar. ZyDDT is the one
place that grades all of them against the same questions.

It supersedes [ZyQuality](https://github.com/zymbol-lang/zyquality). Read
[`CHARTER.md`](CHARTER.md) for what changes and why, and
[`MIGRATION.md`](MIGRATION.md) for what comes across from the 661-file corpus
and what does not.

## The rule

> Every case here is either a **cell** — one point in a declared matrix,
> generated rather than written — or a **pin** — one minimal reproduction of a
> named finding, carrying the ID it came from. A file that is neither does not
> go in; one already in that becomes neither comes out.

## Where it sits

| | asks | finds | cost |
|---|---|---|---|
| **LDV** (`interpreter/LDV.md`) | can the language express this domain? | unknown-unknowns | a release |
| **ZyDDT** (here) | do all engines still answer the same, correctly? | regressions in what we already know | milliseconds |

LDV is the microscope; ZyDDT is the alarm. LDV's decalogue already says this —
point 7, *"regressions belong to a different layer"*, and point 8, *"the
knowledge has to be moved into something that costs milliseconds"*. That layer
had no name and no home. This is it.

## Status

**Design stage.** Nothing is built yet, deliberately: the point is to decide
what earns a place *before* copying anything, not to fork 661 files and sort
them afterwards.
