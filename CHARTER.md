# ZyDDT — the charter

> **What this document is.** The founding decision: why the verification layer is
> being rebuilt rather than extended, what earns a place in it, and what the old
> one got right that must survive the move.
>
> **What it is not.** Not the migration plan — [`MIGRATION.md`](MIGRATION.md) is
> that. Not the validation method — `interpreter/LDV.md` is that, and this
> document is the layer LDV's decalogue points 7 and 8 ask for by name.
>
> **Method.** Every claim of a defect below is one that was actually found and
> is named. Nothing here is a hypothetical failure mode.

---

## Table of contents

1. [The two layers](#1-the-two-layers)
2. [Why ZyQuality is superseded](#2-why-zyquality-is-superseded)
3. [The admission rule](#3-the-admission-rule)
4. [The five surfaces](#4-the-five-surfaces)
5. [What survives the move unchanged](#5-what-survives-the-move-unchanged)
6. [The denominator](#6-the-denominator)
7. [What a verdict means](#7-what-a-verdict-means)

---

## 1. The two layers

`interpreter/LDV.md` § 2 sets Language-Driven Validation against TDD and gets the
distinction right: LDV's unit under test is the language, its test is a whole
application, its cycle is a release, and what it finds is **unknown-unknowns** —
the case nobody could think of until a real domain forced it.

Its decalogue then says, twice, where the findings must go:

> **7 — Regressions belong to a different layer.** Each finding is distilled into
> a minimal, fast, automated case […] The application is never the regression
> test; it is where the regression test came from.
>
> **8 — […] Once one is found, the knowledge has to be moved into something that
> costs milliseconds, or it will be lost the next time somebody refactors the
> thing that caused it.

That layer has existed as a pile of files and a runner. It has never had a
charter, an admission rule, or a way to answer *what is not covered*. ZyDDT is
that layer, named and given one.

The relationship is a loop, and both halves are load-bearing:

```text
      LDV                                        ZyDDT
  ┌─────────────────────┐                 ┌──────────────────────┐
  │ build an application│  a finding,     │ one minimal case,    │
  │ in a domain the     │  with an ID  →  │ pinned by that ID,   │
  │ language has never  │                 │ run by every engine  │
  │ been asked to serve │                 │ on every commit      │
  └─────────────────────┘                 └──────────┬───────────┘
            ▲                                        │
            │        the axes a finding revealed     │
            └────────  become a declared matrix  ◄───┘
                       covered exhaustively
```

The upward arrow is the part that is new. When ZyBank found that `#?`'s count
answers 0 for four different values, that is not one test — it is an **axis**:
every type × the question `#?` asks. Recording the one case that bit is what the
old layer did. Declaring the axis and covering it is what stops the other three
from biting later.

---

## 2. Why ZyQuality is superseded

ZyQuality is not being discarded for being bad. It solved the problem it was
built for — four engines, four private test sets, no common verdict — and its
central rule is carried over verbatim (§ 5). It is superseded because of what it
structurally *cannot* see, and because that blind spot is now measured.

### 2.1 The gate only sees programs that finish and print

`zyq consensus` compares engine output; `zyq expect` compares against a golden.
Both need a program that **runs to completion and produces stdout**. Everything
else is invisible to them:

| invisible to the gate | measured |
|---|---|
| the text of a runtime error | 804 messages one engine defines and another does not, on the *shared* surface alone |
| a diagnostic: a warning emitted, or wrongly not emitted | `zyjs` warned `ambiguous lifetime` on **121** of 222 example programs; the CLI warned on **0** |
| a code path no corpus file reaches | the register VM has **two** interpreters; the second — the one that runs a called function's body — diverged from the first in three separate ways |

Each row above is a defect class that was found by hand in a single session, in
2026-08. None was found by the gate, and the gate was green throughout.

### 2.2 Organised by provenance, not by coverage

The corpus is 661 files in 65 directories. The largest are named for **where the
test came from**, not for what it covers: `gaps/` (34), `bugs/` (34),
`v0.0.4_review/` (28), `smoke/` (22). A directory named for its origin can be
added to forever and never answers the only question that matters:

> **What is not covered?**

A hand-written corpus cannot answer it at any size, because it is a *sample*.
Growing it does not help — it makes the number bigger and the answer no clearer.
That is the fear behind *"do not add hundreds of thousands of repetitive tests"*,
and it is correct: size is not the metric, and a suite that cannot name its gaps
is not made trustworthy by being large.

`i18n/numerals/` (69 files, one per script) is the counter-example already in the
tree, and the shape ZyDDT generalises: it is exhaustive over a **declared axis**,
so its coverage is a fact rather than a hope. It should be *generated* from that
axis instead of hand-written 69 times, but the principle is right.

### 2.3 The instruments that could see the rest were outside the gate

`zyquality/messages/` — an exhaustive inventory of every message all engines
define — was written, documented, and **not registered in `suites.toml`**. It had
rotted to the point of not running at all outside one directory, and it carried a
scanner bug that swallowed Rust source (`'"'`, a char literal, read as the start
of a string). It was wired into the gate on 2026-08-26 and immediately reported
804 one-sided messages on the shared surface.

`zyquality/coverage/` — what code no test has ever executed — is outside the gate
**correctly**, and stays outside: it needs a separate instrumented build, takes
minutes, and leaves `target/debug` instrumented. Its output is a list to read,
not a verdict. ZyDDT keeps that judgement.

The pattern is the one ZyQuality's own `GOVERNANCE.md` warns about — *a gate must
not read "nothing ran" as "nothing failed"* — applied one level up: a measurement
outside the gate is a measurement nobody runs.

---

## 3. The admission rule

> **Every case in ZyDDT is either a CELL or a PIN.**
>
> A **cell** is one point in a declared matrix. It is *generated* from the axes,
> never hand-written, so the matrix's coverage is a property of the declaration
> rather than of anyone's memory.
>
> A **pin** is one minimal reproduction of a named finding — an LDV gap log
> entry, a divergence, a bug — and it carries that identifier. A pin with no ID
> is a file nobody can explain.
>
> A case that is neither does not go in. A case already in that becomes neither
> comes out.

### 3.1 Why this answers the size question

The rule makes size a **consequence** rather than a decision:

- A cell cannot be redundant with another cell — they are distinct points of a
  matrix, by construction. If two cells are the same test, the axes are wrong,
  and that is a bug in the declaration, fixable in one place.
- A pin cannot be redundant with another pin — each names a different finding.
  Two pins with the same ID is a duplicate, and it is mechanically detectable.
- Therefore *"hundreds of thousands of repetitive tests"* is not a risk that has
  to be resisted by discipline. It is unreachable: there is no way to add a file
  that is neither a cell of some axis nor a pin of some finding.

### 3.2 What a matrix looks like

An axis is declared, not discovered. Example, drawn from real divergences:

```toml
[[axis]]
id     = "type-symbol"
what   = "`#?` names every value's type, in every engine"
values = ["###", "##.", "##\"", "##'", "##?", "##]", "##[", "##)", "##(", "##_", "##!"]
engines = ["zytw", "zyvm", "zyjs"]
# 11 values × 3 engines = 33 cells, generated.
# The cell (##!, zyvm) is where `##!` was answered instead of `##Index`.
# The cell (##!, zyjs) is where `##_` was.
```

The point is not the 33 cells. It is that after declaring the axis, *"is the
error value covered?"* stops being a question anybody has to remember to ask.

### 3.3 Where the axes come from

Three sources, in descending order of how much they are worth:

1. **An LDV finding that turned out to be a family.** The most valuable, because
   a real domain proved the axis exists. `#?`'s count answering 0 for `Unit`,
   `""`, `[]` and `#()` came from ZyBank's `es_nulo`; the axis is *every value ×
   every question `#?` answers*.
2. **A place where two engines disagree.** A divergence is evidence that the
   axis was never covered — if it had been, it would have failed on the day it
   was introduced.
3. **A reading of the language's own definition.** `SYMBOLS.md`'s operator table
   and `REFERENCE.md` § 21 are axes already written down in prose. Crossing them
   with the type table is mechanical, and it is the cheapest coverage there is.

---

## 4. The five surfaces

ZyQuality graded engines. 2026-08 established that the engines are not the whole
product a user touches, and that the other surfaces diverge the same way:

| # | surface | what it is | how it diverged |
|---|---|---|---|
| 1 | `zytw` | tree-walker, the diagnostics bench | bound `Unit` silently for a dictionary pattern with an absent key |
| 2 | `zyvm` | register VM, the future default | **two** interpreters; the second answered `Unit` for an absent key and built `#?`'s tuple in the wrong order |
| 3 | `zyjs` | browser engine | over-reported one diagnostic on 121 files, under-reported another on 4 |
| 4 | `highlight.js` | the playground's highlighter **and its hover index** | left `#(`, `#[`, non-Latin booleans and every native-digit number unmarked — 328 `#` unmarked across the corpus |
| 5 | `zymbol.tmGrammar.json` | the VS Code grammar | same three gaps independently, plus `0xFF` split into `0` and an identifier |

Surfaces 4 and 5 are lexers. They are not optional prettiness: a token the
highlighter does not know is a token the reader **cannot ask about**, because the
same file is the hover index. They belong in the same gate as the engines, graded
by the same axes.

The audit method that found their gaps is mechanical and belongs in ZyDDT as a
suite, not as a one-off:

- For the highlighter: every character emitted **outside a span** came out of the
  one unmarked path. Strip the markup, look at what is left.
- For the grammar: tokenise with `vscode-textmate` over Oniguruma — the real
  machinery, not a regex approximation — and flag any operator that lands in the
  bare `source.zymbol` scope.

---

## 5. What survives the move unchanged

Carried over verbatim, because each was learned the expensive way:

**One corpus, all engines, one verdict.** From `GOVERNANCE.md`:

> A change to any engine is validated against \[the shared layer]. A suite that
> grades an engine against files it owns itself is not a gate — it is that
> engine's opinion of itself.

**A gate must not read "nothing ran" as "nothing failed".** Wrappers exit **2**
when the layer is absent, never 0.

**An exclusion requires a reason.** `corpus.toml` replaced five incompatible skip
mechanisms with one table where every entry says *why*. An exclusion without a
reason is indistinguishable from a bug somebody hid. This becomes stricter in
ZyDDT: a skipped **cell** must name the axis value it is skipping and why, so a
hole in a matrix is visible as a hole.

**Baselines that only go down.** `bench` and `messages` record a number; the gate
fails when it rises and reports when it falls. Regenerating is deliberate and
separate.

**Each repository keeps its own wrapper**, with its name, flags and exit codes.
They delegate; they do not reimplement.

---

## 6. The denominator

The complaint that started this — *"we fix one disparity and three more appear"* —
has a precise cause and it is not that the disparities multiply. Measured on
2026-08-26: the gate was green before and after, and the corpus gained zero
divergences. What rose was the **rate of discovery**, because the engines were
finally being probed instead of waited on.

It felt like chaos because there was no denominator. Without a number for *how
many places two engines could disagree*, every find looks like the front of an
infinite queue.

ZyDDT's first obligation is therefore to publish that number, per axis, and to
make it monotonic:

```text
axis                          cells   covered   divergent
type-symbol (`#?`)               33        33           0
dot on every type                33        33           0
edit family × collection        180         0         ?     ← undeclared
message inventory (shared)      804       804          804
```

A row with `?` is the honest answer for an axis nobody has declared yet, and it
is worth more than a green tick on a suite that never asked.

---

## 7. What a verdict means

One command, one verdict, as before. What changes is what it is allowed to be
green about:

- **Green** means every declared cell agrees across every surface it applies to,
  every pin still reproduces its finding as fixed, and no baseline rose.
- **Green does not mean correct.** It means nothing regressed in what has been
  declared. The undeclared axes are named in the report with their `?`, so the
  verdict never implies coverage it does not have.
- A **red** is a regression, not noise. As of 2026-08-26 the old gate reached
  fully green for the first time, which is the precondition for this to be true —
  a permanently-red gate is one nobody reads.

---

## Related documents

| Document | Answers |
|---|---|
| `interpreter/LDV.md` | The validation method, and the decalogue this layer discharges |
| [`MIGRATION.md`](MIGRATION.md) | What crosses over from the 661-file corpus, and what does not |
| `zyquality/GOVERNANCE.md` | The layer being superseded — its rule is § 5 here |
| `interpreter/SYMBOLS.md` § 17 | The operator table: an axis already written in prose |
| `interpreter/REFERENCE.md` § 21 | The symbol reference: the other half of that axis |
