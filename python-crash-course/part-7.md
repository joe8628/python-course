# Part VII — Closing the Loop for the Job Hunt (Chapters 25–28)

Work in a scratch file per chapter, venv active. Asserts remain the acceptance tests wherever they appear; chapters 25 and 27 add design/review exercises whose acceptance criteria live in their docstrings instead, and chapter 28 swaps asserts for the self-check commands (`pytest`, `ruff`, `mypy`) a real repo would gate on.

## Chapter 25 — System & Code Design Exercises

### 25.1 Make illegal states unrepresentable

```python
from dataclasses import dataclass
from enum import Enum

class State(Enum):                 # a closed set — no stringly-typed "paidd" ever compiles
    PENDING = "pending"
    PAID = "paid"

@dataclass(frozen=True)
class Order:
    id: int
    state: State                   # the type now enforces what a comment used to beg for
```
Design rounds reward types that make the invalid impossible over validation sprinkled through methods — ch 11's tools, applied as a design stance.

**Exercise 25.1** — Encode a lifecycle so wrong moves can't happen silently.
```python
from enum import Enum

class State(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"

def advance(state: State) -> State:
    # PENDING -> PAID -> SHIPPED; SHIPPED is terminal -> raise ValueError
    # hint: match (ch 1) or a dict transition table
    ...

assert advance(State.PENDING) is State.PAID
assert advance(State.PAID) is State.SHIPPED
try:
    advance(State.SHIPPED)
    moved = True
except ValueError:
    moved = False
assert not moved
```

### 25.2 Inject what you can't control

```python
import time

def make_stamp(clock=time.time) -> int:   # default is production; tests pass a fake
    return int(clock())                    # deterministic tests need deterministic inputs
```
Any design that reads the wall clock, randomness, or the network inline is untestable by construction — parameterize the edge (ch 22's `Depends` idea, no framework required).

**Exercise 25.2** — A rate limiter you can test without sleeping.
```python
class RateLimiter:
    # allow at most `limit` calls per `window` seconds, as measured by `clock`
    def __init__(self, limit: int, window: float, clock) -> None:
        ...

    def allow(self) -> bool:
        # hint: keep call timestamps; drop the ones older than window, then decide
        ...

now = [100.0]
rl = RateLimiter(2, 60.0, clock=lambda: now[0])
assert rl.allow() and rl.allow()
assert not rl.allow()               # limit hit inside the window
now[0] += 61                        # time travel — no sleep() in tests, ever (ch 19's rule)
assert rl.allow()
```

### 25.3 The structure IS the design

```python
# "recent items, evict oldest"  -> deque(maxlen)   (ch 3's ring buffer)
# "fast membership at scale"    -> set / dict      O(1) vs a list's O(n) scan
# "ordered + unique + lookup"   -> dict (3.7+)     one structure, all three properties
```
State the access pattern first, then name the structure — that sentence order is what interviewers listen for (ch 20's measure-first discipline, applied before the code exists).

**Exercise 25.3** — An LRU cache: the classic access-pattern question.
```python
class LRUCache:
    # capacity-bounded mapping; reading a key refreshes it, inserting past
    # capacity evicts the least recently used key
    def __init__(self, capacity: int) -> None:
        ...

    def get(self, key: str) -> int | None:
        # hint: dicts are ordered — delete + reinsert refreshes; or OrderedDict.move_to_end
        ...

    def put(self, key: str, value: int) -> None:
        ...

cache = LRUCache(2)
cache.put("a", 1)
cache.put("b", 2)
assert cache.get("a") == 1
cache.put("c", 3)                   # evicts "b" — "a" was refreshed by the get
assert cache.get("b") is None
assert cache.get("a") == 1 and cache.get("c") == 3
```

### 25.4 Design review: the four questions

```python
# a design review asks, in order:
# 1. what breaks first under 10x load?              (bottleneck)
# 2. what happens when a dependency fails?          (failure mode)
# 3. what can't be tested without the real thing?   (seams — 25.2)
# 4. which decision is expensive to reverse?        (one-way doors)
```

**Exercise 25.4** — Rewrite this design (prose deliverable, no code).
```text
Design under review — "notification service v1":
- one Service object owns: template rendering, user preference lookup,
  SMTP sending, retry logic, and delivery metrics
- sends synchronously inside the web request handler
- retries forever on failure
- SMTP host and credentials are hardcoded attributes
```
```python
"""Acceptance criteria for your rewrite (bullet points in a scratch .md):

- names at least 3 separate components, one responsibility sentence each (ch 23)
- moves sending out of the request path and says what replaces it
- states a bounded retry policy and where failures go when it's exhausted
- says where the credentials live instead (ch 24.3)
"""
# refactor the DESIGN, not code — apply the four questions above to v1 first
```

## Chapter 26 — Coding Challenge Patterns

### 26.1 Hash-map first

```python
from collections import Counter

Counter("abracadabra").most_common(2)   # [('a', 5), ('b', 2)] — the tally pattern in one call
# anagram test: Counter(a) == Counter(b) — O(n), no sorting needed
```
When a challenge says "count", "duplicate", "anagram", or "seen before", the answer starts with a dict or Counter (ch 3) — reach for it before any nested loop.

**Exercise 26.1** — First non-repeating character.
```python
def first_unique(s: str) -> str | None:
    # hint: one Counter pass, then one scan in the original order
    ...

assert first_unique("swiss") == "w"
assert first_unique("aabb") is None
```

### 26.2 Two pointers and sliding windows

```python
# two pointers: SORTED data, ends move inward       (pair-sum, container problems)
# sliding window: contiguous run + running invariant (longest/shortest-with-property)
lo, hi = 0, len(xs) - 1     # the shape: advance whichever side cannot be in a better answer
```

**Exercise 26.2a** — Pair summing to a target in a sorted list.
```python
def two_sum_sorted(xs: list[int], target: int) -> tuple[int, int] | None:
    # return the pair of VALUES that sums to target, or None
    # hint: two pointers; move the end that overshoots
    ...

assert two_sum_sorted([1, 3, 4, 7, 11], 14) == (3, 11)
assert two_sum_sorted([1, 2, 3], 100) is None
```

**Exercise 26.2b** — Longest run of distinct characters.
```python
def longest_unique(s: str) -> int:
    # length of the longest substring with no repeated character
    # hint: grow hi, shrink lo on violation; a set carries the window's invariant
    ...

assert longest_unique("abcabcbb") == 3
assert longest_unique("bbbb") == 1
assert longest_unique("") == 0
```

### 26.3 A list is the stack

```python
stack = []
stack.append("(")            # push on open
stack.pop()                  # pop on close — an empty pop or leftovers mean invalid
# nesting / matched pairs / undo -> stack, always; recursion is the same idea implicit
```

**Exercise 26.3** — Balanced brackets, all three kinds.
```python
def balanced(s: str) -> bool:
    # "([]{})" -> True, "(]" -> False; ignore non-bracket characters
    # hint: a dict mapping closers to openers + a list-as-stack
    ...

assert balanced("([]{})")
assert not balanced("(]")
assert balanced("f(x[0]) + {1}")
assert not balanced("(()")
```

### 26.4 Memoized recursion: the DP entry point

```python
# top-down dynamic programming = recursion + @cache (ch 20.4's tool, worn as a pattern):
# name the STATE, write the RECURRENCE, pin the BASE CASE — the decorator does the table
```

**Exercise 26.4** — Climbing stairs (the canonical warm-up).
```python
from functools import cache

def ways(n: int) -> int:
    # distinct ways to climb n steps taking 1 or 2 at a time
    # hint: fib-shaped recurrence + @cache; base cases at n <= 1
    ...

assert ways(3) == 3
assert ways(10) == 89
```

## Chapter 27 — Reading & Reviewing Code

### 27.1 Read in passes, not lines

```python
# a reading order that works under interview pressure:
# 1. signature + return type      (what does it CLAIM?)
# 2. happy path                   (does the shape match the claim?)
# 3. edges: empty, None, duplicates, boundaries
# 4. state: what mutates, what escapes  (aliasing — the ch 2 trap)
```

**Exercise 27.1** — Predict each printed value, then run to confirm; for every miss, write the one-line why (alias vs copy).
```python
a = [1, 2, 3]
b = a
b += [4]
print(a)            # ?
c = a + [5]
print(a == c)       # ?
d = {"n": 1}
e = dict(d)
e["n"] = 2
print(d["n"])       # ?
```

### 27.2 The reviewer's defect catalog

```python
def log(msg, tags=[]): ...       # mutable default: ONE list shared across calls (ch 5)
if user == None: ...             # None is a singleton — `is None` (ch 2.4)
try: risky()
except: pass                     # bare except swallows typos and Ctrl-C alike (ch 13)
```
You already know every one of these bugs from earlier parts; review skill is recognizing them in a diff at reading speed, not deriving them from scratch.

**Exercise 27.2a** — This passed review; production says otherwise. Ship the fix.
```python
# reported: "tags from unrelated requests leak into each other"
def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    # make independent calls independent; appending to a caller's list is still fine
    # hint: the None-sentinel default idiom (ch 5)
    ...

assert add_tag("a") == ["a"]
assert add_tag("b") == ["b"]                # the buggy version returns ["a", "b"] here
assert add_tag("x", ["q"]) == ["q", "x"]
```

**Exercise 27.2b** — Every callback fires with the last value. Fix the capture.
```python
# reported: [lambda: i for i in range(3)] — all three return 2 (late binding, ch 5)
def make_callbacks(n: int) -> list:
    # return n zero-arg callables; the k-th must return k
    # hint: bind at definition time — default-argument capture
    ...

cbs = make_callbacks(3)
assert [cb() for cb in cbs] == [0, 1, 2]
```

### 27.3 Review comments that land

```python
# the formula: observation -> consequence -> suggestion
# "tags=[] is shared across calls (obs); repeat callers leak state (cons);
#  use the None-sentinel idiom (sugg)" — never a bare "this is wrong"
```

**Exercise 27.3** — Write the review (prose deliverable, no asserts).
```text
# under review — utils.py (excerpt)
def load(path):
    try:
        data = json.load(open(path))
    except:
        data = None
    print("loaded", path)
    return data
```
```python
"""Acceptance criteria for your review (3 comments in a scratch .md):

- each comment follows observation -> consequence -> suggestion
- together they cover: the bare except (ch 13), the unclosed file handle
  (ch 8's with), and print-instead-of-logging (ch 16)
- at least one names the exact fixing idiom — by name, not as pasted code
"""
# a critique-and-rewrite exercise: your comments should let the author fix it unaided
```

## Chapter 28 — Capstone: a Production-Shaped Project

### 28.1 The spec — `shortlink`

```text
shortlink — a URL shortener you could defend in a system-design round.

Functional:
- POST /links {"url": ...} -> {"code": "<6 chars>"}; GET /{code} -> 307 redirect
- codes are random (injected generator — 25.2), collision-checked against storage
- CLI: `shortlink add <url>` prints the code; `shortlink stats` prints link count

Non-functional (the actual test of this part):
- src layout, pyproject-packaged, console entry point        (Part 0, ch 14-15)
- domain core imports neither sqlite3 nor fastapi            (ch 23's layers)
- fully typed: mypy --strict clean                           (ch 12)
- core tested without touching DB or HTTP; API tested via TestClient (ch 17, 22)
- structured logging at the shell, never print               (ch 16)
```
Build it in a fresh repo beside this workbook; every milestone below ends with the commands that must pass before you move on.

### 28.2 Milestone 1 — a skeleton that already gates

- [ ] `src/shortlink/` package, `tests/`, `pyproject.toml` with dev extras (Part 0's tree)
- [ ] one smoke test importing the package — bare `pytest` exits 5 on an empty suite
- [ ] ruff + mypy configured in pyproject, both clean on the skeleton

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e '.[dev]'
ruff check . && mypy src && pytest -q     # ALL green before any feature code
```

### 28.3 Milestone 2 — the pure core

- [ ] `core.py`: `Link` dataclass; `make_code(rand)` with injected randomness; URL validation that rejects junk with `ValueError`
- [ ] tests parametrized over valid/invalid URLs; a fake `rand` makes codes deterministic
- [ ] nothing in `core.py` imports sqlite3, fastapi, or logging

```bash
pytest -q tests/test_core.py && mypy --strict src
grep -rE 'import (sqlite3|fastapi)' src/shortlink/core.py && echo LEAK || echo core clean
```

### 28.4 Milestone 3 — adapters at the edges

- [ ] `storage.py`: sqlite-backed store, parameterized queries only (ch 21.4, 24.1)
- [ ] `api.py`: FastAPI app; storage arrives via `Depends` (ch 22.4) so tests can override it
- [ ] API tests: create + redirect happy path, 404 for unknown code, 422 for a bad URL

```bash
pytest -q                                 # core AND api suites, in-process
```

### 28.5 Milestone 4 — logging, entry point, CI gate

- [ ] `logging.getLogger(__name__)` per module; one structured line per request outcome (ch 16)
- [ ] `[project.scripts] shortlink = ...` entry point; `shortlink add https://example.com` works from an activated venv
- [ ] pre-commit running ruff/mypy/pytest (ch 18); a CI file that runs the same three on push

```bash
pre-commit run --all-files
shortlink add https://example.com && shortlink stats
```
Done means: a stranger can clone it, run one install command and one test command, and read the code top-down through the layers — that repo is the portfolio piece, and walking someone through it is the interview.

### How to work through this efficiently
Chapters 25 and 26 are rehearsal, not reference — do each exercise cold, out loud, stating the access pattern or the state/recurrence before typing, because narrating the choice is the skill being scored. In chapter 27 hold yourself to the pass order and the comment formula even though nothing mechanical checks prose; sloppy review habits are visible in interviews within minutes. Chapter 28 is the part that compounds: build it in milestone order, never letting a gate go red, and when it's done you have both the portfolio repo and — having built every layer yourself — the answers to the questions it will provoke.
