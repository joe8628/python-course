# Part 0 — Modern Python Project Structure

Everything in this part runs against this directory (`python-crash-course/`) — a real src-layout project. The acceptance tests here are mostly commands rather than asserts: a step is done when the stated command exits `0` (check with `echo $?`); Exercises 0.2 and 0.5 are the usual scaffold-plus-asserts drills.

## 0.1 Anatomy of a project

```text
python-crash-course/           # the directory you are sitting in
├── pyproject.toml             # single source of truth: metadata, deps, build backend, tool config (0.2)
├── README.md                  # gets a stranger from clone to running toolchain in under a minute
├── .gitignore                 # keeps everything regenerable out of git (0.5)
├── src/
│   └── crash_course/          # the importable package — the directory name IS the import name
│       └── __init__.py        # marks a regular package; carries __version__
├── tools/
│   └── lint_workbook.py       # repo-local dev script, deliberately NOT inside the package
├── SPEC.md · PROGRESS.md · part-0.md … part-7.md   # workbook content, not code
└── .venv/                     # per-project interpreter + deps — gitignored, like the tool caches
```

```python
# The flat-layout trap: with crash_course/ at the repo root, the CWD copy would
# shadow the installed package — tests can go green against code that was never packaged.
import crash_course

print(crash_course.__file__)   # src layout: resolves ONLY through the (editable) install
                               # -> .../src/crash_course/__init__.py
```
Nothing under the repo root is importable by accident; `import crash_course` works only because `pip install -e .` wired it up. That means what you test is always what ships.

**Exercise 0.1** — Prove the wiring on this repo (venv active, from `python-crash-course/`).
```bash
python -c "import crash_course as cc; print(cc.__version__, cc.__file__)"
# pass: prints 0.1.0 and a path ending in src/crash_course/__init__.py
# also worth seeing once: run it BEFORE `pip install -e .` in a fresh venv
# -> ModuleNotFoundError. That failure is src layout doing its job.
```

## 0.2 pyproject.toml — the single source of truth

One file replaces `setup.py`, `setup.cfg`, `requirements.txt`, and a drawer of tool dotfiles. Quoted from this repo's `pyproject.toml`:

```toml
[project]
name = "crash-course"            # distribution name (dashes fine; PyPI-facing)
version = "0.1.0"                # canonical version — semver, see 0.5
description = "Running example project for the Python Proficiency Crash Course workbook"
readme = "README.md"
requires-python = ">=3.11"       # installers refuse older interpreters outright
dependencies = []                # RUNTIME deps only — dev tools do not belong here

[project.optional-dependencies]
dev = [                          # an "extra": opt-in group, installed via  pip install -e ".[dev]"
    "ruff",
    "mypy",
    "pytest",
]

[build-system]
requires = ["hatchling"]              # build-time dep, fetched into an isolated build env
build-backend = "hatchling.build"     # who turns this source tree into a wheel

[tool.hatch.build.targets.wheel]
packages = ["src/crash_course"]       # what goes INTO the wheel; src/ is stripped on install
```
Gotcha: the distribution is `crash-course` (dash) but the import is `crash_course` (underscore) — `pip install` names and `import` names are different namespaces. Every tool you add configures itself under its own `[tool.*]` table in this same file (0.4).

**Exercise 0.2** — Read the file the way tools do: mechanically, with the stdlib.
```python
import tomllib

def dev_deps(path: str = "pyproject.toml") -> list[str]:
    # return the dev extra's package names, in file order
    # hint: tomllib.load wants a BINARY file handle; extras live under
    # [project.optional-dependencies]
    ...

assert dev_deps() == ["ruff", "mypy", "pytest"]
```

## 0.3 Environments & dependencies

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
Applications commit a lockfile because a deploy must be byte-for-byte reproducible; libraries instead declare ranges in `pyproject.toml` (e.g. `requests>=2.31`) because they can't dictate the consuming environment. This repo commits no lockfile — it is library-shaped, with all tooling in the `dev` extra.

**Exercise 0.3** — Prove the isolation boundary.
```bash
which python                # pass: a path under .venv/bin
python -m pip list          # pass: crash-course 0.1.0, ruff, mypy, pytest — and almost nothing else
deactivate; which python    # pass: the system interpreter again — the env was the ONLY change
source .venv/bin/activate   # back in before you continue
```

## 0.4 The tooling triad, wired into pre-commit

Three independent gates: **ruff** answers "is it clean?" in milliseconds (style plus a class of real bugs), **mypy** answers "is it consistent?" (whole-program type contradictions), **pytest** answers "is it correct?" (behavior). Their config lives in the same `pyproject.toml` — quoted from this repo:

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

`pre-commit` runs the gates on `git commit` and blocks the commit on any failure — the point is that red never even reaches CI. This file is **not** shipped in this repo; you write it in Exercise 0.4b:

```text
# .pre-commit-config.yaml
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

**Exercise 0.4b** — Wire the hooks: `pip install pre-commit`, save the config above as `.pre-commit-config.yaml`, run `pre-commit install` (in a real project, pre-commit itself would join the dev extra).
```bash
pre-commit run --all-files   # pass: every hook reports Passed, exit 0
```

## 0.5 Conventions that signal seniority

A README that gets a stranger running in a minute, a `.gitignore` that excludes everything regenerable, and a CHANGELOG (Keep a Changelog format, written for consumers, not committers) separate a *project* from a pile of files. This repo's `.gitignore`, verbatim — every entry is rebuildable from source, which is exactly the test for belonging in it:

```text
.venv/
__pycache__/
*.egg-info/
.mypy_cache/
.pytest_cache/
.ruff_cache/
```

```python
# Semantic versioning: MAJOR.MINOR.PATCH = breaking change / new feature / bugfix.
# A leading 0 (this repo: 0.1.0) means "no stability contract yet".
# Declared in [project].version — and duplicated here into crash_course.__version__,
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
# Not in this repo's pyproject.toml — the shape you add when a package ships a CLI:
[project.scripts]
crash-course = "crash_course.cli:main"   # install generates a `crash-course` command that calls main()
```

**Exercise 0.5** — The version is declared in two places in this repo (0.2 and the package). Prove they agree, mechanically.
```python
import tomllib

import crash_course

def versions_match() -> bool:
    # compare crash_course.__version__ with [project].version in pyproject.toml
    # hint: tomllib.load needs "rb"; the key path is ["project"]["version"]
    ...

assert versions_match()
```

### How to work through this efficiently
Run every command against this repo as you read — nothing in this part is hypothetical, so for each quoted config, open the real file and find it. Do the break-and-revert drill in 0.4a slowly once: knowing *which* gate catches *what* is precisely what lets you trust a green run later. Chapters 14, 15, and 18 drill this material with exercises — when you get there, reference back here rather than re-deriving. Part 0 is done when `ruff check . && mypy src && pytest` exits 0 and your pre-commit hook blocks a deliberately bad commit.
