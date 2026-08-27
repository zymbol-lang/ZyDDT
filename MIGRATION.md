# Migration — what crosses over, and what does not

> **What this document is.** The triage procedure for ZyQuality's 661 corpus
> files against ZyDDT's admission rule, and the measurements that justify not
> copying them wholesale.
>
> **What it is not.** Not the result. No file has been triaged yet. This defines
> *how*, so the work is mechanical when it starts and so nobody has to decide the
> same question twice.

---

## 1. Why not just copy it

Because the admission rule ([`CHARTER.md`](CHARTER.md) § 3) would immediately
reject most of it, and copying first means sorting 661 files while the gate is
already depending on them.

Measured on the corpus as of 2026-08-26:

| | files | share |
|---|---:|---:|
| total `.zy` | 661 | |
| with a `.expected` golden | 659 | 99.7% |
| **citing a finding ID** (`HLZ-…`, `BUG-Z…`, `GAP-Z…`, `DM-…`) | **77** | 11.6% |
| citing a `REFERENCE.md` L-number | 13 | 2.0% |
| **with no header comment at all** | **78** | 11.8% |
| in directories named for their *provenance* — `gaps/`, `bugs/`, `v0.0.4_review/`, `smoke/` | 118 | 17.9% |

The two bold rows are the migration in miniature. Only **77 files can currently
say which finding they exist to protect**, which is the definition of a pin. And
**78 files carry no explanation of any kind** — for those, nobody alive can say
what breaking them would mean.

That is not an argument that the other 500 are worthless. It is an argument that
their value is *unrecorded*, and unrecorded value cannot survive a move.

---

## 2. The triage

Each file gets exactly one verdict. The verdicts are ordered: take the first that
applies.

### PIN — it protects a named finding

It cites, or can be traced to, a finding ID from an LDV gap log, a divergence
record, or a `REFERENCE.md` L-entry.

**Action.** Move it. Attach the ID in the header if it is only implicit. Reduce
to the minimum that still fails when the fix is reverted — a pin that also
exercises four unrelated features is a pin that will be edited for the wrong
reason later.

**Expected volume.** ~90 files have an ID today. More will qualify once the
eight gap logs are read against the corpus, which is the one part of this
migration that is genuinely archaeological.

### CELL — it is one point of a matrix

It is one case of something enumerable: a numeral script, a type symbol, an
operator against a value kind, a stdlib function's arity.

**Action.** Do **not** move the file. Declare the axis; the generator produces
that cell along with every sibling the corpus never had. `i18n/numerals/` is 69
files that are one axis declaration, and declaring it covers the scripts nobody
wrote a file for.

**Expected volume.** The largest group, and the one where the file count *drops*
while coverage *rises*. This is the whole reason not to copy.

### SEED — it is a real program worth running, but proves nothing specific

Application-shaped: `smoke/`, the tour programs, the GUIDE examples. They catch
integration failures no single cell would.

**Action.** Move a **small, named** set — enough that a broken build fails
loudly, not enough that anybody mistakes them for coverage. They are pinned by
the fact of running at all, and their goldens are the assertion.

**Expected volume.** Tens, not hundreds. If the seed set needs to be big to feel
safe, the matrices are underdeclared and that is where the work belongs.

### DROP — it is none of the above

No ID, no axis, no integration value. Usually a file written to check a fix
during one session and never explained.

**Action.** Do not move it. Record the path and the reason in
`dropped.tsv` — *dropped*, not deleted: ZyQuality's history remains, and a
dropped file that later turns out to matter is one `git log` away.

⚠ **A file is never dropped for being old, or for passing.** It is dropped for
being unexplainable. If reading it reveals what it protects, it is a PIN and the
reading is the work.

---

## 3. The order of operations

Copying is last, not first.

1. **Declare the axes** that the corpus already covers implicitly — numerals,
   type symbols, the operator table, stdlib arity. Generate them. Run them
   against all five surfaces.
2. **Diff the generated matrices against the corpus.** Every corpus file whose
   behaviour is now covered by a cell is a CELL verdict, decided by
   measurement rather than by opinion. This is the step that makes the triage
   mechanical instead of 661 judgement calls.
3. **Read the eight gap logs** (`interpreter/LDV.md` § 5.1) against what remains.
   Every finding gets a pin; every remaining corpus file that matches a finding
   is that pin's starting point.
4. **Choose the seed set** from what is still standing.
5. **Everything left is DROP**, and the count is published.

The published count in step 5 is the honest measure of the move. If it is small,
the corpus was mostly explicable and ZyQuality was in better shape than § 1
suggests. If it is large, it was carrying files nobody could account for, which
is worth knowing either way.

---

## 4. What must not be lost

Three things that live *outside* `corpus/` and are worth more than most of what
is inside it:

| in ZyQuality | why it matters | verdict |
|---|---|---|
| `corpus.toml` | the one table where every exclusion states a reason | **carry over**, made stricter: a skipped cell names the axis value it skips |
| `messages/` | the diagnostic inventory — the only instrument that sees messages no test reaches; 804 one-sided on the shared surface | **carry over** as a first-class suite, in the gate from day one |
| `reject/` (34 forms) | programs every engine must refuse — the inverse assertion, which no consensus run can make | **carry over**; it is already close to a pure pin set |
| `coverage/` | what code no test has executed | **carry over, still outside the gate** — the reason is written in its own header and it is right |
| `bench/` + baseline | performance, with a number that may not rise | **carry over** unchanged |

---

## 5. The cutover

ZyQuality stays authoritative until ZyDDT can answer, for every question
ZyQuality answers today, at least as well — and until the three wrapper scripts
(`interpreter/tests/scripts/`, `web/tests/test_runner.mjs`) point at ZyDDT with
their names, flags and exit codes unchanged.

Until then ZyDDT is additive and green-or-absent: it must never be the reason a
release is blocked while it is still learning what it grades. The one thing it
may not do is what ZyQuality's own governance forbids — report success for
something it skipped.
