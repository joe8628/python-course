# Part III — Object-Oriented & Typed Python (Chapters 9–12)

Work in a scratch file or REPL. For every exercise, the `assert`s are the acceptance tests: your code is correct when they all pass silently. Chapter 12 adds a second gate: run `mypy --strict` on your scratch file as instructed there — clean output is part of the spec.

## Chapter 9 — Classes & Objects

### 9.1 The minimum civilized dunders: `__repr__` and `__eq__`

```python
class Point:
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y
    def __repr__(self):
        return f"Point({self.x}, {self.y})"   # unambiguous, for tracebacks and the REPL
    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)   # without __eq__, == means IDENTITY (2.4)
```
A class without `__repr__` debugs as `<object at 0x...>`; a class without `__eq__` compares by memory address. Chapter 11 shows dataclasses generate both — write them by hand once so you know what's generated.

**Exercise 9.1** — Give a value type its civilized dunders.
```python
class Interval:
    # __init__(lo, hi); repr like "Interval(2, 5)"; equality by values
    # hint: compare (lo, hi) tuples in __eq__; f-string the repr
    ...

a, b = Interval(2, 5), Interval(2, 5)
assert a == b
assert a != Interval(2, 6)
assert repr(a) == "Interval(2, 5)"
```

### 9.2 Protocol dunders: act like a container

```python
class Playlist:
    def __init__(self, songs):
        self.songs = list(songs)
    def __len__(self):
        return len(self.songs)        # len(p) calls this
    def __getitem__(self, i):
        return self.songs[i]          # p[0] AND p[1:] (slices arrive as slice objects)
    def __contains__(self, song):
        return song in self.songs     # 'in' — without it Python falls back to iterating
```
Implement the protocol and the ecosystem arrives free: `for`, `in`, `reversed`, unpacking all work. `__getitem__` alone is enough to make a class iterable.

**Exercise 9.2** — Wrap a list so the wrapper feels native.
```python
class Deck:
    # wrap a list of card names: support len(), indexing AND slicing, and `in`
    # hint: delegate each dunder to the inner list
    ...

d = Deck(["ace", "king", "queen"])
assert len(d) == 3
assert d[0] == "ace" and d[-1] == "queen"
assert d[1:] == ["king", "queen"]
assert "king" in d
assert [c for c in d] == ["ace", "king", "queen"]   # iteration via __getitem__
```

### 9.3 `property`: computed and guarded attributes

```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius          # single underscore = internal by convention, not enforcement
    @property
    def radius(self) -> float:
        return self._radius
    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError("radius must be positive")   # validation runs on ASSIGNMENT
        self._radius = value
    @property
    def area(self) -> float:
        return 3.14159 * self._radius**2   # computed on access — call sites read c.area, no parens
```
Start with plain attributes; upgrade to `property` only when you need computation or validation — callers never notice the change. That upgrade path is why Python skips Java-style getters.

**Exercise 9.3** — A unit that converts on both read and write.
```python
class Celsius:
    # store .degrees; expose a READ-WRITE property fahrenheit that converts both ways
    # hint: f = c * 9 / 5 + 32, and the inverse for the setter
    ...

t = Celsius(100)
assert t.fahrenheit == 212.0
t.fahrenheit = 32
assert t.degrees == 0.0
```

### 9.4 `classmethod` and `staticmethod`

```python
import json

class Config:
    def __init__(self, entries: dict):
        self.entries = entries
    @classmethod
    def from_json(cls, text: str):     # gets the CLASS — the alternate-constructor idiom
        return cls(json.loads(text))   # cls, not Config: subclasses construct themselves
    @staticmethod
    def valid_key(key: str) -> bool:   # no self, no cls — a plain function namespaced here
        return key.isidentifier()
```
`classmethod` exists mainly for alternate constructors (`dict.fromkeys`, `datetime.fromtimestamp`). `staticmethod` is only an organizational hint — if it grows, promote it to a module function.

**Exercise 9.4** — An alternate constructor that parses.
```python
class Duration:
    def __init__(self, seconds: int):
        self.seconds = seconds

    # add a classmethod from_str: "90s" -> 90 seconds, "2m" -> 120
    # hint: the unit is the last character; build via cls(...)
    ...

assert Duration.from_str("90s").seconds == 90
assert Duration.from_str("2m").seconds == 120
assert isinstance(Duration.from_str("5s"), Duration)
```

## Chapter 10 — Inheritance & Composition

### 10.1 `super()` and the MRO

```python
class Base:
    def greet(self):
        return "base"

class Child(Base):
    def greet(self):
        return f"child+{super().greet()}"   # super() follows the MRO — NOT simply "my parent"

Child.__mro__     # (Child, Base, object) — the C3-linearized lookup order
```
With multiple inheritance, `super()` can dispatch to a *sibling*, which is exactly what lets cooperating classes stack. When behavior surprises you, print `Cls.__mro__` before theorizing.

**Exercise 10.1** — A cooperative pipeline built from the MRO.
```python
class Handler:
    def handle(self, msg: str) -> str:
        return msg

class Upper(Handler):
    # override handle: uppercase the message, then delegate up the MRO
    # hint: return super().handle(...)
    ...

class Exclaim(Handler):
    # override handle: append "!", then delegate up the MRO
    ...

class Loud(Upper, Exclaim):
    pass

assert Exclaim().handle("hi") == "hi!"
assert Loud().handle("hi") == "HI!"     # both ran: check Loud.__mro__ for the order
```

### 10.2 Mixins

```python
import json

class JsonMixin:                       # no __init__, no state — a mixin adds ONE capability
    def to_json(self) -> str:
        return json.dumps(vars(self))  # vars(obj) is its attribute dict

class User(JsonMixin, Base):           # mixins sit LEFT of the base so the MRO hits them first
    ...
```
A mixin is a stateless slice of behavior meant to be combined, never instantiated alone. This is how frameworks bolt features onto your classes.

**Exercise 10.2** — A reusable `__repr__` as a mixin.
```python
class ReprMixin:
    # __repr__ rendering "ClassName(attr=value, ...)" for ANY class that mixes it in
    # hint: type(self).__name__; iterate vars(self).items(); !r on values
    ...

class Point(ReprMixin):
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

assert repr(Point(1, 2)) == "Point(x=1, y=2)"
```

### 10.3 ABCs: contracts with teeth

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> None: ...   # subclasses MUST implement this

    def save_text(self, key: str, text: str) -> None:
        self.save(key, text.encode())    # concrete methods may build on abstract ones (2.2)

# Storage() -> TypeError: abstract class — the contract is enforced at INSTANTIATION
```
An ABC fails fast at construction time instead of `AttributeError` deep in production. Chapter 12's `Protocol` is the static-typing counterpart that needs no inheritance.

**Exercise 10.3** — A tiny template: abstract core, concrete shell.
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    # abstract method area(); concrete method describe() -> "area=<area to 1 dp>"
    # hint: an f-string format spec from 1.1 inside describe()
    ...

class Square(Shape):
    # constructor takes side; implement area()
    ...

assert Square(3).area() == 9
assert Square(2).describe() == "area=4.0"
# Shape() must raise TypeError — try it
```

### 10.4 Composition over inheritance

```python
class NotifyingList(list):        # IS-A: you now own list's ~40-method contract, forever
    ...

class AuditLog:
    def __init__(self):
        self._items: list[str] = []       # HAS-A: the list is an implementation detail
    def add(self, item: str) -> None:
        self._items.append(item)          # expose ONLY the surface you mean to support
```
Subclass only when the child is substitutable *everywhere* the parent appears (Liskov); otherwise compose and delegate. "I want most of its methods" is a reason to compose, not inherit.

**Exercise 10.4** — A stack that owns a list instead of being one.
```python
class BoundedStack:
    # compose a list; expose ONLY push(x), pop(), len(); construction takes maxlen;
    # pushing when full raises OverflowError
    # hint: self._items plus __len__; guard push with a length check
    ...

s = BoundedStack(maxlen=2)
s.push(1)
s.push(2)
assert len(s) == 2 and s.pop() == 2
s.push(3)
try:
    s.push(4)
except OverflowError:
    caught = True
assert caught
assert not isinstance(s, list)     # HAS-A list; IS not one
```

## Chapter 11 — Dataclasses & Modern Modeling

### 11.1 `@dataclass`: the boilerplate generator

```python
from dataclasses import dataclass, field

@dataclass
class Job:
    name: str
    retries: int = 3
    tags: list[str] = field(default_factory=list)   # a bare [] default is REFUSED — 5.3's trap, outlawed
```
One decorator generates the `__init__`/`__repr__`/`__eq__` you hand-wrote in 9.1, driven by the annotations. Field order defines constructor order; defaults must come last, like any signature.

**Exercise 11.1** — Model a record and lean on what's generated.
```python
from dataclasses import dataclass, field

# model Ticket: id (int), title (str), labels (list[str], default empty), done (bool, default False)
...

t = Ticket(1, "fix login")
assert t.labels == [] and t.done is False
assert Ticket(1, "fix login") == t                # generated __eq__: by value
assert repr(t) == "Ticket(id=1, title='fix login', labels=[], done=False)"
```

### 11.2 `frozen=True`: immutable value objects

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Money:
    amount_cents: int          # ints for money — 2.1's float trap avoided by design
    currency: str

price = Money(1999, "EUR")
# price.amount_cents = 5 -> FrozenInstanceError
sale = replace(price, amount_cents=999)    # "mutate" by building a changed COPY
```
Frozen instances are hashable, so value objects become usable as dict keys and set members. Update-by-copy via `replace` keeps every reference consistent.

**Exercise 11.2** — Prove hashability where it matters.
```python
from dataclasses import dataclass

# frozen dataclass GridCell(row: int, col: int); the asserts use cells as dict keys
...

board = {GridCell(0, 0): "start", GridCell(1, 1): "goal"}
assert board[GridCell(0, 0)] == "start"     # equal by value -> the SAME key
assert GridCell(2, 2) not in board
```

### 11.3 `slots=True`: cheaper, stricter instances

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Reading:
    sensor: str
    value: float

# slots=True removes the per-instance __dict__: less memory, faster attribute access,
# and a TYPO like r.valve = 1 raises AttributeError instead of passing silently
```
Reach for slots on classes you create by the million — or whenever silent attribute typos scare you more than dynamic attributes help you.

**Exercise 11.3** — Probe both effects of slots.
```python
from dataclasses import dataclass

# define Reading(sensor: str, value: float) with slots enabled
...

r = Reading("t1", 21.5)
assert not hasattr(r, "__dict__")     # no per-instance dict at all
try:
    r.valve = 1.0                     # typo'd attribute
except AttributeError:
    caught = True
assert caught
```

### 11.4 Enums: named, closed sets of states

```python
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()          # auto(): values you never hardcode or compare against
    ACTIVE = auto()
    CLOSED = auto()

Status.ACTIVE.name            # "ACTIVE"
Status["CLOSED"]              # lookup by NAME (raises KeyError if absent)
list(Status)                  # members iterate in definition order
```
An enum turns stringly-typed state (`"actve"` typos pass silently) into a closed set the language checks. Members are singletons: compare with `is` or `==`, both work.

**Exercise 11.4** — Levels with meaningful values and a forgiving parser.
```python
from enum import Enum

# define Level: DEBUG=10, INFO=20, ERROR=40; then parse_level(name: str) -> Level
# accepting any capitalization
# hint: index the enum by NAME after normalizing case
...

assert parse_level("info") is Level.INFO
assert parse_level("ERROR").value == 40
assert [lv.name for lv in Level] == ["DEBUG", "INFO", "ERROR"]
```

## Chapter 12 — Type Hints & Static Typing

### 12.1 Modern annotations, unions, and narrowing

```python
from collections.abc import Callable, Iterable

def first_name(uid: int) -> str | None:    # X | None is today's Optional[X] — callers MUST handle the miss
    ...

counts: dict[str, int] = {}                # builtin generics — typing.Dict/List are legacy
def total(xs: Iterable[int]) -> int: ...   # accept the widest type that works, return the narrowest
def retry(fn: Callable[[], int]) -> int: ...

def label(port: int | None) -> str:
    if port is None:                       # mypy NARROWS per branch...
        return "default"
    return f"port {port}"                  # ...so here port is int, and the None arm is gone
```
Hints never run — they exist for mypy and for readers. The payoff of `| None` is that forgetting the `is None` check becomes a *static* error instead of a 3 a.m. `AttributeError`.

**Exercise 12.1** — Make the miss explicit in the type.
```python
def safe_div(a: float, b: float) -> float | None:
    # None on division by zero, the quotient otherwise
    # hint: EAFP (6.1) or a guard — either is fine; the SIGNATURE is the point
    ...

assert safe_div(6, 3) == 2.0
assert safe_div(1, 0) is None
```

### 12.2 Generics: `TypeVar` links types together

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T], default: T) -> T:     # T ties input and output: list[int] -> int
    return items[0] if items else default

first([1, 2], 0)          # mypy infers T = int
# first([1, 2], "x")      # mypy error: T can't be int AND str
```
Without the `TypeVar`, `first` would return `Any` and type checking silently stops at every call site. A generic function promises a *relationship* between its types, not a fixed type.

**Exercise 12.2** — A generic chunker.
```python
from typing import TypeVar

# write chunk(items: list[T], size: int) -> list[list[T]]
# hint: slicing (2.3) inside a comprehension over range(0, len(items), size)
...

assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
assert chunk(["a"], 3) == [["a"]]
```

### 12.3 Protocols: structural typing

```python
from typing import Protocol

class Closeable(Protocol):
    def close(self) -> None: ...       # ANY object with a matching close() satisfies this

def shutdown(resource: Closeable) -> None:
    resource.close()                   # files, sockets, DB handles — none of them import Closeable
```
A `Protocol` types duck typing: matching is by shape, not by inheritance, so it works retroactively on classes you don't own. It is the static counterpart of 10.3's ABCs — no registration, no base class.

**Exercise 12.3** — One protocol, many shapes.
```python
from typing import Protocol

# define HasLen (a Protocol with __len__(self) -> int) and
# total_size(items: list[HasLen]) -> int that sums the lengths
# hint: a one-method Protocol class with a ...-body; sum() over a genexp (4.2)
...

assert total_size(["abc", [1, 2], "x"]) == 6
assert total_size([]) == 0
```

### 12.4 Running mypy: the second test suite

```bash
mypy scratch_12.py            # zero-config check of one file
mypy --strict scratch_12.py   # untyped defs, implicit Any, unchecked returns: all errors
```
Treat mypy as a test suite you don't have to write: run it on every chapter-12 scratch file, strict. This repo's `[tool.mypy]` config (Part 0, 0.4) bakes `strict = true` in for real projects.

**Exercise 12.4** — Make mypy pass. Save this as `scratch_12.py`, replace every `...` annotation with a real type, and iterate until BOTH commands are clean — behavior must not change:
`mypy --strict scratch_12.py` and `python scratch_12.py`.
```python
def mean(xs: ...) -> ...:
    # hint: the collection hints from 12.1 — accept the widest workable type
    return sum(xs) / len(xs)

def pick(mapping: ..., key: ..., fallback: ...) -> ...:
    # hint: dict[...] with two parameters; get() with a default
    return mapping.get(key, fallback)

assert mean([1.0, 2.0, 3.0]) == 2.0
assert pick({"a": 1}, "a", 0) == 1
assert pick({"a": 1}, "b", 0) == 0
```

### How to work through this efficiently
Chapters 9–11 are one arc: hand-write the dunders in 9.1, then watch `@dataclass` generate them in 11.1 — you'll know exactly what the decorator saves you and when it isn't enough (custom `__getitem__`, properties). When inheritance behaves oddly, print `__mro__` before theorizing (10.1), and default to composition unless substitutability genuinely holds (10.4). For chapter 12, run `mypy --strict` on every scratch file, not just 12.4's — the habit of reading type errors as failing tests is the actual skill; the asserts prove runtime behavior, mypy proves the contracts.
