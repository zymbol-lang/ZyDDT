# SPDX-License-Identifier: AGPL-3.0-only
"""Reading engines.toml, and running one program through one engine.

This module knows how to *invoke*; it does not know what an answer means.
Classification lives in `observe.py`, so that adding an engine cannot change
what a verdict is.
"""

from __future__ import annotations

import os
import re
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ${NAME:-default} — the same expansion ZyQuality's engines.toml documents, so a
# release gate can point the layer at an installed package with ZYMBOL_BIN.
_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


def _expand(s: str) -> str:
    return _VAR.sub(lambda m: os.environ.get(m.group(1)) or (m.group(2) or ""), s)


@dataclass(frozen=True)
class Engine:
    id: str
    cmd: list[str]
    check_cmd: list[str] | None
    desc: str

    def argv(self, phase: str, file: Path) -> list[str] | None:
        """argv for this phase, or None if the engine cannot answer it.

        None is not a pass and not a failure — it is SKIPPED, and the caller
        must report it as such.

        The program path is made absolute first.  Engines run with cwd=ROOT so
        that engines.toml's relative paths (`../web/tests/run_one.mjs`) resolve
        the way that file documents; a relative PROGRAM path would then be
        resolved against ROOT too, and `zyddt ask ZyDDT/generated/x.zy` from the
        workspace root looked for `ZyDDT/ZyDDT/generated/x.zy`.  Found by
        running the tool from one directory up, which is how every other
        repository will call it.
        """
        template = self.cmd if phase == "run" else self.check_cmd
        if template is None:
            return None
        target = str(Path(file).resolve())
        return [_expand(a).replace("{file}", target) for a in template]


@dataclass(frozen=True)
class Normalise:
    strip_ansi: bool = True
    drop_source_excerpt: bool = True
    keep_location: str = "line"
    compare_column: bool = False


@dataclass(frozen=True)
class Oracle:
    """An implementation in another language, used to decide whether an answer
    the engines AGREE on is also right.  Never under test itself."""

    id: str
    cmd: list[str]
    ext: str
    desc: str

    def argv(self, file: Path) -> list[str]:
        return [_expand(a).replace("{file}", str(Path(file).resolve()))
                for a in self.cmd]


@dataclass(frozen=True)
class Config:
    engines: list[Engine] = field(default_factory=list)
    oracles: dict = field(default_factory=dict)
    normalise: Normalise = field(default_factory=Normalise)

    def by_id(self, ids: list[str] | None) -> list[Engine]:
        if not ids:
            return list(self.engines)
        known = {e.id: e for e in self.engines}
        missing = [i for i in ids if i not in known]
        if missing:
            raise SystemExit(f"zyddt: no such engine: {', '.join(missing)}")
        return [known[i] for i in ids]


def load(path: Path | None = None) -> Config:
    path = path or (ROOT / "engines.toml")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    engines = [
        Engine(
            id=e["id"],
            cmd=e["cmd"],
            check_cmd=e.get("check_cmd"),
            desc=e.get("desc", ""),
        )
        for e in data.get("engine", [])
    ]
    oracles = {o["id"]: Oracle(o["id"], o["cmd"], o.get("ext", ".txt"),
                               o.get("desc", ""))
               for o in data.get("oracle", [])}
    return Config(engines=engines, oracles=oracles,
                  normalise=Normalise(**data.get("normalise", {})))


@dataclass(frozen=True)
class RawRun:
    """What the process actually did. No interpretation."""

    engine: str
    phase: str
    argv: list[str]
    exit: int
    stdout: str
    stderr: str
    blocked: str | None = None  # why no answer was obtained, if none was


def run_oracle(oracle: Oracle, file: Path, timeout: float = 30.0) -> RawRun:
    """Run the independent implementation. Its stderr is not a diagnostic about
    Zymbol, so a failing oracle is BLOCKED — never a verdict about the case."""
    try:
        p = subprocess.run(oracle.argv(file), capture_output=True,
                           timeout=timeout, cwd=ROOT)
    except FileNotFoundError as e:
        return RawRun(oracle.id, "oracle", [], -1, "", "",
                      blocked=f"not executable: {e.filename}")
    except subprocess.TimeoutExpired:
        return RawRun(oracle.id, "oracle", [], -1, "", "",
                      blocked=f"timed out after {timeout:g}s")
    if p.returncode != 0:
        return RawRun(oracle.id, "oracle", [], p.returncode, "", "",
                      blocked=f"oracle failed: "
                              f"{p.stderr.decode('utf-8', 'replace').strip().splitlines()[-1:] or ['(silent)']}"
                              .strip("[]'"))
    return RawRun(oracle.id, "oracle", [], 0,
                  p.stdout.decode("utf-8", "replace"),
                  p.stderr.decode("utf-8", "replace"))


def run(engine: Engine, file: Path, phase: str = "run", timeout: float = 30.0,
        stdin: bytes = b"") -> RawRun:
    argv = engine.argv(phase, file)
    if argv is None:
        return RawRun(engine.id, phase, [], -1, "", "",
                      blocked=f"engine has no {phase} entry point")
    try:
        p = subprocess.run(
            argv, input=stdin, capture_output=True, timeout=timeout, cwd=ROOT
        )
    except FileNotFoundError as e:
        # The binary is absent. Never a pass: an engine that did not run has not
        # agreed with anything.
        return RawRun(engine.id, phase, argv, -1, "", "", blocked=f"not executable: {e.filename}")
    except subprocess.TimeoutExpired:
        return RawRun(engine.id, phase, argv, -1, "", "", blocked=f"timed out after {timeout:g}s")
    return RawRun(
        engine.id, phase, argv, p.returncode,
        p.stdout.decode("utf-8", "replace"),
        p.stderr.decode("utf-8", "replace"),
    )
