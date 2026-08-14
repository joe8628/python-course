# Part I — Reactivating the Fundamentals

Work in a scratch file or REPL. For every exercise, the `assert`s are the acceptance tests: your code is correct when they all pass silently.

## Chapter 1 — Modern Python at a Glance

### 1.1 f-strings

```python
name, n = "svc", 3
f"{name}-{n:03d}"        # ':' begins a format spec; 03d = zero-pad to width 3
f"{n=}"                  # '=' self-documents: renders "n=3" (debug shorthand)
f"{3.14159:.2f}"         # .2f = fixed-point, 2 decimals -> "3.14"
```
The format spec is a mini-language (`[fill][align][width][,][.prec][type]`). It replaces almost all `.format()` and `%` usage.

**Exercise 1.1** — Write a one-liner that renders a right-aligned, comma-grouped price.
```python
def fmt_price(label: str, amount: float) -> str:
    # target: fmt_price("CPU", 1299.5) == "CPU.........$1,299.50"
    # hint: dots are fill, '<' / '>' set alignment, ',' groups thousands
    ...

assert fmt_price("CPU", 1299.5) == "CPU.........$1,299.50"
assert fmt_price("RAM", 80) == "RAM...........$80.00"
```

### 1.2 The walrus operator `:=`

```python
# := assigns AND yields the value inside a larger expression
if (size := len(payload)) > 1024:   # bind once, reuse 'size' below
    raise ValueError(f"too big: {size}")
```
Use it to avoid computing or calling something twice, or to remove a "priming read" before a loop. Don't use it where a plain assignment is clearer.

**Exercise 1.2** — Refactor this two-call loop into one that calls `next_line()` exactly once per iteration, using `:=`.
```python
line = next_line()
while line != "":
    process(line)
    line = next_line()
# rewrite as a single while-loop with no duplicated next_line() call
```

### 1.3 Structural pattern matching

```python
# match compares STRUCTURE and binds names — far beyond an == switch
match event:
    case {"type": "click", "x": x, "y": y}:   # dict pattern, binds x and y
        handle(x, y)
    case ("key", code) if code > 0:           # sequence pattern + guard
        ...
    case _:                                   # wildcard: the default arm
        ignore()
```

**Exercise 1.3** — Build a parser for commands shaped as tuples. Fill the arms; return a string per the asserts. Don't add an `if/elif` chain — use `case` patterns.
```python
def run(cmd):
    match cmd:
        ...  # ("move", dx, dy) -> "moved by dx,dy"
             # ("quit",)        -> "bye"
             # anything else     -> "unknown"

assert run(("move", 2, -1)) == "moved by 2,-1"
assert run(("quit",)) == "bye"
assert run(("foo",)) == "unknown"
```

### 1.4 A clean environment (do this once, now)

```bash
python -m venv .venv && source .venv/bin/activate   # isolated interpreter + deps
python -m pip install ruff mypy pytest              # lint, type-check, test
```
A `pyproject.toml` is the modern single source of truth for project metadata and tool config — we'll fill it out in Part IV. For now, just confirm `ruff check .` and `mypy --version` run inside the venv.

## Chapter 2 — The Data Model & Built-in Types

### 2.1 Numbers

```python
2 ** 200                 # int is arbitrary-precision — never overflows
0.1 + 0.2                # 0.30000000000000004 — binary float can't store 0.1 exactly
from decimal import Decimal
Decimal("0.1") + Decimal("0.2")   # exact base-10 — construct from STRINGS, not floats
```

**Exercise 2.1** — Implement exact money addition. Returning a `float` will fail the assert by design.
```python
from decimal import Decimal

def add_money(*amounts: str) -> Decimal:
    # sum string amounts exactly; quantize to 2 dp
    # hint: Decimal(a).quantize(Decimal("0.01"))
    ...

assert add_money("0.10", "0.20") == Decimal("0.30")
assert str(add_money("19.99", "0.01")) == "20.00"
```

### 2.2 Text vs. bytes

```python
"café".encode("utf-8")           # str = code points (text); bytes = raw octets
b"\xc3\xa9".decode("utf-8")      # decode turns octets back into text -> "é"
len("café"), len("café".encode())  # (4, 5) — chars != bytes for non-ASCII
```
The boundary rule: decode bytes to `str` the moment data enters your program, encode back to `bytes` only at the I/O edge.

**Exercise 2.2** — Round-trip a string through bytes and prove the invariant holds for any codec you pass.
```python
def roundtrip(text: str, codec: str = "utf-8") -> bool:
    # encode then decode; return whether you recovered the original
    ...

assert roundtrip("naïve café")
assert roundtrip("Σπασμένα", "utf-8")
```

### 2.3 Slicing

```python
s = "abcdef"
s[1:4]      # [start:stop) — stop is exclusive -> "bcd"
s[::-1]     # [start:stop:step], step -1 walks backward -> reversed
s[::2]      # every 2nd element
```

**Exercise 2.3** — Write a palindrome check using slicing only (no loop, no `reversed`).
```python
def is_palindrome(s: str) -> bool:
    ...  # one line; compare s against its reverse slice

assert is_palindrome("racecar")
assert not is_palindrome("python")
```

### 2.4 Truthiness, identity, equality

```python
if items:           # empty containers/0/""/None are falsy — don't write len(x)==0
    ...
a == b              # value equality (calls __eq__)
a is b              # identity: same object in memory (id(a) == id(b))
x is None           # ALWAYS use 'is' for None — it's a singleton
```

**Exercise 2.4** — Predict each result, then run to confirm. Where prediction and reality differ, write a one-line comment explaining why (hint: small-int and string interning are implementation details, not guarantees).
```python
print(256 is 256)        # ?
print(257 is 257)        # ?  (try in a .py file, not the REPL)
print([] is [])          # ?
print("" == False)       # ?
print([] == False)       # ?
```

## Chapter 3 — Core Collections in Depth

### 3.1 Choosing the structure

```python
# list  -> ordered, mutable, index access            (a sequence of things)
# tuple -> ordered, immutable, hashable               (a fixed record / dict key)
# set   -> unordered, unique, O(1) membership         (dedup + fast 'in')
# dict  -> key->value, insertion-ordered (3.7+), O(1) (a lookup table)
```

**Exercise 3.1** — Given log lines `"<user> <action>"`, return the set of unique users. Pick the structure that makes dedup free.
```python
def unique_users(lines: list[str]) -> set[str]:
    ...

assert unique_users(["jj login", "jj click", "amy login"]) == {"jj", "amy"}
```

### 3.2 dict patterns that separate fluent from rusty

```python
d.get(k, default)              # never raises KeyError; returns default if absent
d.setdefault(k, []).append(v)  # get-or-initialize in one step (group-by idiom)
{k: v for k, v in pairs}       # dict comprehension
```

**Exercise 3.2** — Group words by their first letter. Use `setdefault` (or a `defaultdict` — see below); no `if k in d` checks.
```python
def group_by_initial(words: list[str]) -> dict[str, list[str]]:
    ...

assert group_by_initial(["ant", "bee", "ape"]) == {"a": ["ant", "ape"], "b": ["bee"]}
```

### 3.3 The `collections` toolkit

```python
from collections import defaultdict, Counter, deque
defaultdict(list)        # missing key auto-creates default(); kills setdefault boilerplate
Counter(iterable)        # tally; .most_common(n) returns top-n by count
deque(maxlen=5)          # O(1) push/pop BOTH ends; with maxlen, a fixed ring buffer
```

**Exercise 3.3a** — Top-N word frequency. Lean on `Counter`; don't hand-roll the tally.
```python
def top_words(text: str, n: int) -> list[tuple[str, int]]:
    # split, normalize case, count, return n most common as (word, count)
    ...

assert top_words("a A b a B", 2) == [("a", 3), ("b", 2)]
```

**Exercise 3.3b** — A rolling window of the last `k` readings. Let `deque(maxlen=k)` evict for you; you should never call `pop` manually.
```python
def last_k(readings: list[int], k: int) -> list[int]:
    ...

assert last_k([1, 2, 3, 4, 5], 3) == [3, 4, 5]
```

## Chapter 4 — Control Flow & Comprehensions

### 4.1 Comprehensions: map + filter in one pass

```python
[f(x) for x in xs if p(x)]      # build a NEW list; transform + filter together
{k: f(v) for k, v in d.items()} # dict comprehension
{f(x) for x in xs}              # set comprehension (auto-dedup)
```
Readability rule: if it needs more than one `for` plus one `if`, or won't fit comfortably on a line, use a loop instead.

**Exercise 4.1** — Convert this loop into a single comprehension.
```python
result = []
for x in range(20):
    if x % 3 == 0:
        result.append(x * x)
# rewrite 'result' as one list comprehension
```

### 4.2 Generator expressions: lazy and memory-flat

```python
(f(x) for x in xs)          # generator: yields one item at a time, builds no list
sum(x*x for x in range(10)) # parens optional as a sole call arg — never materializes
```
Use a generator when feeding an aggregator (`sum`, `any`, `max`) or streaming large data — you avoid holding the whole sequence in memory.

**Exercise 4.2** — Sum the squares of even numbers up to `n` without ever building a list. Prove laziness by making it work for `n = 10_000_000` without memory blowup.
```python
def sum_even_squares(n: int) -> int:
    ...  # use a generator expression inside sum()

assert sum_even_squares(10) == 0 + 4 + 16 + 36 + 64
```

### 4.3 `for ... else` and short-circuiting

```python
for x in xs:
    if hit(x):
        break
else:                # runs ONLY if the loop completed without 'break'
    not_found()      # ideal for "searched everything, found nothing"
```

**Exercise 4.3** — Implement `first_prime_over(n)` returning the first prime `> n`. Use the `for/else` form to detect "no divisor found" cleanly.
```python
def first_prime_over(n: int) -> int:
    # outer loop over candidates; inner loop tests divisors with for/else
    ...

assert first_prime_over(10) == 11
assert first_prime_over(14) == 17
```

### 4.4 Flattening (a comprehension-ordering gotcha)

```python
[x for row in matrix for x in row]   # nested fors read LEFT-TO-RIGHT, outer first
```

**Exercise 4.4** — Flatten one level, keeping only positive numbers.
```python
def flatten_positive(matrix: list[list[int]]) -> list[int]:
    ...

assert flatten_positive([[1, -2], [3, -4, 5]]) == [1, 3, 5]
```

### How to work through this efficiently
Type every snippet — don't read passively. For each exercise: read the `assert`s first (they're the spec), reach for the idiom named in the hint, then run until green. When something surprises you (2.4 especially), reproduce it in a file and write the one-line *why* in a comment; that's the part that actually re-cements the model.

Then:
1. Run `python tools/lint_workbook.py part-1.md`. If the linter flags
   the exemplar itself, FIX THE LINTER (the exemplar is ground truth),
   rerun until clean, and note the linter change in PROGRESS.md.
2. Write /tmp/verify_part1.py with reference solutions for exercises
   1.1, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3a, 3.3b, 4.2, 4.3, 4.4 plus
   their exact asserts (1.2, 2.4, 4.1 are refactor/predict exercises —
   skip). Run `pytest /tmp/verify_part1.py -q`; must be green.
3. Update PROGRESS.md: part-1 -> linted. Delete the /tmp file. Stop.
