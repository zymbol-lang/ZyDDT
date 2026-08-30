# SPDX-License-Identifier: AGPL-3.0-only
"""Grading the grader.

A layer that judges three engines has to be judged itself.  ZyQuality learned
this the expensive way: the two harness defects found while producing its first
consensus numbers — a reversed argv and a missing module resolver — both
*inflated the divergence count*, and neither was visible in the output.  A
broken runner does not announce itself; it announces the engines.

Three parts, and the split is the point:

  **Cold** — the classifier, the parser, the comparator, the globs and the
  config readers, run against fixtures whose answer is known by inspection.
  These need no engine at all.  If they needed one, a broken engine would look
  like a broken runner and the test would be useless exactly when it matters.

  **Cmd** — every subcommand survives being called.  It exists because the cold
  part cannot see the command layer at all: a `NameError` in a command body once
  left every cold case green while `zyddt axis` was dead.

  **Live** — the engines are reachable and answer the seed program correctly.
  This one needs them, and says so.

Every stderr fixture below is real output, captured from `zymbol 0.0.9` or from
`web/tests/run_one.mjs` on 2026-08-27, pasted verbatim including the ANSI escape
codes the Rust CLI writes into a pipe.  A fixture somebody typed from memory
grades the memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import axes as A
from . import engines as E
from . import compare as C
from . import exclude as X
from . import observe as O
from .engines import Normalise, RawRun

NORM = Normalise()

# ── Real stderr, captured verbatim ───────────────────────────────────────────

RUST_ERROR = (
    "\x1b[1m\x1b[31merror\x1b[39m\x1b[0m: undefined variable 'noexiste'\n"
    "  \x1b[1m\x1b[34m-->\x1b[39m\x1b[0m /tmp/probe/err_static.zy:2:4\n"
    "\x1b[1m\x1b[34m   2\x1b[39m\x1b[0m \x1b[34m|\x1b[39m\n"
    "\x1b[1m\x1b[34m   2\x1b[39m\x1b[0m \x1b[34m|\x1b[39m >> noexiste ¶\n"
    "\x1b[34m     |\x1b[39m \x1b[1m\x1b[31m   ^^^^^^^^\x1b[39m\x1b[0m\n"
    "  \x1b[1m\x1b[32m= help:\x1b[39m\x1b[0m variables must be defined before use\n"
)
JS_ERROR = "error: undefined variable 'noexiste'\n  --> line 2\n"
RUST_WARN = (
    "warning: unused variable 'sinusar'\n"
    "  --> /tmp/probe/warn.zy:2:1\n"
    "  = help: consider removing this variable or prefixing with '_' "
    "if intentionally unused\n"
)
JS_WARN = (
    "warning: unused variable 'sinusar'\n"
    "  --> line 2\n"
    "  = help: consider removing this variable or prefixing with '_' "
    "if intentionally unused\n"
)
RUNTIME = "Runtime error: division by zero\n"
UNREADABLE = ("Error: failed to read file: /tmp/probe/nope.zy\n\n"
              "Caused by:\n    No such file or directory (os error 2)\n")


def _obs(engine: str, exit: int, out: str = "", err: str = "") -> O.Observation:
    return O.classify(RawRun(engine, "run", [], exit, out, err), NORM)


@dataclass
class Case:
    name: str
    what: str          # the answer, stated so the reader can check it by eye
    fn: callable


CASES: list[Case] = []


def case(name: str, what: str):
    def deco(fn):
        CASES.append(Case(name, what, fn))
        return fn
    return deco


# ── The classifier ───────────────────────────────────────────────────────────

@case("classify/ok", "silent stderr and exit 0 is ok")
def _():
    o = _obs("zytw", 0, "5\n", "")
    assert o.verdict == "ok", o.verdict
    assert o.out == "5\n"
    assert o.diags == ()


@case("classify/warn", "a warning is not a failure: the program still ran and printed")
def _():
    o = _obs("zytw", 0, "hola\n", RUST_WARN)
    assert o.verdict == "warn", o.verdict
    assert o.out == "hola\n", "the output must survive a warning"
    assert len(o.diags) == 1 and o.diags[0].severity == "warning"


@case("classify/error-static", "an `error:` with no output is a refusal")
def _():
    o = _obs("zytw", 1, "", RUST_ERROR)
    assert o.verdict == "error/static", o.verdict
    assert o.out == ""


@case("classify/error-runtime",
      "`Runtime error:` means it started — partial output is part of the answer")
def _():
    o = _obs("zytw", 1, "antes\n", RUNTIME)
    assert o.verdict == "error/runtime", o.verdict
    assert o.out == "antes\n"


@case("classify/exit-is-not-the-classifier",
      "`<~ 3` leaves a healthy program at exit 3; it is still ok")
def _():
    o = _obs("zytw", 3, "adios\n", "")
    assert o.verdict == "ok", f"exit code leaked into the verdict: {o.verdict}"
    assert o.exit == 3, "and the exit code is still recorded"


@case("classify/exit-0-after-an-error-is-not-ok",
      "the mirror: a diagnostic decides even when the process exits 0")
def _():
    o = _obs("zyjs", 0, "", JS_ERROR)
    assert o.verdict == "error/static", o.verdict


@case("classify/unreadable-is-BLOCKED",
      "stderr nothing recognised, with no diagnostic, is never a pass")
def _():
    # The bug this exists for: a missing file classified as `ok`, because no
    # rule matched and the exit code is deliberately not the classifier.
    o = _obs("zytw", 1, "", UNREADABLE)
    assert o.status == "BLOCKED", f"a missing file classified as {o.verdict}"


# ── The stderr parser ────────────────────────────────────────────────────────

@case("parse/ansi-stripped", "the Rust CLI colours a pipe; the colour must not reach the record")
def _():
    o = _obs("zytw", 1, "", RUST_ERROR)
    assert "\x1b" not in O.render(o), "ANSI leaked into the observation"
    assert o.diags[0].head == "undefined variable 'noexiste'", o.diags[0].head


@case("parse/source-excerpt-dropped",
      "the `2 | >> noexiste` block and its caret are presentation, not an answer")
def _():
    o = _obs("zytw", 1, "", RUST_ERROR)
    assert len(o.diags) == 1, f"the excerpt became {len(o.diags)} diagnostics"
    assert o.diags[0].body == (), o.diags[0].body
    assert o.leftover == (), o.leftover


@case("parse/both-location-layouts",
      "`--> path:2:4` and `--> line 2` are the same line 2")
def _():
    rust, js = _obs("zytw", 1, "", RUST_ERROR), _obs("zyjs", 1, "", JS_ERROR)
    assert rust.diags[0].line == 2 and js.diags[0].line == 2
    assert rust.diags[0].col == 4, "the column is recorded even when not compared"
    assert js.diags[0].col is None, "zyjs cannot produce one"


@case("parse/path-never-recorded",
      "the path is machine-dependent and must not reach the record")
def _():
    assert "/tmp/probe" not in O.render(_obs("zytw", 1, "", RUST_ERROR))


@case("parse/help-is-its-own-field", "`= help:` is not part of the message head")
def _():
    d = _obs("zytw", 0, "", RUST_WARN).diags[0]
    assert d.head == "unused variable 'sinusar'", d.head
    assert d.help and d.help.startswith("consider removing"), d.help


# ── The comparator ───────────────────────────────────────────────────────────

@case("compare/agree", "identical answers from two engines")
def _():
    c = C.consensus([_obs("zytw", 0, "5\n"), _obs("zyvm", 0, "5\n")])
    assert c.outcome == C.AGREE, c.outcome
    assert c.full and c.coverage == "2/2"


@case("compare/wording-not-diverge",
      "same refusal, same line, different words — inventory, not a regression")
def _():
    c = C.consensus([_obs("zytw", 1, "", RUST_ERROR), _obs("zyjs", 1, "", JS_ERROR)])
    assert c.outcome == C.WORDING, \
        f"a help line that only one engine emits came out {c.outcome}"


@case("compare/diverge-on-behaviour",
      "one refuses and one runs: that is a regression whatever the words")
def _():
    c = C.consensus([_obs("zytw", 1, "", RUST_ERROR), _obs("zyjs", 0, "", JS_WARN)])
    assert c.outcome == C.DIVERGE, c.outcome


@case("compare/exit-code-is-compared",
      "same text, different exit status: not the same answer")
def _():
    c = C.consensus([_obs("zytw", 0, "5\n"), _obs("zyvm", 3, "5\n")])
    assert c.outcome == C.DIVERGE, c.outcome


@case("compare/column-off-by-default",
      "zyjs cannot produce a column; comparing it would redden every diagnostic")
def _():
    pair = [_obs("zytw", 0, "hola\n", RUST_WARN), _obs("zyjs", 0, "hola\n", JS_WARN)]
    assert C.consensus(pair, compare_column=False).outcome == C.AGREE
    assert C.consensus(pair, compare_column=True).outcome == C.DIVERGE, \
        "--strict-column must actually change the answer"


@case("compare/blocked-never-equals-blocked",
      "two engines that both failed to run have not agreed about anything")
def _():
    a, b = _obs("zytw", 1, "", UNREADABLE), _obs("zyvm", 1, "", UNREADABLE)
    assert a.status == b.status == "BLOCKED"
    assert a.shape_key(False) != b.shape_key(False)
    assert C.consensus([a, b]).outcome == C.NO_VERDICT


@case("compare/one-answer-is-not-an-agreement",
      "an engine agreeing with itself is not a verdict")
def _():
    c = C.consensus([_obs("zytw", 0, "5\n"), _obs("zyvm", 1, "", UNREADABLE)])
    assert c.outcome == C.NO_VERDICT, c.outcome


@case("compare/excluded-is-not-blocked",
      "a declared absence still leaves a verdict, and it is marked 2/3")
def _():
    rule = X.Rule("x/*", ("zyjs",), "BASH_EXEC", "no browser equivalent")
    obs = [_obs("zytw", 0, "3\n"), _obs("zyvm", 0, "3\n"),
           O.Observation("zyjs", "run", "EXCLUDED", None, -1, "", excluded=rule)]
    c = C.consensus(obs)
    assert c.outcome == C.AGREE, c.outcome
    assert not c.full and c.coverage == "2/3", c.coverage


# ── The exclusion table ──────────────────────────────────────────────────────

@case("exclude/star-stays-inside-a-segment",
      "`environment/*` must not silently catch `environment/db/deep`")
def _():
    assert X._glob("environment/*", "environment/shell-pipe")
    assert not X._glob("environment/*", "environment/db/deep")
    assert X._glob("environment/**", "environment/db/deep")


@case("exclude/reason-is-mandatory",
      "an exclusion nobody explained is indistinguishable from a hidden bug")
def _(tmp: Path = None):
    import tempfile
    p = Path(tempfile.mkdtemp()) / "x.toml"
    p.write_text('[[rule]]\nmatch = "a/b"\nengines = ["zyjs"]\ntag = "T"\n')
    try:
        X.load(p)
    except SystemExit:
        return
    raise AssertionError("a rule with no reason was accepted")


@case("exclude/engineless-rule-covers-every-engine",
      "omitting `engines` means the case's output is not a function of the program")
def _():
    t = X.Table((X.Rule("a/*", (), "T", "wall time"),), set())
    assert t.excluded("a/b", "zytw") and t.excluded("a/b", "zyjs")


@case("exclude/dead-rule-is-reported",
      "a rule that matched no case is a list that stopped describing anything")
def _():
    t = X.Table((X.Rule("gone/*", ("zyjs",), "T", "why"),), set())
    t.excluded("here/x", "zyjs")
    assert len(t.dead_rules()) == 1


# ── Axes and the generator ───────────────────────────────────────────────────

@case("axes/suggestive-oracle-is-caught",
      "an oracle whose answer is typed into the .zy source checks nothing")
def _():
    # The exact cell that shipped: the zymbol side printed a literal chosen
    # knowing the answer, the python side computed it. Two copies of one number.
    fraud = A.Cell("x", "c", "", ">> 9007199254740991 ¶\n")
    assert A.suggestive(fraud, "9007199254740991\n") == "9007199254740991"

    honest = A.Cell("x", "c", "", ">> (2 ^ 52) + (2 ^ 52 - 1) ¶\n")
    assert A.suggestive(honest, "9007199254740991\n") is None

    # Short answers collide by accident, so the test does not apply below four
    # characters: "42" is in half of all arithmetic sources.
    short = A.Cell("x", "c", "", ">> 6 * 7 ¶\n")
    assert A.suggestive(short, "42\n") is None

    # And it is a heuristic, so a declared reason silences it.
    excused = A.Cell("x", "c", "", ">> 1000 + 0 ¶\n",
                     oracle_literal_ok="the addend is the answer here")
    assert A.suggestive(excused, "1000\n") is None


@case("axes/one-oracle-per-cell",
      "two oracles that disagree is a question about the oracles")
def _():
    try:
        A._oracle_of({"id": "c", "oracle": {"py": "1", "js": "2"}}, Path("a.toml"))
    except SystemExit:
        return
    raise AssertionError("a cell with two oracles was accepted")


@case("axes/declared-axes-load", "every axes/*.toml parses and declares cells")
def _():
    loaded = A.load_all()
    assert loaded, "no axes declared"
    for ax in loaded:
        assert ax.cells, f"axis {ax.id} declares no cells"
        assert ax.what, f"axis {ax.id} does not say what it is"
        for c in ax.cells:
            assert c.what, f"cell {ax.id}/{c.id} does not say what it is"


@case("axes/exclusions-parse", "exclusions.toml loads and every rule has a reason")
def _():
    for r in X.load().rules:
        assert r.reason and r.tag


@case("compare/offenders-are-named-on-a-divergence",
      "`they differ` routes nowhere; `zyjs answered warn` routes to one file")
def _():
    # The check used to run only after the engines agreed, so the case where
    # naming a culprit matters most reported DIVERGE and stopped.
    obs = [_obs("zytw", 1, "", RUST_ERROR), _obs("zyvm", 1, "", RUST_ERROR),
           _obs("zyjs", 0, "hola\n", JS_WARN)]
    assert C.consensus(obs).outcome == C.DIVERGE
    bad = C.offenders(obs, "error")
    assert [o.engine for o in bad] == ["zyjs"], [o.engine for o in bad]


@case("compare/offenders-ignores-what-did-not-answer",
      "an engine that was excluded or blocked cannot be out of compliance")
def _():
    rule = X.Rule("x/*", ("zyjs",), "BASH_EXEC", "no browser equivalent")
    obs = [_obs("zytw", 1, "", RUST_ERROR),
           _obs("zyvm", 1, "", UNREADABLE),                     # BLOCKED
           O.Observation("zyjs", "run", "EXCLUDED", None, -1, "", excluded=rule)]
    assert C.offenders(obs, "error") == []


@case("compare/all-three-wrong-together-is-not-a-divergence",
      "the class only an oracle or an expect can find: they agree, and agree wrongly")
def _():
    obs = [_obs(e, 0, "hola\n", JS_WARN) for e in ("zytw", "zyvm", "zyjs")]
    assert C.consensus(obs).outcome == C.AGREE, "a differential sees nothing here"
    assert len(C.offenders(obs, "error")) == 3, "and expect sees all three"


@case("compare/oracle-runs-on-every-shared-shape",
      "a wording split must not switch off the correctness check underneath it")
def _():
    # The oracle sat after the WORDING branch at first, so a cell whose engines
    # differed only in the words of a diagnostic never had its answer checked.
    assert C.oracle_applies(C.AGREE)
    assert C.oracle_applies(C.WORDING), "a wording split silenced the oracle"
    assert C.oracle_applies(C.PARTIAL)
    # No single answer to check in these two.
    assert not C.oracle_applies(C.DIVERGE)
    assert not C.oracle_applies(C.NO_VERDICT)


@case("verdict/red-beats-no-verdict",
      "a run that diverged AND could not judge something exits 1, not 2")
def _():
    # Exit 2 tells a CI the harness could not run. Saying that when the harness
    # ran fine and the code diverged points the reader at the wrong thing.
    assert C.worse(C.NOVERDICT, C.RED) == C.RED
    assert C.worse(C.RED, C.NOVERDICT) == C.RED
    assert C.worse(C.GREEN, C.NOVERDICT) == C.NOVERDICT
    assert C.worse(C.GREEN, C.GREEN) == C.GREEN


# ── The matrix ───────────────────────────────────────────────────────────────
#
# The generator is the one part of this layer that can manufacture coverage that
# does not exist.  A template that expands wrong still writes a `.zy`, the `.zy`
# still runs, and the run is still counted in the denominator — so the cell is
# reported as coverage of a question it never asked.  Every case below is one
# way that could happen.

def _dim(name, values, **defaults):
    return {"name": name, "values": values, "defaults": defaults}


@case("matrix/cross-product-is-every-point",
      "two dimensions produce n×m cells, not n+m")
def _():
    cells = A._matrix_cells(
        {"dimension": [_dim("op", ["a", "b", "c"]), _dim("v", ["x", "y"])],
         "matrix": {"id": "«op»-«v»", "src": ">> «op» «v» ¶"}},
        "t", Path("t.toml"))
    assert len(cells) == 6, len(cells)
    assert {c.id for c in cells} == {"a-x", "a-y", "b-x", "b-y", "c-x", "c-y"}


@case("matrix/placeholder-is-not-a-brace",
      "a template body is Zymbol, and Zymbol spends braces")
def _():
    # The reason the delimiter is «…». `str.format` would read `{ <~ a }` as a
    # field name and raise, and `{name}` inside a Zymbol string is an
    # interpolation the generator must leave alone.
    src = 'f(a) { <~ a }\n>> "hola {name}" ¶\n>> «v» ¶'
    got = A.expand(src, {"v": {"id": "x", "v": "7"}}, "t")
    assert "{ <~ a }" in got and '"hola {name}"' in got and ">> 7 ¶" in got


@case("matrix/unknown-name-is-fatal",
      "a typo that expanded to nothing would be counted as coverage")
def _():
    for bad in ("«nope»", "«v.nofield»"):
        try:
            A.expand(bad, {"v": {"id": "x", "v": "7"}}, "t")
        except SystemExit:
            continue
        raise AssertionError(f"{bad} expanded silently")


@case("matrix/duplicate-cell-id-is-fatal",
      "two cells with one name are one file, and the denominator counts both")
def _():
    import tempfile, tomllib
    p = Path(tempfile.mkdtemp()) / "dup.toml"
    # `id` names only the first dimension, so the second collapses: four points
    # of the matrix write two files, and the two survivors are whichever ran
    # last. The generator would report four cells either way.
    p.write_text('id = "d"\n'
                 '[[dimension]]\nname = "a"\nvalues = ["p", "q"]\n'
                 '[[dimension]]\nname = "b"\nvalues = ["r", "s"]\n'
                 '[matrix]\nid = "«a»"\nsrc = ">> 1 ¶"\n', encoding="utf-8")
    d = tomllib.loads(p.read_text(encoding="utf-8"))
    ids = [c.id for c in A._matrix_cells(d, "dup", p)]
    assert len(ids) == 4 and len(set(ids)) == 2, ids   # the collision is real
    try:
        A.load_all_from(p.parent)                       # and load_all refuses it
    except SystemExit as e:
        assert "twice" in str(e), e
        return
    raise AssertionError("an axis whose cells collide onto one file was accepted")


@case("matrix/value-id-must-be-a-filename",
      "there is no slugification, because two guesses that collide merge two points")
def _():
    try:
        A._values_of({"name": "op", "values": ["+"]}, "t.toml")
    except SystemExit:
        return
    raise AssertionError("'+' was accepted as a cell id")


@case("matrix/defaults-fill-only-what-a-value-omits",
      "one field that varies on two values stays out of the other sixty-seven")
def _():
    vals = A._values_of(
        {"name": "s", "defaults": {"decimal": "."},
         "values": [{"id": "a"}, {"id": "b", "decimal": "\u066b"}]}, "t.toml")
    assert vals[0]["decimal"] == "." and vals[1]["decimal"] == "\u066b"


@case("matrix/skip-states-a-reason-and-names-the-point",
      "CHARTER § 5: a hole in a matrix has to be visible AS a hole")
def _():
    coords = {"op": {"id": "pow"}, "pair": {"id": "int-int"}}
    r = A._skip_reason([{"when": {"op": "pow"}, "reason": "why"}], coords, "t")
    assert r is not None and "op=pow" in r and "why" in r
    assert A._skip_reason([{"when": {"op": "plus"}, "reason": "w"}], coords, "t") is None
    try:
        A._skip_reason([{"when": {"op": "pow"}}], coords, "t")
    except SystemExit:
        return
    raise AssertionError("a skip with no reason was accepted")


@case("matrix/skip-may-not-name-an-undeclared-dimension",
      "a skip on a dimension that does not exist would never match and never say so")
def _():
    try:
        A._skip_reason([{"when": {"nope": "x"}, "reason": "r"}],
                       {"op": {"id": "pow"}}, "t")
    except SystemExit:
        return
    raise AssertionError("a skip named a dimension the matrix does not declare")


# ── Surfaces: the tolerance rule ─────────────────────────────────────────────

@case("surface tolerates what it declares", "and nothing else")
def _():
    surf = E.Surface(id="s", cmd=[], desc="", tolerate=r"[][(){}\s]+")
    for text in ("(", ")", "()", "] {", "  "):
        assert surf.excused(text), f"should tolerate {text!r}"
    # The two the corpus actually found, and the reason the rule is narrow: a
    # `|` inside `0x|…|` and a bare `#` are operators, not punctuation.
    for text in ("|", "#", "$++", "(a"):
        assert not surf.excused(text), f"should NOT tolerate {text!r}"


@case("a surface with no rule tolerates nothing", "the default is strict")
def _():
    surf = E.Surface(id="s", cmd=[], desc="")
    for text in ("(", " ", "|", ""):
        assert not surf.excused(text), f"should NOT tolerate {text!r}"


@case("engines.toml declares both lexer surfaces", "or the gate grades three of five")
def _():
    cfg = E.load()
    ids = {s.id for s in cfg.surfaces}
    assert ids == {"highlight", "tmgrammar"}, ids
    # A tolerance without a reason is indistinguishable from a gap somebody hid
    # — the rule corpus.toml states about exclusions, applied here.
    for s in cfg.surfaces:
        assert not s.tolerate or s.reason, f"{s.id} tolerates without saying why"


# ── The command surface ──────────────────────────────────────────────────────

# Every subcommand, with arguments cheap enough to run on every selftest.
# `selftest` and `suite` are absent on purpose: suite calls selftest, so
# including either would recurse.
SMOKE: list[tuple[str, list[str]]] = [
    ("engines", []),
    ("gen", []),
    ("axis", ["verdict"]),
    ("observe", ["generated/verdict/ok.zy"]),
    ("ask", ["generated/verdict/ok.zy"]),
    ("check", ["--regen", "cases/seed/hello.zy"]),
    ("surfaces", []),
]


def smoke_cli(script: Path, timeout: float = 60.0) -> list[str]:
    """Run every subcommand and require it not to crash.

    This exists because of a hole in this very file.  A slice-and-splice edit to
    bin/zyddt deleted `_observe_all`, `zyddt axis` died with a NameError — and
    `zyddt selftest` still reported 28/28, because every cold case imports the
    `zyddt` package and none of them touches the command layer.  A grader that
    passes while its own front end is broken is the exact failure it exists to
    catch, one level in.

    Nothing here checks WHAT a command printed; the cold cases and the axes do
    that.  This only asks whether the command survives being called at all, which
    is the part no other test covers.
    """
    import subprocess
    root = script.resolve().parents[1]
    bad = []
    for cmd, extra in SMOKE:
        try:
            p = subprocess.run([str(script), cmd, *extra], capture_output=True,
                               timeout=timeout, cwd=root)
        except subprocess.TimeoutExpired:
            bad.append(f"{cmd}: timed out after {timeout:g}s")
            continue
        # 0/1/2 are the verdicts. Anything else is the runner falling over —
        # a Python traceback exits 1, so the stderr check is what catches it.
        err = p.stderr.decode("utf-8", "replace")
        if p.returncode not in (0, 1, 2):
            bad.append(f"{cmd}: exit {p.returncode}")
        elif "Traceback (most recent call last)" in err:
            bad.append(f"{cmd}: {err.strip().splitlines()[-1]}")
    # `check --regen` writes goldens beside the seed; it is a smoke run, not a
    # recording, so they do not survive it.
    for g in (root / "cases" / "seed").glob("*.observed"):
        g.unlink()
    return bad


def run(verbose: bool = False) -> tuple[int, int, list[str]]:
    """→ (passed, total, failures). Needs no engine."""
    failures = []
    for c in CASES:
        try:
            c.fn()
            if verbose:
                print(f"    ok    {c.name:<44} {c.what}")
        except Exception as e:  # noqa: BLE001 — a selftest reports, never raises
            failures.append(f"{c.name}: {e}")
    return len(CASES) - len(failures), len(CASES), failures
