# Part 0 — Modern Python Project Structure

You **build** the course folder in this part — nothing here is handed to you finished. Acceptance is mechanical: a step is done when the stated command exits `0` (check with `echo $?`), and Exercises 0.2 and 0.5 add the usual asserts. Everything lives in one directory (`~/projects/crash-course/` is used throughout): the project you are about to create, and each `part-N.md` you download as you reach it — this file included.

## 0.1 Anatomy of a project

```text
crash-course/                  # the directory YOU create — project and workbook in one
├── part-0.md … part-7.md      # the parts you have downloaded so far; this file is the first
├── pyproject.toml             # single source of truth: metadata, deps, build backend, tool config (0.2)
├── README.md                  # gets a stranger from clone to running toolchain in under a minute
├── .gitignore                 # keeps everything regenerable out of git (0.5)
├── src/
│   └── crash_course/          # the importable package — the directory name IS the import name
│       └── __init__.py        # marks a regular package; carries __version__
├── tests/
│   └── test_smoke.py          # outside the package; a suite that collects nothing makes bare `pytest` exit 5, not 0
├── scratch.py                 # where every later exercise gets worked; never committed
└── .venv/                     # per-project interpreter + deps — gitignored, like the tool caches
```

```python
# The flat-layout trap: with crash_course/ at the project root, the CWD copy would
# shadow the installed package — tests can go green against code that was never packaged.
import crash_course

print(crash_course.__file__)   # src layout: resolves ONLY through the (editable) install
                               # -> .../src/crash_course/__init__.py
```
Nothing under the project root is importable by accident; `import crash_course` works only once `pip install -e .` wires it up. Build order matters for the rest of this part: **`__init__.py` and `README.md` must exist before the first install**, because `pyproject.toml` will point at both and a build resolves those pointers (0.2, 0.3).

**Exercise 0.1** — Create the skeleton, in this order, and watch the pre-install failure.
```bash
mkdir -p ~/projects/crash-course/src/crash_course ~/projects/crash-course/tests
cd ~/projects/crash-course
printf '__version__ = "0.1.0"\n' > src/crash_course/__init__.py   # regular package: the dir needs this file
printf '# crash-course\n\nRunning example for the Python crash course.\n' > README.md
python3 -c "import crash_course"   # pass: ModuleNotFoundError — src layout doing its job, nothing is installed yet
```

## 0.2 pyproject.toml — the single source of truth

One file replaces `setup.py`, `setup.cfg`, `requirements.txt`, and a drawer of tool dotfiles. Every key below is read at **build** time, so a key naming a file is a hard dependency on that file existing — this is the shape, not the contents; Exercise 0.2's asserts pin the values.

```toml
[project]
name = "..."                     # distribution name (dashes fine; PyPI-facing)
version = "..."                  # canonical version — semver, see 0.5
description = "..."              # one line; free text
readme = "..."                   # a POINTER: the build opens this file and fails loudly if it is missing
requires-python = "..."          # installers refuse older interpreters outright
dependencies = []                # RUNTIME deps only — dev tools do not belong here

[project.optional-dependencies]
dev = [...]                      # an "extra": opt-in group, installed via  pip install -e ".[dev]"

[build-system]
requires = [...]                 # build-time dep, fetched into an isolated build env
build-backend = "..."            # who turns this source tree into a wheel

[tool.hatch.build.targets.wheel]
packages = [...]                 # ALSO a pointer: name a directory that does not exist and the
                                 # editable install silently wires up nothing (0.3)
```
Gotcha: the distribution is `crash-course` (dash) but the import is `crash_course` (underscore) — `pip install` names and `import` names are different namespaces. Every tool you add configures itself under its own `[tool.*]` table in this same file (0.4).

**Exercise 0.2** — Write `pyproject.toml` until these asserts pass. Run them from the project root; this is the file the rest of Part 0 depends on.
```python
import tomllib

def meta(path: str = "pyproject.toml") -> dict[str, object]:
    # parse the file the way every build tool does
    # hint: tomllib.load wants a BINARY file handle
    ...

project = meta()["project"]
assert project["name"] == "crash-course"
assert project["version"] == "0.1.0"
assert project["readme"] == "README.md"
assert project["requires-python"] == ">=3.11"
assert project["dependencies"] == []
assert project["optional-dependencies"]["dev"] == ["ruff", "mypy", "pytest"]
assert meta()["build-system"]["requires"] == ["hatchling"]
assert meta()["build-system"]["build-backend"] == "hatchling.build"
assert meta()["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == ["src/crash_course"]
```

## 0.3 Environments & dependencies

The venv is the isolation boundary; the editable install is what makes `src/` importable. Run these from the project root, in this order — steps 1–2 of Exercise 0.1 are prerequisites, not decoration.

```bash
python3 -m venv .venv               # private interpreter + site-packages under ./.venv
source .venv/bin/activate           # puts .venv/bin first on PATH — python/pip now mean THIS env
python -m pip install -e ".[dev]"   # -e (editable): src/ edits are live, no reinstall; [dev] pulls the extra
# uv is a drop-in accelerator for the same model: uv venv / uv pip install -e ".[dev]"
```

```bash
python -m pip freeze > requirements.lock     # snapshot EXACT versions, transitive deps included
python -m pip install -r requirements.lock   # replay: identical env on CI, prod, a colleague's laptop
```
Applications commit a lockfile because a deploy must be byte-for-byte reproducible; libraries instead declare ranges in `pyproject.toml` (e.g. `requests>=2.31`) because they can't dictate the consuming environment. This project commits no lockfile — it is library-shaped, with all tooling in the `dev` extra.

**Exercise 0.3a** — Prove the isolation boundary.
```bash
which python                # pass: a path under .venv/bin
python -m pip list          # pass: crash-course 0.1.0, ruff, mypy, pytest — and almost nothing else
deactivate; which python3   # pass: the system path again (e.g. /usr/bin/python3) — the env was the ONLY change
source .venv/bin/activate   # back in before you continue
```

**Exercise 0.3b** — Break both pointers from 0.2 and read the two failure modes; they fail very differently.
```bash
mv README.md /tmp/ && python -m pip install -e ".[dev]"
# pass: the build fails, naming the missing readme. It dies during METADATA generation —
# before pip resolves a single dependency, which is why nothing at all gets installed.
# Then put it back: mv /tmp/README.md .

mv src/crash_course /tmp/ && python -m pip install -e ".[dev]"
# pass: the install reports SUCCESS, then `python -c "import crash_course"` raises ModuleNotFoundError.
# An editable install of a package directory that does not exist wires up nothing and says nothing.
mv /tmp/crash_course src/ && python -m pip install -e ".[dev]"
```
A loud failure costs you a minute; the silent one costs an afternoon. The tell for the silent case: the installed `*.dist-info/RECORD` lists metadata only — no `.pth`, no `__editable__` finder, so nothing was ever added to the import path.

## 0.4 The tooling triad, wired into pre-commit

Three independent gates: **ruff** answers "is it clean?" in milliseconds (style plus a class of real bugs), **mypy** answers "is it consistent?" (whole-program type contradictions), **pytest** answers "is it correct?" (behavior). Add their config to the same `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100                    # one agreed width — end of formatting debates
target-version = "py311"             # lets UP rules rewrite code to 3.11+ idioms
src = ["src"]                        # first-party root, so import-sorting classifies correctly

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]  # pycodestyle, pyflakes (undefined names!), import order,
                                     # pyupgrade, bugbear (mutable defaults, late-binding loops)

[tool.mypy]
python_version = "3.11"
strict = true                        # untyped defs, implicit Any, discarded returns: all errors

[tool.pytest.ini_options]
addopts = "-ra"                      # end-of-run summary line for every non-passing test
pythonpath = ["src"]                 # tests can import the package even without an install
```

`pre-commit` runs the gates on `git commit` and blocks the commit on any failure — the point is that red never even reaches CI. Your project is its own git root, so the hooks run from where you commit:

```text
# .pre-commit-config.yaml — saved at the GIT ROOT. If a project sits below its
# repo root, each entry has to `cd` in first; yours does not.
repos:
  - repo: local              # local + system = run the activated venv's own tools (no version skew)
    hooks:
      - id: ruff
        name: ruff
        entry: ruff check .
        language: system
        pass_filenames: false   # run repo-wide, not only on staged files
      - id: mypy
        name: mypy
        entry: mypy src
        language: system
        pass_filenames: false
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
```

**Exercise 0.4a** — Predict which gate catches each planted bug, then confirm. Add each line below to `src/crash_course/__init__.py` one at a time, run all three commands, note which goes red (and with what rule code), then revert.
```bash
# 1) import os                                        -> which tool? which code?
# 2) def f(x: int) -> str: return x                   -> which tool?
# 3) def g(items: list[int] = []) -> list[int]: return items   -> which tool? which code?
ruff check . && mypy src && pytest   # after reverting: exits 0 again (echo $?)
```
`pytest` exits 5 — not 0 — on a suite that collects nothing, which fails the gate for the wrong reason. Give `tests/test_smoke.py` one trivial test before you wire the hooks.

**Exercise 0.4b** — Wire the hooks: `git init` if you haven't, `pip install pre-commit`, save the config above as `.pre-commit-config.yaml` at the project root, run `pre-commit install` (in a real project, pre-commit itself would join the dev extra).
```bash
pre-commit run --all-files   # pass: every hook reports Passed, exit 0
```

## 0.5 Conventions that signal seniority

A README that gets a stranger running in a minute, a `.gitignore` that excludes everything regenerable, and a CHANGELOG (Keep a Changelog format, written for consumers, not committers) separate a *project* from a pile of files. The test for belonging in `.gitignore` is exactly "can this be rebuilt from source?" — Exercise 0.5's asserts pin the set your project needs.

```python
# Semantic versioning: MAJOR.MINOR.PATCH = breaking change / new feature / bugfix.
# A leading 0 (this project: 0.1.0) means "no stability contract yet".
# Declared in [project].version — and duplicated into crash_course.__version__,
# which is a drift risk you check mechanically in Exercise 0.5.
```

```python
import csv             # module: a single importable .py file
import crash_course    # regular package: a directory WITH __init__.py (src/crash_course here)

# namespace package: a package directory WITHOUT __init__.py — its pieces can be
# merged from several installed distributions (a plugin-ecosystem feature).
# Gotcha: a forgotten __init__.py doesn't error; it silently changes the kind.
```

```toml
# Not needed here — the shape you add when a package ships a CLI:
[project.scripts]
crash-course = "crash_course.cli:main"   # install generates a `crash-course` command that calls main()
```

**Exercise 0.5** — Write `.gitignore`, then prove both conventions mechanically.
```python
import tomllib
from pathlib import Path

import crash_course

def versions_match() -> bool:
    # compare crash_course.__version__ with [project].version in pyproject.toml
    # hint: tomllib.load needs "rb"; the key path is ["project"]["version"]
    ...

def ignored() -> set[str]:
    # the meaningful entries of .gitignore — no blanks, no # comments
    # hint: Path.read_text().splitlines(), then strip and filter
    ...

assert versions_match()
assert {".venv/", "__pycache__/", "*.egg-info/"} <= ignored()
assert {".mypy_cache/", ".pytest_cache/", ".ruff_cache/"} <= ignored()
```

### How to work through this efficiently
Build as you read — every command here runs against the project you just created, so nothing is hypothetical. Do 0.3b slowly once: knowing what a loud build failure looks like *and* what a silent no-op install looks like is what lets you trust a green install later. Chapters 14, 15, and 18 drill this material with exercises — when you get there, reference back here rather than re-deriving. Part 0 is done when `ruff check . && mypy src && pytest` exits 0, your pre-commit hook blocks a deliberately bad commit, and `pip list` shows the dev extra installed. Then download `part-1.md` into this same folder and start Chapter 1 — [HOW-TO-USE.md](HOW-TO-USE.md) has the command.
