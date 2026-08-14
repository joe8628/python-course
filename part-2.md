# Part II — Writing Pythonic Code (Chapters 5–8)

Work in a scratch file or REPL. For every exercise, the `assert`s are the acceptance tests: your code is correct when they all pass silently. Two exercises (5.3, 5.4b) are predict-then-explain: no asserts — the deliverable is the one-line *why* you write after running them.

## Chapter 5 — Functions, Arguments & Scope

### 5.1 `*args`, `**kwargs`, and forwarding

```python
def report(*args, **kwargs):        # in a SIGNATURE the stars pack: args is a tuple, kwargs a dict
    return f"{args} {kwargs}"

report(1, 2, mode="fast")           # "(1, 2) {'mode': 'fast'}"

opts = {"retries": 3, "timeout": 1.0}
connect("db", **opts)               # at a CALL SITE the stars unpack: mapping -> keyword arguments
```
The same stars pack in a signature and unpack at a call site. Forwarding `*args, **kwargs` untouched is the backbone of every wrapper you'll write in 8.1.

**Exercise 5.1** — Write a forwarding helper that injects a default without stomping the caller's choice.
```python
def with_default_timeout(func, *args, **kwargs):
    # call func with the given arguments, adding timeout=5 ONLY if absent
    # hint: kwargs.setdefault, then forward with * and **
    ...

def fake_request(url: str, timeout: int | None = None) -> str:
    return f"{url}:{timeout}"

assert with_default_timeout(fake_request, "/a") == "/a:5"
assert with_default_timeout(fake_request, "/b", timeout=1) == "/b:1"
```

### 5.2 Keyword-only and positional-only parameters

```python
def move(src, dst, /, *, overwrite=False):   # '/' ends positional-ONLY; '*' starts keyword-ONLY
    ...

move("a.txt", "b.txt", overwrite=True)       # OK
# move("a.txt", "b.txt", True) -> TypeError — a bare boolean can't sneak in positionally
```
Keyword-only flags keep call sites self-documenting; positional-only lets you rename `src`/`dst` later without breaking callers. Both are API-design signals reviewers look for.

**Exercise 5.2** — Enforce the boundary in your own signature.
```python
def clamp(value, /, *, lo, hi):
    # return value limited to the range [lo, hi]
    # hint: nest min() and max()
    ...

assert clamp(5, lo=0, hi=3) == 3
assert clamp(-2, lo=0, hi=3) == 0
assert clamp(2, lo=0, hi=3) == 2
# clamp(5, 0, 3) -> TypeError: lo and hi are keyword-only — try it
```

### 5.3 The mutable default trap

```python
def register(event, log=[]):    # the default is created ONCE, at def time — not per call
    log.append(event)
    return log
```
Default values live on the function object and are evaluated exactly once, when `def` runs. The fix reviewers expect is the `None`-default idiom: default to `None`, create the fresh object inside.

**Exercise 5.3** — Using `register` above: predict all four printed values, run to confirm, then write a one-line comment explaining the last two. Finish by rewriting `register` with the `None`-default idiom so the surprise disappears.
```python
print(register("a"))          # ?
print(register("b"))          # ?
print(register("c", []))      # ?
print(register("d"))          # ?  — where did "c" go?
# rewrite register(event, log=None), creating the list inside, and rerun
```

### 5.4 Closures, LEGB, and `nonlocal`

```python
def make_counter():
    count = 0
    def bump():
        nonlocal count      # rebinding an Enclosing name needs nonlocal (LEGB: Local, Enclosing, Global, Builtins)
        count += 1
        return count
    return bump             # 'count' stays alive inside the returned closure
```
Reading an enclosing name just works; assigning to it without `nonlocal` silently creates a new local instead. A closure captures the *variable*, not its value at definition time — that late binding is 5.4b.

**Exercise 5.4a** — A stateful function with no class in sight.
```python
def make_accumulator(start: int = 0):
    # return a function add(n) that returns the running total
    # hint: nonlocal
    ...

acc = make_accumulator(10)
assert acc(5) == 15
assert acc(5) == 20
```

**Exercise 5.4b** — Predict the printed list, run, and explain in one comment why all three functions agree. Then rewrite the comprehension so it prints `[0, 1, 2]`.
```python
fns = [lambda: i for i in range(3)]
print([f() for f in fns])     # predict: ?
# rewrite: give the lambda a default argument — defaults bind at DEFINITION
# time (5.3's trap, used for good here)
```

## Chapter 6 — Idiomatic Python

### 6.1 EAFP vs LBYL

```python
if "port" in cfg and str(cfg["port"]).isdigit():   # LBYL: the checks drift from the operation
    port = int(cfg["port"])

try:
    port = int(cfg["port"])        # EAFP: attempt it — one lookup, no check/use gap
except (KeyError, ValueError):     # catch the NARROWEST exceptions that mean "expected miss"
    port = 8080
```
EAFP (easier to ask forgiveness than permission) is the Python default when a miss is a normal case, not a bug. Catching broad `Exception` here would hide real defects — chapter 13 drills that line.

**Exercise 6.1** — Walk a nested dict EAFP-style.
```python
def get_nested(d: dict, *keys, default=None):
    # follow keys into nested dicts; ANY miss (absent key, non-dict level) returns default
    # hint: one try/except (KeyError, TypeError) around a loop of lookups
    ...

assert get_nested({"a": {"b": 1}}, "a", "b") == 1
assert get_nested({"a": {}}, "a", "b", default=0) == 0
assert get_nested({"a": 5}, "a", "b", default=-1) == -1
```

### 6.2 Unpacking and starred assignment

```python
a, b = b, a                     # swap without a temp
first, *rest = [1, 2, 3, 4]     # the star soaks up the slack as a list -> rest == [2, 3, 4]
head, *_, tail = range(5)       # _ / *_ signal "don't care"
merged = {**defaults, **overrides}   # dict merge — the RIGHT side wins key clashes
```

**Exercise 6.2** — Split a command line into verb and arguments in one statement.
```python
def split_command(line: str) -> tuple[str, list[str]]:
    # "git commit -m x" -> ("git", ["commit", "-m", "x"]); no-arg commands give []
    # hint: starred assignment on .split()
    ...

assert split_command("git commit -m x") == ("git", ["commit", "-m", "x"])
assert split_command("ls") == ("ls", [])
```

### 6.3 `enumerate` and `zip`

```python
for i, line in enumerate(lines, start=1):    # never range(len(...)); start picks the first index
    ...

for name, score in zip(names, scores):       # lockstep iteration — stops at the SHORTEST input
    ...

dict(zip(keys, values))                      # the pair-up idiom
list(zip("ab", "12", strict=True))           # strict=True raises on length mismatch (3.10+)
```
Silently truncating at the shortest input is `zip`'s classic data-loss bug; pass `strict=True` whenever the lengths *must* agree.

**Exercise 6.3** — Report which lines changed.
```python
def numbered_mismatches(expected: list[str], got: list[str]) -> list[int]:
    # equal lengths guaranteed; return the 1-based indices where they differ
    # hint: enumerate(zip(...), start=1) inside a comprehension
    ...

assert numbered_mismatches(["a", "b", "c"], ["a", "x", "c"]) == [2]
assert numbered_mismatches(["a"], ["a"]) == []
```

### 6.4 Idioms reviewers scan for

```python
from pathlib import Path

", ".join(parts)                  # not += concatenation in a loop (that's quadratic)
if x is None:                     # never 'x == None' — identity for the singleton (2.4)
    ...
log = Path(base) / "logs" / "app.txt"   # not string concatenation with "/"
value = default if override is None else override   # 'override or default' swallows 0, "", False
```
Each left-hand form is what a fluent reviewer expects; each avoided form is a review comment waiting to happen. The last line is the subtlest: `or` treats every falsy value as missing.

**Exercise 6.4** — Rewrite this fragment idiomatically: no `+=` string building, no `== None`, no `range(len(...))` — three lines or fewer.
```python
out = ""
for i in range(len(cells)):
    if cells[i] == None:
        out = out + "-,"
    else:
        out = out + str(cells[i]) + ","
out = out[:-1]
# rewrite: join over a conditional expression inside a comprehension
```

## Chapter 7 — Iterators & Generators

### 7.1 The iterator protocol

```python
it = iter([1, 2])        # a for-loop is sugar for: iter(), then next() until StopIteration
next(it)                 # -> 1
next(it)                 # -> 2; one more next(it) raises StopIteration
next(it, "done")         # 2-arg next: return a default instead of raising
```
An *iterable* can hand out fresh iterators forever (a list); an *iterator* is single-pass — once exhausted it stays empty. Passing a half-consumed iterator around is a classic subtle bug.

**Exercise 7.1** — Consecutive pairs, driven by the protocol directly: no indexing, no slicing.
```python
def pairwise_manual(xs: list[int]) -> list[tuple[int, int]]:
    # [(x0, x1), (x1, x2), ...]; length < 2 gives []
    # hint: iter(), a 2-arg next() to prime, then a for-loop over the SAME iterator
    ...

assert pairwise_manual([1, 2, 3]) == [(1, 2), (2, 3)]
assert pairwise_manual([7]) == []
```

### 7.2 `yield`: generator functions

```python
def read_chunks(data: str, size: int):
    for i in range(0, len(data), size):
        yield data[i : i + size]     # PAUSES here — locals survive until the next next()

gen = read_chunks("abcdef", 2)       # NO body code has run yet; this only builds the generator
next(gen)                            # "ab" — executes up to the first yield
```
A generator function returns a generator object immediately; the body advances only on demand. State lives in the paused frame — no instance variables needed.

**Exercise 7.2** — Order-preserving dedup as a stream.
```python
def dedupe(items):
    # yield each item the FIRST time it appears, preserving order; works for any iterable
    # hint: a seen-set guarding a yield
    ...

assert list(dedupe([3, 1, 3, 2, 1])) == [3, 1, 2]
assert list(dedupe("aab")) == ["a", "b"]
```

### 7.3 Lazy pipelines

```python
lines = (raw.strip() for raw in fh)              # nothing has been read yet
errors = (ln for ln in lines if "ERROR" in ln)   # still nothing — just composed machinery
first = next(errors, None)                       # NOW work happens, and only up to the first hit
```
Chained generators stream data of any size through constant memory (4.2's point, compounded). Nothing executes until something consumes the end of the pipeline.

**Exercise 7.3** — Find the first match while provably consuming no more input than needed.
```python
def first_long_word(words, min_len: int):
    # return the first word with len > min_len, or None; accept any iterable
    # hint: 2-arg next() over a generator expression
    ...

stream = iter(["a", "bb", "cccc", "dd"])
assert first_long_word(stream, 3) == "cccc"
assert next(stream) == "dd"        # the lazy proof: "dd" was never consumed by the search
```

### 7.4 The `itertools` toolkit

```python
from itertools import chain, groupby, islice, pairwise

chain(a, b)                  # one stream over many iterables — no copying, no +
islice(gen, 5)               # slicing for iterators: generators don't support [:5]
pairwise("abc")              # ('a','b'), ('b','c') — what you built by hand in 7.1
groupby(rows, key=level)     # groups CONSECUTIVE equal keys only — sort first if scattered
```
`groupby` grouping only adjacent equal keys is the gotcha everyone hits once. All of these return lazy iterators, so they compose with 7.3's pipelines for free.

**Exercise 7.4** — Run-length encode a string.
```python
from itertools import groupby

def run_lengths(s: str) -> list[tuple[str, int]]:
    # "aaabbc" -> [("a", 3), ("b", 2), ("c", 1)]
    # hint: groupby with no key; a group must be materialized to be measured
    ...

assert run_lengths("aaabbc") == [("a", 3), ("b", 2), ("c", 1)]
assert run_lengths("") == []
```

## Chapter 8 — Decorators & Context Managers

### 8.1 Writing decorators

```python
import functools

def logged(func):
    @functools.wraps(func)          # copies __name__/__doc__ — skip it and tracebacks lie to you
    def wrapper(*args, **kwargs):   # 5.1's forwarding is what makes the wrapper generic
        print("calling", func.__name__)
        return func(*args, **kwargs)
    return wrapper

@logged                             # sugar for: fetch = logged(fetch), applied at def time
def fetch(url: str) -> str:
    ...
```
A decorator is an ordinary function that takes a function and returns a replacement — the `@` line runs once, at definition. Everything you need was already covered: closures (5.4) hold `func`; stars (5.1) forward the call.

**Exercise 8.1** — A decorator that counts invocations.
```python
import functools

def count_calls(func):
    # wrap func so the wrapper carries a .calls attribute, incremented per call
    # hint: functions are objects — set the attribute on the wrapper; keep functools.wraps
    ...

@count_calls
def ping() -> str:
    return "pong"

assert ping() == "pong"
assert ping() == "pong"
assert ping.calls == 2
assert ping.__name__ == "ping"     # wraps did its job
```

### 8.2 `functools` essentials

```python
from functools import cache, partial

@cache                          # memoize on the args (they must be hashable); unbounded —
def parse(path: str) -> dict:   # use lru_cache(maxsize=...) when the key space is large
    ...

int_from_hex = partial(int, base=16)   # freeze arguments -> a new, narrower callable
int_from_hex("ff")                     # 255
```

**Exercise 8.2** — Prove the cache works, mechanically.
```python
from functools import cache

calls = []

@cache
def area(w: int, h: int) -> int:
    # record (w, h) in calls, then return the product
    ...

assert area(2, 3) == 6
assert area(2, 3) == 6
assert len(calls) == 1                        # the second call never ran the body
assert area(3, 2) == 6 and len(calls) == 2    # different args = a different cache key
```

### 8.3 The `with` protocol

```python
import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self                       # this is the value bound by 'as'
    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False                      # False = let exceptions propagate (the sane default)
```
`__exit__` always runs — `with` is `try/finally` with a protocol. Returning `True` from `__exit__` swallows the exception; do that only when suppression *is* the feature.

**Exercise 8.3** — A context manager that turns exceptions into data.
```python
class Collect:
    # __enter__ returns self carrying a fresh .items list; on an exception,
    # __exit__ appends ("error", <exception class name>) and suppresses it
    # hint: exc_type is None on a clean exit; exc_type.__name__ otherwise
    ...

with Collect() as c:
    c.items.append("a")
assert c.items == ["a"]

with Collect() as c:
    raise ValueError("boom")             # suppressed by __exit__
assert c.items == [("error", "ValueError")]
```

### 8.4 `contextlib`: generators as context managers

```python
from contextlib import contextmanager, suppress
from pathlib import Path

@contextmanager
def temp_attr(obj, name, value):
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield obj                  # before the yield = __enter__; after = __exit__
    finally:
        setattr(obj, name, old)    # guaranteed restore, even if the body raised

with suppress(FileNotFoundError):  # the honest spelling of try/except/pass
    Path("stale.lock").unlink()
```
One generator replaces the whole 8.3 class: yield exactly once, and wrap the yield in `try/finally` whenever cleanup must be unconditional. Without the `finally`, an exception in the body skips your cleanup.

**Exercise 8.4** — Balanced push/pop that survives exceptions.
```python
from contextlib import contextmanager

@contextmanager
def pushd(stack: list[str], name: str):
    # append name on entry; ALWAYS pop on exit, even when the body raises
    # hint: try/finally around a single yield
    ...

trail: list[str] = []
with pushd(trail, "a"):
    assert trail == ["a"]
assert trail == []

try:
    with pushd(trail, "b"):
        raise RuntimeError("boom")
except RuntimeError:
    pass
assert trail == []                 # cleanup ran despite the raise
```

### How to work through this efficiently
Read each exercise's asserts before its hint — they are the spec, and half the learning is decoding them. This part compounds on itself deliberately: 5.1's forwarding is the skeleton of 8.1's wrapper, 5.4's closures are what make decorators possible, and the evaluated-once default is both the trap (5.3) and the fix (5.4b) — so run the two predict exercises and write the one-line *why* before moving past them; that comment is the actual deliverable. For the generator chapter, prove laziness with `next()` (as 7.3's second assert does) instead of trusting the prose.
