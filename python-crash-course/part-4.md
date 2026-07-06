# Part IV — Structuring Real Projects (Chapters 13–16)

Work from the workbook root (`python-crash-course/`, venv active — 0.3): chapters 14–15 drill the real Part 0 project, not toy examples. Asserts stay the acceptance tests; in chapter 16 they inspect *captured log records* via a list handler, never printed output.

## Chapter 13 — Errors & Exceptions

### 13.1 The hierarchy: catch families, catch narrowly

```python
# BaseException
#  └── Exception             <- catch at or below here; KeyboardInterrupt/SystemExit sit ABOVE on purpose
#       ├── LookupError      <- parent of KeyError AND IndexError
#       ├── ValueError, TypeError, OSError ...
try:
    port = int(cfg["port"])
except (KeyError, ValueError):   # exactly the failures that mean "expected miss" (6.1)
    port = 8080
```
A bare `except:` or `except Exception:` converts real bugs into silence — catch the narrowest class that means "expected". The hierarchy lets you catch a *family* through its common ancestor.

**Exercise 13.1** — One handler for two container types.
```python
def lookup(data, key_or_index, default=None):
    # data is a dict OR a list; an absent key / out-of-range index returns default
    # hint: ONE except clause — the common ancestor of KeyError and IndexError
    ...

assert lookup({"a": 1}, "a") == 1
assert lookup({"a": 1}, "b", default=0) == 0
assert lookup([10, 20], 1) == 20
assert lookup([10, 20], 5, default=-1) == -1
```

### 13.2 Custom exceptions: your own hierarchy

```python
class ConfigError(Exception):
    """Base for everything this package raises."""      # a docstring body is enough

class MissingKeyError(ConfigError):
    def __init__(self, key: str):
        super().__init__(f"missing config key: {key}")
        self.key = key                # carry DATA for handlers, not just a message
```
Give a package one base exception so callers can write `except ConfigError:` and mean "anything yours". Subclass a builtin (`ValueError`) when existing handlers should keep working.

**Exercise 13.2** — An exception that carries its evidence.
```python
# define InvalidUnitError(ValueError) carrying .unit, and convert(value, unit):
# "km" -> meters (x1000), "cm" -> meters (/100); any other unit raises InvalidUnitError
...

assert convert(2, "km") == 2000.0
assert convert(50, "cm") == 0.5
try:
    convert(1, "mi")
except InvalidUnitError as e:
    assert e.unit == "mi"
assert isinstance(InvalidUnitError("x"), ValueError)   # slots into the builtin hierarchy
```

### 13.3 `try` shape: keep the guarded region minimal

```python
def load(path):
    try:
        fh = open(path)              # ONLY the risky call lives inside try
    except FileNotFoundError:
        return {}
    else:
        with fh:                     # else runs only when try succeeded — the success path stays visible
            return parse(fh.read())
```
A fat `try` block is the EAFP anti-pattern: you can no longer say which line you meant to guard, and unrelated bugs get swallowed by the handler. `else` keeps success code outside the guarded region.

**Exercise 13.3** — Absence is data; every other failure propagates.
```python
from pathlib import Path

def first_line(path: str) -> str | None:
    # None when the file doesn't exist; any OTHER OSError must propagate
    # hint: except FileNotFoundError only; read inside else/with
    ...

p = Path("scratch_13.txt")
p.write_text("alpha\nbeta\n")
assert first_line("scratch_13.txt") == "alpha"
assert first_line("no_such_file.txt") is None
p.unlink()
```

### 13.4 Chaining: translate at boundaries with `raise ... from`

```python
import json

try:
    cfg = json.loads(text)
except json.JSONDecodeError as exc:
    raise ConfigError("config is not valid JSON") from exc   # cause preserved as __cause__
# bare `raise` inside except re-raises unchanged; `from None` hides the cause — only for pure noise
```
At an API boundary, translate low-level exceptions into your domain's so callers depend on your contract, not your internals. `from` keeps the original traceback attached for whoever debugs it.

**Exercise 13.4** — Prove the chain survives.
```python
import json

# define ConfigError(Exception) and load_config(text: str) -> dict that parses JSON,
# raising ConfigError chained FROM the original decode error
...

assert load_config('{"a": 1}') == {"a": 1}
try:
    load_config("{oops")
except ConfigError as e:
    assert isinstance(e.__cause__, json.JSONDecodeError)   # the chain survived translation
```

## Chapter 14 — Modules, Packages & Layout

### 14.1 Imports run once: the module cache

```python
import json                     # module object created on FIRST import, cached in sys.modules
import sys

"json" in sys.modules           # True — a second `import json` is a dict lookup, not a re-run
from json import loads          # binds ONE name here; the module still loaded fully
# from .utils import helper    # relative form — only meaningful INSIDE a package
```
Import caching is why module-level code executes exactly once per process — and why module-level mutable state behaves as a singleton. Prefer absolute imports; keep relative ones for intra-package siblings.

**Exercise 14.1** — Interrogate the cache directly.
```python
import sys

def is_cached(name: str) -> bool:
    # True if the module has already been imported by THIS process
    # hint: sys.modules is just a dict (3.2)
    ...

import csv
assert is_cached("csv")
assert not is_cached("wave")     # stdlib module nothing here imports
```

### 14.2 `__init__.py`: the package's front door

```python
# pkg/__init__.py runs on first import of pkg — keep it LIGHT; heavy imports here tax every user
# re-export the public API so callers never deep-import:
#     from .engine import run
#     __all__ = ["run"]        # what `from pkg import *` exposes; doubles as the documented API
```
This repo's `src/crash_course/__init__.py` (tree in 0.1) holds only `__version__` — the light-init rule applied. Callers should import from the package, never from its internal modules.

**Exercise 14.2** — Wire a front door. In a scratch directory:
```bash
mkdir -p shoputils
printf 'def total(prices):\n    return sum(prices)\n' > shoputils/cart.py
# now write shoputils/__init__.py so the import below works WITHOUT touching .cart:
python -c "from shoputils import total; print(total([1, 2]))"   # pass: prints 3
```

### 14.3 src layout, drilled

```python
import crash_course

crash_course.__file__     # must point into src/ via the editable install — 0.1's shadowing argument
```
Part 0 (0.1) explained *why* src layout exists; now reproduce the trap it prevents, once, so you recognize it in flat-layout repos.

**Exercise 14.3** — Build the shadow, watch it win, explain it.
```bash
python -c "import crash_course; print(crash_course.__file__)"   # 1) note the src/ path
mkdir -p /tmp/flat/crash_course && touch /tmp/flat/crash_course/__init__.py
cd /tmp/flat && python -c "import crash_course; print(crash_course.__file__)"
# 2) predict before running step 2's print: which crash_course wins, and why?
# 3) write the one-line why (hint: what is sys.path[0] for a script/-c run?)
cd - && rm -rf /tmp/flat
```

### 14.4 Namespace packages: the silent kind

```python
import crash_course

crash_course.__file__ is not None    # regular package: __init__.py exists (kinds defined in 0.5)
# a directory WITHOUT __init__.py still imports — as a NAMESPACE package with __file__ == None,
# so a forgotten __init__.py never errors; it silently changes the package's kind
```
0.5 defined the three kinds; the operational skill is *detecting* which one you actually shipped when imports behave strangely.

**Exercise 14.4** — A detector, plus a live specimen.
```python
import json
import sys
from pathlib import Path

def is_namespace_pkg(mod) -> bool:
    # True for namespace packages
    # hint: they are the ones with no __file__
    ...

Path("ns_demo").mkdir(exist_ok=True)     # a dir with NO __init__.py
sys.path.insert(0, ".")
import ns_demo
assert is_namespace_pkg(ns_demo)
assert not is_namespace_pkg(json)
Path("ns_demo").rmdir()
```

## Chapter 15 — Dependency & Environment Management

### 15.1 Know which interpreter is running

```python
import sys

sys.executable                     # the exact binary running you — log it when an env misbehaves
sys.prefix != sys.base_prefix      # True INSIDE a venv (0.3) — the programmatic activation check
```
The first question in any "works on my machine" incident is *which Python and which site-packages* — both answers live in `sys`.

**Exercise 15.1** — Guard code that must never run outside a venv.
```python
import sys

def in_venv() -> bool:
    # hint: compare the two prefixes from the snippet above
    ...

assert in_venv()          # run inside the workbook venv from 0.3
```

### 15.2 Dependency specifiers: what the strings mean

```python
# PEP 508 specifiers — the strings inside [project] dependencies (0.2):
# "requests>=2.31"               floor only — the library default (0.3): stay wide
# "urllib3>=2,<3"                floor + ceiling, guarding a known break
# "fastapi[standard]"            someone else's extra, pulled in transitively
# "tomli; python_version<'3.11'" environment marker — installed conditionally
```
Every constraint you add is a promise about compatibility you usually haven't tested — default to floors, add ceilings only for known breakage.

**Exercise 15.2** — Split a specifier into name and constraint.
```python
def parse_specifier(spec: str) -> tuple[str, str]:
    # "requests>=2.31" -> ("requests", ">=2.31"); bare "black" -> ("black", "")
    # hint: find the first character in "<>=!~" (7.3's 2-arg next), then slice (2.3)
    ...

assert parse_specifier("requests>=2.31") == ("requests", ">=2.31")
assert parse_specifier("black") == ("black", "")
assert parse_specifier("urllib3>=2,<3") == ("urllib3", ">=2,<3")
```

### 15.3 Lockfiles: trust, then verify

```bash
python -m pip freeze > requirements.lock     # the application rule from 0.3, applied
python -m pip install -r requirements.lock   # replay elsewhere; drift = quiet breakage later
```

**Exercise 15.3** — A drift detector for CI.
```python
def lock_drift(lock_lines: list[str], installed: dict[str, str]) -> list[str]:
    # lock lines look like "ruff==0.5.0"; return names whose installed version
    # differs OR that are missing entirely, in lock order
    # hint: split on "=="; dict .get (3.2)
    ...

assert lock_drift(["ruff==0.5.0", "mypy==1.10.0"], {"ruff": "0.5.0", "mypy": "1.8.0"}) == ["mypy"]
assert lock_drift(["pytest==8.0.0"], {}) == ["pytest"]
assert lock_drift(["ruff==0.5.0"], {"ruff": "0.5.0"}) == []
```

### 15.4 What actually ships: wheels

```bash
python -m pip install build && python -m build    # -> dist/*.tar.gz (sdist) + dist/*.whl (wheel)
# the wheel filename encodes its compatibility contract:
#   crash_course-0.1.0-py3-none-any.whl
#   name        version python abi  platform      ("any" = pure Python, runs everywhere)
```
`pip install` prefers a wheel (pre-built, fast) and falls back to building the sdist. Your `[build-system]` from 0.2 is what makes that build possible on a stranger's machine.

**Exercise 15.4** — Read a wheel's contract from its name.
```python
def wheel_parts(filename: str) -> dict[str, str]:
    # "crash_course-0.1.0-py3-none-any.whl" -> {"name": ..., "version": ...,
    #  "python": "py3", "abi": "none", "platform": "any"}
    # hint: removesuffix, then split on "-" and zip with the five field names (6.3)
    ...

assert wheel_parts("crash_course-0.1.0-py3-none-any.whl") == {
    "name": "crash_course", "version": "0.1.0",
    "python": "py3", "abi": "none", "platform": "any",
}
```

## Chapter 16 — Logging & Debugging

### 16.1 Loggers done right

```python
import logging

logger = logging.getLogger(__name__)     # ONE module-level logger, named after the module

def transfer(amount: int) -> None:
    logger.info("transferring %s", amount)   # %s + args — NOT an f-string: formatting is deferred
```
`__name__` loggers form a dotted tree mirroring your packages, so an app can dial one subsystem up or down. Deferred `%s` formatting means a suppressed level costs almost nothing — an f-string pays up front every call.

**Exercise 16.1** — Assert on records, not output.
```python
import logging

class ListHandler(logging.Handler):          # the caplog pattern: records land in a plain list
    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []
    def emit(self, record):
        self.records.append(record)

def audit(logger: logging.Logger, user: str, action: str) -> None:
    # emit exactly one INFO record "user=%s action=%s" with DEFERRED args
    ...

log = logging.getLogger("part4.audit")
log.setLevel(logging.INFO)
h = ListHandler()
log.addHandler(h)
audit(log, "jj", "login")
assert len(h.records) == 1
assert h.records[0].levelno == logging.INFO
assert h.records[0].getMessage() == "user=jj action=login"
assert h.records[0].args == ("jj", "login")     # proof the formatting was deferred
```

### 16.2 Levels, configuration, and `logger.exception`

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
# configure ONCE, at the application entry point — libraries never call basicConfig

logging.getLogger("app.db")        # dotted children propagate UP to "app"'s handlers
# levels: DEBUG < INFO < WARNING < ERROR < CRITICAL; below-threshold calls are near-free (16.1)
```
Inside an `except` block, `logger.exception(...)` logs at ERROR *and* attaches the full traceback — the difference between a searchable incident and a mystery string.

**Exercise 16.2** — Failure with the traceback attached.
```python
import logging

# reuse ListHandler from 16.1
def notify_failure(logger: logging.Logger, job: str) -> None:
    # called from inside an except block: one ERROR record naming the job, traceback attached
    # hint: a single logger method does both — no traceback module needed
    ...

log = logging.getLogger("part4.jobs")
h = ListHandler()
log.addHandler(h)
try:
    raise TimeoutError("worker 3")
except TimeoutError:
    notify_failure(log, "nightly-sync")
assert h.records[0].levelno == logging.ERROR
assert h.records[0].exc_info is not None           # the traceback rode along, unstringified
assert "nightly-sync" in h.records[0].getMessage()
```

### 16.3 Structured logs: fields, not prose

```python
import logging

logger = logging.getLogger(__name__)
logger.info("payment ok", extra={"order_id": 42})   # extra={} becomes ATTRIBUTES on the record
# a JSON/key=value formatter then emits machine-parseable lines that aggregators can
# index and filter — prose-only messages can merely be grepped
```
Log *fields* for anything a human or machine will later filter by (ids, durations, counts); keep the message itself a stable, searchable constant.

**Exercise 16.3** — An event logger with attached fields.
```python
import logging

# reuse ListHandler from 16.1
def log_event(logger: logging.Logger, name: str, **fields) -> None:
    # one INFO record whose message is `name`, with every field as a record attribute
    # hint: you already hold the dict extra= wants (5.1)
    ...

log = logging.getLogger("part4.events")
log.setLevel(logging.INFO)
h = ListHandler()
log.addHandler(h)
log_event(log, "checkout", order_id=7, cents=250)
rec = h.records[0]
assert rec.getMessage() == "checkout"
assert rec.order_id == 7 and rec.cents == 250
```

### 16.4 `pdb`: the debugger you always have

```python
def buggy(order: dict[str, int]) -> int:
    total = sum(order.values())
    breakpoint()               # pauses HERE in pdb; PYTHONBREAKPOINT=0 disables them all
    return total
# survival kit: n(ext) · s(tep in) · c(ontinue) · l(ist) · p expr · pp expr · w(here) · b line · q(uit)
# post-mortem on a crash: python -m pdb -c continue script.py
```
`breakpoint()` beats print-debugging the moment you'd need a second print: you inspect *any* variable at the frozen frame, walk the stack with `w`, and move up/down it with `u`/`d`.

**Exercise 16.4** — A guided session, on code you already own:
```bash
# 1) paste your 4.3 first_prime_over into scratch_16.py; add breakpoint() inside the INNER loop
# 2) run: python scratch_16.py  — at the (Pdb) prompt try: p candidate, p d, w, n, c
# 3) predict what w(here) shows for the inner loop vs after moving the breakpoint
#    to the outer loop; confirm, then write the one-line difference as a comment
# 4) remove the breakpoint; the file must run silent again
```

### How to work through this efficiently
Chapter 13 is one habit: guard the narrowest region with the narrowest class, and translate with `from` at boundaries — the asserts on `__cause__` and `.unit` check the habit, not trivia. Chapters 14–15 drill what Part 0 defined: when stuck, reread the cited section (0.1, 0.2, 0.3, 0.5) rather than re-deriving; run every bash drill for real, especially 14.3's shadowing trap. In chapter 16, the `ListHandler` is the point — asserting on records is exactly what pytest's `caplog` does in chapter 17, so you're building the testing reflex one part early. Finish by running 16.4's pdb session slowly; ten minutes of deliberate stepping pays for itself the first time production misbehaves.
