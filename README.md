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

## Authorship & AI collaboration

Zymbol is designed by
**[OscarE.EspinozaB](https://github.com/zymbol-lang/interpreter/commits?author=OscarEEspinozaB)**.
Every decision about the language and about what this layer grades originates
from and is controlled by its author. ZyDDT, like the interpreter and like the
LDV applications, is built with **[Claude Code](https://claude.ai/code)**
(Anthropic) as the engineering team, under the author's direction. The use of AI
is transparent and intentional — it is not concealed or minimized.

What AI does not replace: the design rationale, the specification that guides
each feature, the judgment on what earns a place here and what does not, and the
final say on every merged change. See [`CHARTER.md`](CHARTER.md) § 8 for why
that distinction is load-bearing *for a test layer specifically*.
