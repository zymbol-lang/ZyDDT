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

**The runner exists; the corpus does not.** That order is deliberate — the point
was to decide what earns a place *before* copying anything, not to fork 661 files
and sort them afterwards. What runs today is the machinery for asking, plus the
first two axes and the first pin.

```bash
./bin/zyddt suite                  # the whole layer, one verdict
./bin/zyddt selftest               # grade the runner itself
./bin/zyddt engines                # what can run, and what cannot
./bin/zyddt gen                    # write every cell from axes/*.toml
./bin/zyddt axis                   # generate, run, publish the denominator
./bin/zyddt ask FILE...            # CELL: every engine must answer alike
./bin/zyddt check FILE...          # PIN: compare against the recorded .observed
./bin/zyddt observe FILE           # what each engine said, verbatim
```

Exit codes are the contract every other repository's wrapper already honours:
**0** green, **1** red, **2** no verdict — an engine did not answer, so nothing
may be called a pass. When a run produces both, red wins: exit 2 tells a CI the
harness could not run, and saying that when the harness ran fine and the code
diverged points the reader at the wrong thing.

[`VERDICTS.md`](VERDICTS.md) is the definition of what `ok`, `warn` and `error`
mean, how they are recognised, and what makes two engines' answers the same
answer. Read it before adding a case; it is where the surprises are — the exit
code is not the verdict, a wording difference is not a red, and agreeing is not
the same as being right.

### Four questions, four mechanisms

Each answers something the one above it cannot.

| | asks | when it is the right form |
|---|---|---|
| `ask` — **differential** | did every engine answer alike? | always, wherever it can decide. It encodes no belief about the right answer, so it cannot encode a wrong one ([`CHARTER.md`](CHARTER.md) § 8.2) |
| `expect` — **category** | did each engine reach the required category? | a malformed program, or any cell named for what it produces. Checked per engine on every outcome, so a divergence **names** the engine that is out of compliance rather than only reporting that they differ |
| `oracle` — **independent answer** | is what they agree on *right*? | anywhere another language can decide it. `zytw` and `zyvm` share the whole front end and `zyjs` was ported from them, so a wrong answer they all inherited is a green row |
| `check` — **golden** | is one engine still doing exactly this? | when the differential cannot decide. Recorded from a run and reviewed as a diff, never typed from what somebody expects |

And one mechanism for what cannot be asked at all: [`exclusions.toml`](exclusions.toml),
one table with a mandatory `reason`, never a separate directory —
[`VERDICTS.md`](VERDICTS.md) § 9 has why.

Findings are written in Spanish, in [`HALLAZGOS/`](HALLAZGOS/INDICE.md), one file
per engine plus one for what has no single culprit. The runner names the engine
that is out of compliance and prints the file the finding belongs in, so the
routing comes out of the run rather than out of a reading.

### Where it stands, measured

```text
axis             cells  agree  oracled  narrowed  wording  diverge  wrong
arithmetic           4      4        4         0        0        0      0
environment          3      3        0         3        0        0      0
refusal              3      0        0         0        2        1      0
verdict-shape        5      4        0         0        1        0      0
pins                 1      1        —         0        —        0      —
selftest            41     41        —         —        —        —      —
```

`oracled` is the honest count of cells where agreement is not the only evidence.
`narrowed` is agreement with a surface excused by a rule — `[2/3]` in the report,
and it matters most for this pair: with `zyjs` excused, only `zytw` and `zyvm`
remain, and they share the lexer, the parser and the semantic analyser, so the
whole front-end question goes unasked.

Four axes and one pin is not coverage, and the table is written this way so it
cannot be mistaken for any. An axis nobody has declared has no row here, and that
absence is worth more than a green tick on a suite that never asked
([`CHARTER.md`](CHARTER.md) § 6).

The one red is real and was found by the first run of the first axis:
[`ZYJS-001`](HALLAZGOS/zyjs.md). `x = =` is refused by `zytw` and `zyvm` and
**accepted** by `zyjs`, which runs it to completion with only an unused-variable
warning. Tracing it found the cause, and it is wider than the cell:
`parsePrimary` in `zymbol.js` ends by consuming **any** token it does not
recognise and returning a Unit literal, so six different malformed programs are
accepted where both Rust engines refuse them.

It is the same family as `DM-06` — closed on 2026-08-18 by narrowing `zyjs`'s
`parseOutput` from `parseExpr` to `parseAdditive` — and that fix could not have
reached this: narrowing decides which grammar is invoked, and the swallow is
underneath it, at the bottom of `parsePrimary`.

As a cell it needed no ID, which is exactly why the axis form finds what the
finding-by-finding form waits for.

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
