# Part V — Engineering Practices (Chapters 17–20)

Work in one scratch file per chapter (`scratch_17.py` …), venv active. Asserts stay the acceptance tests — with two twists: chapter 17's acceptance is `pytest -q scratch_17.py` reporting green, and chapters 19–20 assert on *ordering and operation counts*, never on wall-clock time.

## Chapter 17 — Testing

### 17.1 pytest: plain functions, plain asserts

```python
# test_calc.py — pytest discovers test_*.py files and test_* functions; no TestCase classes
import pytest

def test_add():
    assert add(2, 2) == 4              # on failure pytest shows BOTH sides (assertion rewriting)

def test_add_rejects_strings():
    with pytest.raises(TypeError):     # passes ONLY if the block raises exactly this family
        add("2", 2)
```
A test is arrange–act–assert, one behavior each, named for the behavior (`test_add_rejects_strings` reads as a spec line). Run `pytest -q` and let the failure output do the debugging.

**Exercise 17.1** — The code is done; write the tests.
```python
import pytest

def slug(text: str) -> str:                 # code under test — given, don't edit
    if not text.strip():
        raise ValueError("empty text")
    return "-".join(text.lower().split())

assert slug("Hello World") == "hello-world"   # the contract, inline — now express it as tests:

def test_slug_lowercases_and_dashes():
    ...   # hint: one assert per behavior beats one mega-assert

def test_slug_empty_raises():
    ...   # hint: with pytest.raises(ValueError)

# acceptance: `pytest -q scratch_17.py` reports 2 passed
```

### 17.2 Fixtures: arrange once, inject by name

```python
import pytest

@pytest.fixture
def cart():
    return ["apple", "bread"]     # a FRESH value per test — tests must never share state

def test_count(cart):             # the parameter name requests the fixture; pytest injects it
    assert len(cart) == 2

# built-ins you'll use weekly: tmp_path (fresh real directory), caplog (16.1's ListHandler,
# built in), monkeypatch (17.4), capsys — no imports needed, just name them
```
A yield inside a fixture splits setup from teardown exactly like 8.4's `@contextmanager` — teardown runs even when the test fails. Anything two tests both arrange belongs in a fixture.

**Exercise 17.2** — Arrange in a fixture, then make the tests pass.
```python
import pytest
from pathlib import Path

@pytest.fixture
def note_dir(tmp_path):
    (tmp_path / "a.txt").write_text("old")     # arrange ONCE, here
    return tmp_path

def test_replaces(note_dir):
    rotate(note_dir, "a.txt", "new")
    assert (note_dir / "a.txt").read_text() == "new"

def test_keeps_backup(note_dir):
    rotate(note_dir, "a.txt", "new")
    assert (note_dir / "a.txt.bak").read_text() == "old"

def rotate(directory: Path, name: str, text: str) -> None:
    # replace the note's content, saving the previous content to <name>.bak first
    # hint: read_text before you overwrite; write the .bak sibling
    ...

# acceptance: pytest -q scratch_17.py -> both pass, each with a fresh note_dir
```

### 17.3 Parametrization: one test, a table of cases

```python
import pytest

@pytest.mark.parametrize(("raw", "expected"), [
    ("1.5", 1.5),
    ("2e3", 2000.0),
    ("-4", -4.0),
])
def test_parse(raw, expected):
    assert float(raw) == expected      # ONE function, three independently reported cases
```
Each row fails independently with its inputs in the test id — copy-pasted near-identical tests are the smell this removes. Parametrize inputs, never the assertions.

**Exercise 17.3** — The table is the spec; implement to it.
```python
import pytest

@pytest.mark.parametrize(("text", "expected"), [
    ("2+3", 5),
    ("10-4", 6),
    (" 7 + 1 ", 8),
])
def test_calc(text, expected):
    assert calc(text) == expected

def calc(text: str) -> int:
    # a two-operand calculator for + and -
    # hint: str.partition on the operator; int() shrugs at surrounding spaces
    ...

# acceptance: pytest -q scratch_17.py -> 3 passed
```

### 17.4 Mocking: replace the unpredictable

```python
def get_rate() -> float: ...           # imagine: a slow, flaky network call

def convert(usd: float) -> float:
    return usd * get_rate()

def test_convert(monkeypatch):
    monkeypatch.setattr("scratch_17.get_rate", lambda: 2.0)   # swapped by NAME, auto-undone
    assert convert(3.0) == 6.0
# patch where the name is LOOKED UP (the using module), not where it's defined — the classic trap
```
Mock only at your system's edges — network, clock, randomness, filesystem you don't own; mocking your own logic tests the mock instead. `monkeypatch` undoes itself after each test.

**Exercise 17.4** — Pin the dice.
```python
import random

def roll() -> int:
    return random.randint(1, 6)        # nondeterministic — untestable as-is

assert 1 <= roll() <= 6                # the un-pinned contract: range only

def test_roll_pinned(monkeypatch):
    # force randint to produce 6, then assert roll() == 6 exactly
    # hint: monkeypatch.setattr on the random module; a lambda swallowing both args (5.1)
    ...

# acceptance: pytest -q scratch_17.py passes — no real randomness left inside the test
```

### 17.5 TDD and coverage: the loop and its blind spots

```bash
python -m pip install coverage
coverage run -m pytest && coverage report -m    # -m lists the exact MISSED lines
# chase untested BRANCHES, not the percentage — 100% covered can still be 100% wrong
```
The TDD loop is red (write the failing test first) → green (minimal code) → refactor (tests stay green). Coverage's job is only to show which branches your loop never visited.

**Exercise 17.5** — One function, test-driven, by hand.
```python
# red: write test_pluralize cases FIRST for the three rules the asserts encode
# green: implement pluralize minimally until pytest passes
# refactor: remove duplication; the tests must stay green
def pluralize(noun: str) -> str:
    # hint: str.endswith — it also accepts a TUPLE of suffixes
    ...

assert pluralize("cat") == "cats"
assert pluralize("bus") == "buses"
assert pluralize("sky") == "skies"
```

## Chapter 18 — Code Quality & Tooling

### 18.1 Formatters: end the whitespace debate

```bash
ruff format .            # rewrites in place, per 0.2's [tool.ruff] line-length — no opinions left
ruff format --check .    # CI mode: exit 1 if anything WOULD change; touches nothing
```
A formatter's value is that its output is *nobody's* style, so review comments about layout disappear. Format on save or in the pre-commit hook (0.4) — never by hand.

**Exercise 18.1** — Prove idempotence to yourself.
```bash
# 1) paste your 17.5 pluralize into fmt_demo.py, then mangle it: odd indentation,
#    single-space around operators, one 150-char line (keep it VALID python)
ruff format --check fmt_demo.py; echo $?     # 2) predict the exit code, then look
ruff format fmt_demo.py && ruff format --check fmt_demo.py; echo $?   # 3) predict again
# 4) run step 3 twice more — formatting formatted code must change nothing
```

### 18.2 Linters catch bugs, not just style

```python
# what 0.4's select = ["E", "F", "I", "UP", "B"] buys, in bug terms:
x = undefined_name           # F821 — a NameError caught BEFORE runtime
def f(items=[]): ...         # B006 — 5.3's mutable default, mechanized
from typing import List      # UP035 — 12.1's legacy-generics rule, enforced
```
Every `# noqa` suppression is borrowed technical debt with the rule code as the IOU. Prefer fixing; suppress only with a written reason.

**Exercise 18.2** — Audit the debt markers.
```python
def noqa_lines(source: str) -> list[int]:
    # 1-based line numbers of every line carrying a "# noqa" suppression
    # hint: enumerate(splitlines(), start=1) (6.3) inside a comprehension
    ...

assert noqa_lines("x = 1\ny = bad()  # noqa: F821\n") == [2]
assert noqa_lines("clean = True\n") == []
assert noqa_lines("a = 1  # noqa\nb = 2  # noqa: E501\n") == [1, 2]
```

### 18.3 pre-commit and CI: the same gate, twice

```bash
pre-commit run --all-files       # 0.4's hook, on demand — the fast local mirror
# CI re-runs the SAME commands (ruff check, mypy src, pytest) as enforcement;
# if the hook and CI ever drift, "passed locally" stops meaning anything
```
The local hook exists for speed, CI for authority — one set of commands, two trigger points. Any check too slow for the hook (full test suite) still belongs in CI.

**Exercise 18.3** — A tiny gate-runner, like CI does it.
```python
import subprocess

def gate(cmds: list[list[str]]) -> list[str]:
    # run every command (never stop early); return argv[0] of each FAILURE, in order
    # hint: subprocess.run(...).returncode; nonzero means failed
    ...

assert gate([["true"], ["false"], ["true"]]) == ["false"]
assert gate([["false"], ["false"]]) == ["false", "false"]
assert gate([["true"]]) == []
```

## Chapter 19 — Concurrency & Parallelism

### 19.1 The decision table (and the GIL)

```python
# the GIL: one thread runs Python BYTECODE at a time — threads add no CPU throughput
# I/O-bound, many waits, async-friendly libs  -> asyncio   (one thread, cooperative)
# I/O-bound, blocking libraries               -> threads   (GIL is RELEASED during I/O)
# CPU-bound                                   -> processes (real parallelism, separate GILs)
# unsure                                      -> measure first (chapter 20)
```
Concurrency is about *waiting better*; parallelism is about *computing more* — the GIL only forbids the second for threads. Choose the model from the workload, never from habit.

**Exercise 19.1** — Encode the table so you never re-derive it.
```python
def executor_for(task: dict) -> str:
    # {"kind": "cpu"} -> "processes"; {"kind": "io", "blocking_lib": True} -> "threads";
    # {"kind": "io", "blocking_lib": False} -> "asyncio"
    # hint: match with dict patterns (1.3)
    ...

assert executor_for({"kind": "cpu"}) == "processes"
assert executor_for({"kind": "io", "blocking_lib": True}) == "threads"
assert executor_for({"kind": "io", "blocking_lib": False}) == "asyncio"
```

### 19.2 Thread pools via `concurrent.futures`

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as pool:        # the with closes the pool (8.3)
    results = list(pool.map(fetch, urls))              # RESULT order == input order,
                                                       # even when completion order differs
# swap in ProcessPoolExecutor for CPU work — same API, real parallelism
# shared mutable state across threads = races; the GIL does NOT make `n += 1` atomic
```
`pool.map` is the 80% case: same function, many inputs, order preserved. The moment threads *write* shared state you need a `Lock` — or better, a design where they don't.

**Exercise 19.2** — Prove the ordering guarantee, not the speed.
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_lengths(words: list[str]) -> list[int]:
    # len() of each word, computed across 4 worker threads
    # hint: pool.map inside the with block; materialize before the pool closes
    ...

assert parallel_lengths(["a", "bbb", "cc"]) == [1, 3, 2]   # input order, guaranteed
assert parallel_lengths([]) == []
```

### 19.3 `async`/`await` mechanics

```python
import asyncio

async def fetch(name: str) -> str:
    await asyncio.sleep(0)         # await = yield control HERE; the loop runs others meanwhile
    return name

asyncio.run(fetch("a"))            # the one entry point: builds, runs, and closes the loop
# fetch("a") alone creates a coroutine object and runs NOTHING — 7.2's laziness again
```
`async def` functions are cooperative: they only give up control at an `await`, so one blocking call (`time.sleep`, requests) freezes every task on the loop. Async all the way down, or not at all.

**Exercise 19.3** — Minimal mechanics, no clock.
```python
import asyncio

async def shout(word: str) -> str:
    # yield control once (a zero sleep), then return the word uppercased
    ...

assert asyncio.run(shout("hi")) == "HI"
```

### 19.4 `gather`: run tasks concurrently

```python
import asyncio

async def main() -> tuple[str, str]:
    a, b = await asyncio.gather(job("a"), job("b"))   # starts BOTH; results in ARGUMENT order
    return a, b
# to see the interleaving itself, log events to a list — order of appends is the evidence
```
`gather` is how independent awaits actually overlap — sequential `await job("a")` then `await job("b")` never interleaves. Assert on the event order, not on elapsed time.

**Exercise 19.4** — Make the interleaving visible, then assert it.
```python
import asyncio

async def worker(name: str, log: list[str]) -> None:
    # append f"{name}:start", yield control once (zero sleep), append f"{name}:end"
    ...

async def run_two(log: list[str]) -> None:
    # run worker("a") and worker("b") CONCURRENTLY
    # hint: asyncio.gather
    ...

log: list[str] = []
asyncio.run(run_two(log))
assert log == ["a:start", "b:start", "a:end", "b:end"]   # interleaved; sequential would read a,a,b,b
```

## Chapter 20 — Performance & Profiling

### 20.1 Measure first — and count, don't clock

```bash
python -m timeit -s "s = set(range(1000))" "999 in s"    # micro: one expression, sane repetition
python -m cProfile -s cumulative script.py                # macro: where the time actually went
# no optimization without a measurement AND a target; wall-clock varies per machine —
# OPERATION COUNTS don't, which is why this chapter's asserts count instead of time
```

**Exercise 20.1** — Instrument the work itself.
```python
def linear_search(xs: list[int], target: int) -> tuple[bool, int]:
    # return (found, comparisons_made) — count every element examined
    # hint: enumerate the scan; return as soon as you hit
    ...

assert linear_search([5, 3, 9], 9) == (True, 3)
assert linear_search([5, 3, 9], 5) == (True, 1)
assert linear_search([5, 3, 9], 1) == (False, 3)
```

### 20.2 Complexity: the data structure is the algorithm

```python
# 3.1's table, priced:   x in list -> O(n) scan        x in set -> O(1) hash
# list.append -> O(1) amortized;  list.insert(0, x) -> O(n);  deque.appendleft -> O(1) (3.3)
# sorted(xs) -> O(n log n);  heapq.nsmallest(k, xs) -> O(n log k) when k << n
```
Most "slow Python" is an O(n) container operation inside an O(n) loop — a data-structure bug, not a language problem. Fix the structure before reaching for anything exotic.

**Exercise 20.2** — See the quadratic, without a stopwatch.
```python
def dedupe_ops(items: list[int]) -> tuple[list[int], int]:
    # order-preserving dedupe with `seen` as a LIST; count one operation per element
    # the scan examines (a miss examines all of seen; a hit stops at the match)
    ...

def dedupe_ops_set(items: list[int]) -> tuple[list[int], int]:
    # same result with `seen` as a SET; each membership test counts as ONE operation
    ...

xs = list(range(100)) * 2
assert dedupe_ops(xs)[0] == dedupe_ops_set(xs)[0] == list(range(100))
set_ops = dedupe_ops_set(xs)[1]
assert set_ops == len(xs)                        # one probe per item — linear
assert dedupe_ops(xs)[1] > 40 * set_ops          # the quadratic, visible as a count
```

### 20.3 Reading a profile

```bash
python -m cProfile -s cumulative script.py | head -20
# tottime = the function's OWN work; cumtime = own + everything it called
# sort by cumulative to find the guilty caller, by tottime to find the guilty code
```
Optimize the top line, re-profile, repeat — the second hotspot usually moves after you fix the first. A profile that surprises you is the measurement paying for itself.

**Exercise 20.3** — Rank the hotspots.
```python
def hotspots(rows: list[tuple[str, int, float]], top: int) -> list[str]:
    # rows are (func_name, ncalls, tottime); return the `top` names by tottime, descending
    # hint: sorted with a key lambda and reverse=True; then slice
    ...

assert hotspots([("parse", 10, 0.5), ("io", 2, 1.5), ("fmt", 90, 0.1)], 2) == ["io", "parse"]
assert hotspots([("a", 1, 0.2)], 5) == ["a"]
```

### 20.4 Caching: trade memory for repeated work

```python
from functools import lru_cache

@lru_cache(maxsize=None)              # 8.2's decorator, worn as a performance tool
def score(board: str) -> int: ...

score.cache_info()                    # CacheInfo(hits=…, misses=…) — a built-in op-counter
# cache only PURE functions (same args -> same result); a stale cache is a new bug class
```
Memoization turns overlapping recursion from exponential to linear — the biggest constant-effort win in this chapter. `cache_info()` gives you the operation counts to prove it.

**Exercise 20.4** — Exponential to linear, proven by count.
```python
from functools import cache

calls = 0

# define fib(n): naive two-branch recursion, memoized, incrementing `calls`
# once per REAL body execution
# hint: @cache on top; global (5.4's rebinding rule, module scope)
...

assert fib(20) == 6765
assert calls == 21          # one execution per distinct n — un-memoized it would be 21891
```

### How to work through this efficiently
Chapter 17 inverts the workbook once per exercise: sometimes the code is given and the tests are the deliverable, sometimes the table of cases is given and the implementation is — read which way each one points before typing, and let `pytest -q` be the judge. Chapter 18's drills only pay off run against your real scratch files, so use them, not toy input. In chapters 19–20 the discipline is the same: never claim "concurrent" or "faster" from feel — 19.4's event log and 20.2's operation counts are the shape of evidence that survives code review, and they are exactly what the asserts demand.
