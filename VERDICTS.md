# What a verdict is

> **What this document is.** The definition of the three answers an engine can
> give about a program, how each is recognised, and what makes two engines'
> answers the same answer.
>
> **Method.** Every rule below was measured on `zymbol 0.0.9` across `zytw`,
> `zyvm` and `zyjs` on 2026-08-27. Where a measurement contradicted the obvious
> design, the measurement is quoted and the design changed. Nothing here is a
> rule somebody thought sounded right.

---

## 1. The three verdicts, and the thing that is not one

| verdict | the program | stderr | `zyddt` prints |
|---|---|---|---|
| `ok` | ran to completion | silent | `AGREE … ok` |
| `warn` | ran to completion | ≥1 `warning:`, no `error:` | `AGREE … warn` |
| `error/static` | was refused; nothing executed | ≥1 `error:` | `AGREE … error/static` |
| `error/runtime` | started, printed, then died | `Runtime error: …` | `AGREE … error/runtime` |
| **`BLOCKED`** | **was never asked** | — | `NO VERDICT`, exit 2 |

`BLOCKED` is deliberately not a verdict. It is what happens when the binary is
absent, the harness times out, or the engine has no entry point for the phase
being asked. It is never a pass and it never equals another `BLOCKED`: two
engines that both failed to run have not agreed about the language. This is
ZyQuality's governance rule — *a gate must not read "nothing ran" as "nothing
failed"* — carried over as a value in the type rather than as a habit.

### A warning is not a soft failure

`warn` means the program **ran and printed**, and the engine had something to say
about it anyway. The recorded observation carries both:

```
status  warn
exit    0
--- out
hola
--- diag
warning @4:1  unused variable 'sin_usar'
    help: consider removing this variable or prefixing with '_' if intentionally unused
```

The output is graded exactly as it would be for `ok`. A change that keeps the
output and drops the warning is a change, and it shows up here — which is the
whole point, because that is the class the old gate could not see at all. In
2026-08 `zyjs` warned `ambiguous lifetime` on **121** of 222 example programs and
the CLI warned on **0**, and the gate was green throughout.

### 1.1 Stderr belongs to the engine, so unreadable stderr is not a pass

`REFERENCE.md` L37 settled the streams: what the program prints goes to stdout,
what the engine has to say *about* the program goes to stderr. A Zymbol program
has no way to write to stderr itself — `<\ shell \>` captures its child's.

So text on stderr that no rule recognised, with no diagnostic beside it, means
the engine failed in a way this layer does not model, and any verdict read off it
is a guess. That is `BLOCKED`.

The rule was not written from theory. `zyddt ask` on a path that did not exist
classified

```text
Error: failed to read file: /…/nope.zy
```

as **ok** — no rule matched, and the exit code is deliberately not the classifier
(§ 2). A missing file reading as a pass is the exact failure the whole layer is
built against, and it survived in the runner for about twenty minutes.

---

## 2. Why the exit code does not decide

The obvious design is to read the exit status: 0 is fine, non-zero is not. It is
wrong here, and the counter-example is in the corpus as
`verdict-shape/exit-is-not-a-verdict`:

```zymbol
>> "adios" ¶
<~ 3
```

Measured on all three engines: prints `adios`, exits **3**. A top-level `<~ n` is
the program's exit status (GAP-ZYB-006), so the exit code is a value the
*program* chooses. Classifying on it would call that healthy program a failure —
and, worse, would call a program that ends `<~ 0` after a fatal diagnostic a
success.

So **the verdict is read from stderr, and the exit code travels beside it as
data.** It is still compared: two engines that print the same text and leave with
different statuses have not answered the same question, and the shell downstream
will act on the difference.

---

## 3. What is normalised away, and why

Each rule below is in `engines.toml` under `[normalise]`, with the measurement
that forced it. A normalisation with no reason is indistinguishable from a
difference somebody hid.

| stripped | because |
|---|---|
| ANSI colour | the Rust CLI writes colour **into a pipe** and does not honour `NO_COLOR`. Without stripping, `zytw` and `zyjs` differ on every diagnostic ever emitted |
| the source excerpt and caret | `zytw`/`zyvm` render the offending line and a `^^^` under it; `zyjs` renders neither. Same fact, drawn twice |
| the path in `-->` | `zytw` says `/abs/path.zy:2:4`, `zyjs` says `line 2`. The path is machine-dependent — it leaked a scratchpad path in the first probe ever run |
| **not** the column | recorded in every observation, excluded from the default comparison because `zyjs` cannot produce one at all. Comparing it would report a fixed, unfixable difference on every diagnostic and drown the real ones. Declared in `engines.toml` so the hole is visible as a hole; `--strict-column` turns it on |
| **nothing else** | anything on stderr no rule recognised is kept in an `--- unclaimed` section and compared verbatim, and if it is the **only** thing on stderr the observation is `BLOCKED`. A parser that silently drops what it does not understand is how a whole class of message stops being graded — and see § 1.1 for what that rule caught on the day it was written |

---

## 4. Two engines agree when they did the same thing

The first version of the comparator had one key, and every diagnostic the engines
word differently came out **red**. On the first run that was three of eight cells,
and two of the three were the same fact stated twice: `zytw` emits
`= help: variables must be defined before use` and `zyjs` does not. The engines
agree completely about the program — they refuse it, at the same line, before
running it — and disagree only about how much they say.

Grading those the same colour is how a real divergence gets lost. So there are
two keys:

**Shape — what the engines *did*. A difference here is a regression.**
The verdict, the exit code, the program's output, and each diagnostic's severity
and line.

**Wording — what the engines *said*. A difference here is inventory.**
Each diagnostic's message text and its `help:`. Compared only between
observations whose shape already matches; on its own it would call two engines
that refuse and accept the same program "a wording difference".

Wording splits are held in `wording.baseline`, as a **list and not a count** — a
count that stays at 3 while one split closes and another opens is a green gate
over a regression. It may fall on its own and may never rise on its own:

```bash
zyddt axis                     # a new split is RED
zyddt axis --regen-baseline    # deliberate, separate, and a reviewable diff
```

This is `zyquality/messages/` applied to what is actually emitted at runtime,
where that suite counts what is *defined* in the source. The two are
complementary: a message no test reaches is invisible here and visible there.

---

## 5. The outcomes of asking

`zyddt ask` and `zyddt axis` both end in exactly one of these. Only the first two
are a pass.

| outcome | meaning | exit |
|---|---|---|
| `AGREE` | same shape, same words | 0 |
| `WORDING` | same shape, different words, already in the baseline | 0 |
| `NEW WORDING` | same shape, different words, **not** in the baseline | 1 |
| `DIVERGE` | different shape — the engines did different things | 1 |
| `WRONG` | they agreed, and the axis says the category is wrong | 1 |
| `WRONG` | at least one engine did not reach the category the cell requires — and it is **named** (§ 11) | 1 |
| `WRONG ANSWER` | they agreed, and an independent implementation says the answer is wrong (§ 8) | 1 |
| `PARTIAL` | the answering engines agreed; not all of them answered | 2 |
| `NO VERDICT` | fewer than two engines answered. An agreement of one is not an agreement | 2 |
| `DEAD RULE` | an exclusion matched no case, so the list has stopped describing anything | 2 |

Exit codes are the contract every other repository's wrapper already honours:
**0** green, **1** red, **2** no verdict.

When a run produces both, **red wins**: a run that diverged *and* failed to judge
something exits 1, not 2. Exit 2 tells a CI "the harness could not run", and
saying that when the harness ran fine and the code diverged points the reader at
the wrong thing. A plain `max()` over the raw codes had this backwards, and
`verdict/red-beats-no-verdict` in the selftest holds it down.

---

## 6. Asserting, and when it is allowed

`zyddt ask` asserts nothing. It requires the engines to answer alike, which
encodes no belief about the right answer and therefore cannot encode a wrong one
(`CHARTER.md` § 8.2). Prefer it wherever it can decide.

It cannot decide two things, and each has its own form:

**A program all three engines wrongly accept.** A consensus run cannot see it —
three engines that agree wrongly agree perfectly. This is what `axes/refusal.toml`
is for: it declares `expect = "error"`, the weakest claim that still bites
(*whatever the message, this must not run*), and `zyddt axis` reports `WRONG`
when they all accept it.

**One engine's behaviour, held still.** `zyddt check` compares against a recorded
`.observed` file, one per engine, because the engines legitimately differ in what
they *can* say. The golden is recorded from a run and reviewed as a diff, never
typed from what somebody expects — a golden written by hand encodes the belief it
was supposed to catch:

```bash
zyddt check --regen cases/pin/X.zy    # record
git diff cases/pin/                    # the review IS the diff
zyddt check cases/pin/X.zy             # from then on, it must hold
```

---

## 7. Adding a case

There are exactly two ways, and the admission rule (`CHARTER.md` § 3) allows no
third. Neither of them is "write another test".

**A cell** — one point of a declared matrix. Add a value to an axis in `axes/`;
`zyddt gen` writes it and every sibling. The file under `generated/` is not
committed and must not be edited: `generated/` is in `.gitignore` precisely so
the declaration stays the truth.

Usually this means **adding a row to a dimension**, and the sibling cells come
with it. Every script in `axes/numerals.toml` is one line of this shape:

```toml
  { id = "adlam", name = "Adlam", base = "1E950", zero = "𞥐", nine = "𞥙" },
```

The day the lexer's `DIGIT_BLOCKS` grows a seventieth entry, that is the whole
change here: one more line produces a cell, a Python oracle computed from the
block base alone, and a row in the denominator. The template it crosses is the
one the other 69 already answer, so the new script is asked exactly what they
are asked — which is the property a hand-written seventieth file could not have,
and the reason the corpus's 69 could drift from each other and did.

Writing the point out is the other form, for when the point carries an essay:

```toml
[[cell]]
id   = "some-value"
what = "what this point of the axis is"
src  = """
>> 1 + 1 ¶
"""
```

Both produce the same `Cell`. `CHARTER.md` § 3.2 has the full matrix syntax and
the three properties the generator has to guarantee.

**A pin** — one minimal reproduction of a named finding, in `cases/pin/`, named
for the ID it carries. A pin with no ID is a file nobody can explain, and the
header says what it protects and what it deliberately does not:

> Named-tuple equality is DM-22 and was deliberately NOT fixed. It is not
> asserted here — a pin that quietly covers an open finding reports it as closed.

A skipped cell names the axis value it is skipping and why — `skip = "reason"`
on a written cell, `[[matrix.skip]]` with a `when` and a mandatory `reason` on a
matrix — so a hole in a matrix is visible **as a hole** rather than as a smaller
matrix. The report prints the coordinates it skipped, not just the count.

Two things a cell may add, and both change what its green means:

- an **oracle** (§ 8), which turns "they agreed" into "they agreed and it is
  right". Add one wherever an independent implementation can decide the answer;
  the `oracled` column is the honest count of cells where agreement is not the
  only evidence.
- an entry in `exclusions.toml` (§ 9), when a surface cannot be asked at all.
  Never a new directory, always a rule with a `reason`.

---

## 8. Agreement is not correctness — the oracle

Everything up to here decides whether the engines answered *alike*. None of it
can tell whether the answer is *right*, and the gap is not academic: `zytw` and
`zyvm` share the lexer, the parser and the semantic analyser, so they can only
disagree about execution, and `zyjs` was hand-ported from them. A wrong answer
all three inherited is a perfectly green row. It is the hazard `CHARTER.md` § 8.2
names for a test written by whoever wrote the engine, one level up.

So a cell may declare an **oracle**: the same computation in another language,
whose answer was authored outside Zymbol entirely.

```toml
[[cell]]
id   = "product"
src  = '''
>> 6 * 7 ¶
'''
oracle.py = '''
print(6 * 7)
'''
```

The engines must agree with each other **and** with it. `WRONG ANSWER` is the one
thing a differential can never say. The oracle runs only after the engines agree —
running it against engines that disagree would answer a question nobody asked
("which of them is right") when the finding is that they differ at all.

`engines.toml` declares the oracles (`py`, `js`), carried over from ZyQuality
where the idea was already right and had no consumer. An oracle is never the
thing under test, and is never cited for anything it does not itself decide:
CPython is the authority on integer arithmetic and says nothing about how Zymbol
formats a dictionary. A cell that wants that wants a golden.

### The two ways an oracle goes wrong

**One: it does not check anything.** The `i53-boundary` cell shipped like this,
and it is worth looking at before writing another one:

```toml
src       = '>> 9007199254740991 ¶'    # a LITERAL, typed knowing the answer
oracle.py = 'print(2**53 - 1)'         # a COMPUTATION
```

The two sides do not do the same thing. Zymbol prints back a constant chosen to
match what Python computes, so the "check" confirms only that the same number was
typed twice — and it would have stayed green through any change to how Zymbol
computes anything at all.

> **An oracle is a check only when both sides compute, by the same route.**

That is mechanically testable for the exact fraud above: does the oracle's answer
appear verbatim in the Zymbol source? If it does, the answer was written into the
program the oracle is supposed to be deciding. `zyddt axis` reports it as
`SUGGESTIVE` and gives no verdict for that cell.

It is a heuristic and says so — `>> 1000 + 0 ¶` legitimately contains its own
answer — so it warns rather than fails, it does not apply below four characters
(`42` is in half of all arithmetic), and `oracle_literal_ok = "reason"` silences
it, with a reason, like every other exclusion here.

The route matters as much as the expression. The boundary cell now reads
`(2 ^ 52) + (2 ^ 52 - 1)` on both sides, because `2 ^ 53 - 1` cannot be used at
all — see below.

**Two: it asserts *another* language's answer about this one.** Both mismatches
on the first run of `axes/arithmetic.toml` were the oracle's fault, not the
engines':

| cell | Zymbol | naive Python oracle |
|---|---|---|
| `7 / 2` | `3` | `3.5` |
| `-7 % 3` | `-1` | `2` |

Neither engine was wrong. Zymbol's `/` between Ints truncates toward zero like C
and Go (`DI-06`), and `%` follows that same division; Python 3 floors and offers
`//` separately. The oracles are now `math.trunc` and `math.fmod`, with the rule
they encode written beside them.

An oracle that needs a comment saying **which** rule it encodes is an oracle
earning its place: the language had made that decision and nothing executable
recorded it.

### Where an oracle cannot exist at all

`>> 2 ^ 53 - 1 ¶` is `Runtime error: integer overflow: 2 ^ 53` in all three
engines. `print(2**53 - 1)` is `9007199254740991`. **Neither is wrong.**

`^` binds tighter than `-`, so the intermediate is 9007199254740992 — outside
±(2^53−1) — and a fail-closed model must refuse it even though the subtraction
would have brought the result back into range. Python has no boundary to cross.

So the two languages do not share a number model at that point, which is the
whole reason the cell exists, and an oracle there would be asserting Python's
answer about Zymbol. The cell carries `expect = "error"` and no oracle, and the
absence is written into it as the finding. `expect` is the strongest claim that
is actually true of both: *whatever the message, this must not produce a number.*

A cell that cannot have an oracle should say so where the next reader will look.
An oracle quietly omitted is indistinguishable from one nobody got round to.

---

## 9. What a browser cannot be asked — exclusions

Some cases cannot be judged on every surface. `<\ shell \>` has no browser
equivalent; `std/db` is ODBC; raw-mode key input needs a real terminal.

**They are not moved somewhere else.** `exclusions.toml` is one table, matched
against the case id; the case stays where it belongs and runs everywhere it can.
Moving the file would stop `zytw` and `zyvm` being judged on it too — and
`corpus.toml` was written to undo exactly that. ZyQuality had **four** exclusion
lists (a `@vm-skip` marker, a `VM_COMPARE_EXCLUDE` regex, a 40-entry `SKIP_SET`
literal inside `test_runner.mjs`, and a `grep -L lib_time`), none of which could
see the others, so a file excluded from the JavaScript comparison because it
shelled out was still counted as a divergence by another engine.

```toml
[[rule]]
match   = "environment/shell-*"
engines = ["zyjs"]      # omit for every engine: "not a function of the program"
tag     = "BASH_EXEC"   # drop the whole class with --without BASH_EXEC
reason  = "`<\ shell \>` has no browser equivalent"     # REQUIRED
```

`reason` is not optional and not a warning: loading a rule without one is a hard
exit. An exclusion nobody explained is indistinguishable from a bug somebody hid.

Three consequences the report makes visible:

**An excluded engine is never invoked** — not run-and-discard. `<\ shell \>` in
`zyjs` does not fail, it *answers*: `case 'BashExec'` in `zymbol.js` is a stub
that returns `Date.now() * 1e6 + random()`. A discarded answer is one refactor
away from being read.

**A narrowed agreement is marked `[2/3]`** and counted in its own column. It
matters most for exactly this pair: with `zyjs` excused, only `zytw` and `zyvm`
remain, and they share the whole front end — so the parser and semantic questions
go unasked and the row is weaker than its colour suggests.

**A rule that matched no case is a `DEAD RULE`** and puts the run at exit 2. Two
were written into the first draft of `exclusions.toml` straight from ZyQuality's
list, and both were dead on the first run because ZyDDT has no `TUI` or `std/db`
cell yet. They were deleted rather than kept "for later": their wording sits in a
comment, and they come back in the same commit as the cell that needs them, which
is the only commit in which they can be verified.

### Choosing the case matters more than writing the rule

The first `environment` cell was `<\ "echo hola" \>`, and all three engines
answered `hola` — which made the exclusion look unnecessary. The stub
special-cases `date` formats and `echo`; the cell had landed on the one command
it happens to get right.

That is worse than an engine that cannot do a thing: it is an engine that answers
anyway. The cells are now `wc -l` through a pipe, `expr`, and an `echo` with
`$(( ))` in it — chosen so the stub cannot coincide with the real answer.

---

## 10. How the runner knows it is running right

A layer that judges three engines has to be judged itself. ZyQuality learned it
the expensive way: the two harness defects found while producing its first
consensus numbers — a reversed argv and a missing module resolver — both
**inflated the divergence count**, and neither was visible in the output. A
broken runner does not announce itself. It announces the engines.

```console
$ zyddt selftest
  cold  29/29 ok   classifier, parser, comparator, globs, config
  cmd    6/6  ok   every subcommand survives being called
  live   3/3  ok   every engine runs the seed and answers it right
```

**Cold** needs no engine, deliberately: if it did, a broken engine would look like
a broken runner, and the test would be useless exactly when it matters. Every
stderr fixture in it is real output captured from `zymbol 0.0.9` and
`run_one.mjs`, pasted verbatim including the ANSI escapes the Rust CLI writes
into a pipe — a fixture typed from memory grades the memory. Each case states its
answer in a sentence, so a reader can check it by eye:

```python
@case("classify/exit-is-not-the-classifier",
      "`<~ 3` leaves a healthy program at exit 3; it is still ok")
```

**Cmd** runs every subcommand and asks only whether it survives being called. It
exists because of a hole in the cold part. A slice-and-splice edit to `bin/zyddt`
deleted `_observe_all`; `zyddt axis` died with a `NameError` — and
`zyddt selftest` still reported **28/28** — every cold case there was at the
time — because every cold case imports the
`zyddt` package and none of them touches the command layer. A grader that passes
while its own front end is broken is the exact failure it exists to catch, one
level in.

**Live** is separate and named, because it is the part that can fail for a reason
that is not the runner's fault.

`zyddt suite` runs the selftest **first** and stops there if the cold or cmd parts
fail:
every number below it is produced by the thing that just proved it grades wrong.

### It was verified by breaking the runner

A selftest that has never failed is a selftest nobody has tested. Two defects
were injected on purpose, and the cases caught them:

| injected defect | caught by |
|---|---|
| classify on the exit code | 1 cold case — `classify/exit-is-not-the-classifier` |
| stop stripping ANSI | 6 cold cases, across the parser and the comparator |
| delete a name a command body uses | 4 of 6 `cmd` runs; every cold case stayed green |

The third row is the one worth reading twice. It is the defect that actually
happened, it left every cold case green, and it is why there are three parts
rather than two.


---

## 11. Naming which engine is wrong

`DIVERGE` is a fact about a **pair**: they differ. It does not say who is wrong,
so it routes nowhere — and a finding that routes nowhere does not get filed.

A cell (or its axis) may declare `expect`: the category every engine must reach.
It is checked **per engine, on every outcome, `DIVERGE` included**:

```text
WRONG       refusal/assign-no-rhs  an assignment whose right-hand side is missing
    zytw               error/static           cumple   expect=error
    zyvm               error/static           cumple   expect=error
    zyjs               warn                   INCUMPLE expect=error
    → HALLAZGOS/zyjs.md
```

That last line is the routing, and it comes out of the run rather than out of a
reading. `HALLAZGOS/INDICE.md` has the rule and the file layout.

This was wrong at first in a way worth recording: the check ran *after* the
engines agreed, so the one case where naming a culprit matters most — they
disagree and one of them is out of compliance — reported `DIVERGE` and stopped.

### It is not the same claim as an oracle

They answer different questions, and the difference is what each can be trusted
with:

| | asserts | who authored the answer |
|---|---|---|
| `expect` | the **category**: error, warn, ok | us. It is a claim, and a weak one on purpose — *whatever the message, this must not run* |
| `oracle` | the **value**: this exact output | another language entirely (§ 8) |

`expect` is the right form where an oracle cannot exist. `x = =` is not a Python
program, so no independent implementation can say what it should print — but any
implementation of *this* language must refuse it, and that is checkable without
agreeing on a single character of the message.

### A cell named for a category should assert it

`axes/verdict.toml` declared no `expect` at first, on the grounds that a pure
differential encodes no belief and so cannot encode a wrong one (`CHARTER.md`
§ 8.2). That reasoning is right in general and was wrong there, because those
cells are **named** for the category they produce. `error-static` asserts
something in its own identity; without an `expect` the assertion is decorative,
and if all three engines started answering `warn` the differential would stay
green while the axis silently stopped testing the thing it is called.

A claim already made in a cell's name should be made where the runner can read
it.

### What it cannot see

Every engine reaching the required category and still disagreeing about *how* —
three different error messages, say — is still a `DIVERGE`, and it routes to
`HALLAZGOS/GLOBAL.md` rather than to any one engine's file. The report says so
on the line.
