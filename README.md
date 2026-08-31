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
point 7, *"regressions belong to a different layer first"*, and point 8, *"the
knowledge has to be moved into something that costs milliseconds"*. That layer
had no name and no home. This is it.

*First*, not *only*: the LDV applications stay in a gate of their own after
their release (`zyquality/project`, and `ZyFmtCheck`'s default body). They are a
second alarm — slower, and it tells you a program broke rather than which rule
did. ZyDDT is the one that names the rule.

## Status

**The runner exists; the corpus does not.** That order is deliberate — the point
was to decide what earns a place *before* copying anything, not to fork 661 files
and sort them afterwards. What runs today is the machinery for asking, eight
declared axes — three of them crossed matrices — and five pins. Not one file has
been copied over from ZyQuality yet, and the axes have produced ten findings the
661-file corpus could not see. **All ten are closed.**

```bash
./bin/zyddt suite                  # the whole layer, one verdict — 394 cells, ~30 s
./bin/zyddt surfaces               # the two lexers: what did they leave unmarked
./bin/zyddt selftest               # grade the runner itself
./bin/zyddt engines                # what can run, and what cannot
./bin/zyddt gen                    # write every cell from axes/*.toml
./bin/zyddt axis                   # generate, run, publish the denominator
./bin/zyddt --detail N axis        # how many reds quote their output (default 8)
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
| `oracle` — **independent answer** | is what they agree on *right*? | anywhere another language can decide it — and only where **both sides compute, by the same route**. `zytw` and `zyvm` share the whole front end and `zyjs` was ported from them, so a wrong answer they all inherited is a green row |
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
axis                 cells  agree  oracled  narrowed  wording  diverge  wrong
arithmetic               6      6        4         0        0        0      0
diagnostic               7      7        0         0        0        0      0
environment              3      3        0         3        0        0      0
integer-arithmetic      36     36       36         0        0        0      0
numerals                69     69       69         0        0        0      0
operator               252    252        0         0        0        0      0
refusal                 13     12        0         0        1        0      0
type-symbol             48     48        0         0        0        0      0
verdict-shape            5      5        0         0        0        0      0
pins                    11     11        —         0        —        0      —
surfaces                 2      2        —         0        —        0      —
selftest                50     50        —         —        —        —      —
```

`surfaces` is the two lexers CHARTER § 4 declares and this layer did not grade:
the playground's highlighter and the VS Code grammar. They never run a program,
so they have no verdict to classify — they are asked what they left unmarked,
over the same cells and pins the engines answer. Both are clean; both were not
on the first run.

`oracled` is the honest count of cells where agreement is not the only evidence:
**109 of 439**. `integer-arithmetic` exists to raise it where it was lowest —
`operator` crosses the same six operators and asks only whether the three
engines agreed, which is a weak question about a front end two of them share.
Its oracle was verified by breaking it: flooring instead of truncating reports
`WRONG ANSWER` on exactly the two mixed-sign pairs, which is what the operand
pairs were chosen to separate.
`narrowed` is agreement with a surface excused by a rule — `[2/3]` in the report,
and it matters most for this pair: with `zyjs` excused, only `zytw` and `zyvm`
remain, and they share the lexer, the parser and the semantic analyser, so the
whole front-end question goes unasked.

Nine axes and nine pins is not coverage either, and the table is written this
way so it cannot be mistaken for any. An axis nobody has declared has no row
here, and that absence is worth more than a green tick on a suite that never
asked ([`CHARTER.md`](CHARTER.md) § 6). Of the 394 cells, 321 are green by
agreement and nothing else: if one of those hides an error all three engines
share, this layer cannot see it today.

`numerals` and `type-symbol` are the first two axes generated from a **crossed
matrix** rather than written point by point, and `numerals` is what the shape was
for: `zyquality/corpus/i18n/numerals/` is 69 files that differ only in which
digit block they substitute, and this is the same 69 as one declaration plus one
template — with an oracle each, which the corpus's goldens could not have, since
a golden records what the engines said and cannot disagree with them.

### What the first crossing of `operator` found, and what it cost to close

14 operators × 18 type pairs is 252 questions nobody had asked, and **150 of them
were red on the first run** (2026-08-29). That was not 150 findings: it was
**six**, each printed once per cell it touched. All six are closed, along with
the three older ones and one that the closing turned up.

| finding | cells | what | closed |
|---|---:|---|---|
| [`ZYVM-001`](HALLAZGOS/zyvm.md) | 40 | the VM **ran what the tree-walker refuses** — `7 && 3` printed `#1`, `"ab" / "cd"` printed `[ab]` | 2026-08-30 |
| [`ZYJS-004`](HALLAZGOS/zyjs.md) | 70 | the browser engine wrote a runtime **warning to stdout**, into the program's own output | 2026-08-30 |
| [`ZYJS-006`](HALLAZGOS/zyjs.md) | 54 | `[object Object]` and `undefined` inside a diagnostic, and a dictionary called `Tuple` | 2026-08-30 |
| [`ZYJS-005`](HALLAZGOS/zyjs.md) | 34 | `&&`/`\|\|` on non-booleans: no warning, no refusal, an answer | 2026-08-30 |
| [`GLOBAL-001`](HALLAZGOS/GLOBAL.md) | 28 | the same impossible comparison refused in three different wordings | 2026-08-30 |
| [`ZYVM-002`](HALLAZGOS/zyvm.md) | 10 | the diagnostic for `-` quoted the guidance for `+` | 2026-08-30 |
| [`ZYJS-001`](HALLAZGOS/zyjs.md) | 1 | `parsePrimary` swallowed **any** token it did not recognise and returned Unit | 2026-08-30 |
| [`ZYJS-002`](HALLAZGOS/zyjs.md) | 2 | lexer diagnostics carried no line, and folded their guidance into the message | 2026-08-30 |
| [`ZYJS-003`](HALLAZGOS/zyjs.md) | 5 | a JavaScript `RangeError` reached the user as `error: Invalid code point NaN` | 2026-08-30 |

Three decisions unblocked them, and all three are the author's: **`&&` on
non-booleans is an error** (the v0.0.9 loop-specifier rule — *there is no
truthiness* — applied to another operator); **tuples do not order**; and **a
diagnostic names types, not values**, which is the only wording all three engines
can always produce and which closes `ZYJS-006` by construction.

### What closing them found that no ficha had

This is the part worth reading, because none of it came from a review:

- **The VM's short-circuit still decided by truthiness.** The matrix crosses
  `&&` with *truthy* left operands, so every cell reached the `And` instruction
  and went green once that instruction required Bools — while `0 && #1` still
  answered `#0`, having jumped before it. The jump cannot check for itself
  (`? 7 { … }` compiles to the same one and is a warning there), so the guard is
  its own instruction, `RequireBool`.
- **`zyjs` got chained output right by accident.** `>> a >> b ¶` is two
  statements, and the browser engine had no such rule: the second `>>` fell into
  `parsePrimary`'s catch-all, came back as Unit, and Unit prints as nothing.
  Removing the catch-all put **18 corpus files red at once** and forced the rule
  to be implemented rather than simulated. The ficha had warned this could
  happen; it happened.
- **`zyjs`'s unary operators checked nothing.** `-"a"` answered `NaN`, `!7`
  answered `#0`. A pin found it by *running*, the first time the question was
  asked of all three engines at once — unary minus is not in a matrix of binary
  operators.

The forms that had no cell now have one. The five sibling faces of `ZYJS-001`
and the four sibling base prefixes of `ZYJS-003` are cells of their own axes, in
the same commit as the fix: a root cause with six symptoms and one cell is a
cause that comes back through any of the other five.

`wording.baseline` carries **one** entry, written on purpose and with its reason
attached: the Rust engines add `= help: expected signature: g(Number, Number)`
to an arity refusal, with the parameter types they INFERRED, and `zyjs` has no
parameter inference to build that with. Reproducing it means building one, which
is a design decision and not a message fix. What was fixed in the same commit is
that `zyjs` had no line on that diagnostic at all.

### What only the LDV applications found

394 green cells, a 661-file corpus and 222 examples did not see either of these.
A real program did — which is [`LDV.md`](../interpreter/LDV.md) § 1 in two lines.

- [`ZYJS-007`](HALLAZGOS/zyjs.md), **closed**: zyjs continued an identifier on
  ASCII digits where the Rust lexer uses `is_alphanumeric()`. Chaturanga is
  written in Sanskrit and names variables `कार्यस्थितिः२`; the file ran here on a
  wrong parse, correctly under both Rust engines, and `ZYJS-001`'s catch-all was
  what hid it. No corpus file names a variable that way.
- [`GLB-001`](HALLAZGOS/GLOBAL.md), **closed**: filed first as `ZYJS-008` by
  reading the symptom — zyjs refuses what both Rust engines accept — and the
  reading was backwards. zyjs was right: the Rust semantic analyser **did not
  descend into the operand of a `$` operator**, so nothing written there was
  checked at all. Fixing it surfaced four calls in Chaturanga's own suite
  missing their `<~` mark, and all four sat inside a `$#`. A blind spot does not
  leave errors at random; it leaves them in its own shape.
- [`ZYJS-009`](HALLAZGOS/zyjs.md), **closed**: `alias::f()` inside a module
  resolved against the **caller's** alias table — dynamic scoping. It needs two
  different modules to share an alias name, which no corpus file does. With it
  fixed, Chaturanga's whole suite passes under `zyjs` too, for the first time,
  and so do GO's and serpiente's.
- [`ZYJS-010`](HALLAZGOS/zyjs.md), **closed**: a module's function ran in the
  caller's scope, so the caller's variables shadowed the module's own functions
  and a sibling's write to module state was invisible. `klingon_galaxy` names an
  array after the function that produces it; `ZyBank`'s locale dispatcher builds
  its catalogue in one function and reads it in another. Both are ordinary.
- [`ZYJS-011`](HALLAZGOS/zyjs.md) and [`GLB-002`](HALLAZGOS/GLOBAL.md),
  **closed**: `s = °s "x"` — the string accumulator the guide documents —
  returned only the `°s` and dropped the rest of the juxtaposition; and with `s`
  undeclared the three engines answered three different things, because the
  neutral value belongs to the OPERATOR and all three knew that only on the
  assignment path.
- [`GLB-003`](HALLAZGOS/GLOBAL.md), **open**: two loops reusing an iterator name
  warn once in Rust and twice in the browser. Nobody has decided which is right,
  so nothing asserts it.

All three say the same thing about the denominator: `zyquality/project/apps.toml`
excludes `zyjs` from the application suites **on purpose** — they are
command-line programs — so nothing grades that crossing. Checking it here meant
diffing `zyjs` against its own previous version, file by file, which was the
only instrument available.

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
