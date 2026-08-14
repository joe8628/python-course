# Part VI — Applied Python for the Role (Chapters 21–24)

Work in one scratch file per chapter (`scratch_21.py` …), venv active. The asserts stay the acceptance tests. Chapters 21, 23 and 24 run on the stdlib alone; chapter 22 needs a one-time `python -m pip install fastapi httpx` in your venv — its TestClient drives the app in-process, so nothing in this part opens a socket.

## Chapter 21 — Working with Data

### 21.1 JSON: the type gap

```python
import json
from datetime import datetime

json.dumps({"id": 7, "tags": ("a", "b")})   # tuple silently becomes a JSON array -> comes back a list
json.loads('{"7": true}')                   # object keys are ALWAYS str after a round-trip
json.dumps({"at": datetime.now()})          # TypeError — no JSON form; pass default= to translate
```
JSON has six types; everything else in your data is your problem. `default=` is called for any value `dumps` can't handle — return a JSON-able stand-in there.

**Exercise 21.1** — Serialize records that contain `date` and `set` values.
```python
import json
from datetime import date

def to_json(record: dict) -> str:
    # dates -> ISO strings, sets -> sorted lists, everything else untouched
    # hint: a default= callable; date.isoformat() and sorted()
    ...

doc = to_json({"user": "amy", "joined": date(2024, 5, 1), "roles": {"dev", "admin"}})
assert json.loads(doc) == {"user": "amy", "joined": "2024-05-01", "roles": ["admin", "dev"]}
```

### 21.2 CSV: everything is a string

```python
import csv, io

rows = csv.DictReader(io.StringIO("name,qty\nbolt,4\n"))   # the header row becomes the dict keys
next(rows)                   # {'name': 'bolt', 'qty': '4'} — '4' is a str; convert types yourself
# writing needs open(path, "w", newline="") — omit newline="" and Windows double-spaces the file
```

**Exercise 21.2** — Parse CSV text into typed records.
```python
import csv, io
from dataclasses import dataclass

@dataclass
class Item:
    name: str
    qty: int
    price: float

def load_items(csv_text: str) -> list[Item]:
    # hint: DictReader over io.StringIO; convert each field to its declared type
    ...

items = load_items("name,qty,price\nbolt,4,0.10\nnut,10,0.05\n")
assert items[0] == Item("bolt", 4, 0.10)
assert sum(i.qty for i in items) == 14
```

### 21.3 REST is payload shaping, not transport

```python
from urllib.parse import urlencode, urlparse, parse_qs

urlencode({"q": "python dev", "page": 2})   # 'q=python+dev&page=2' — escaping handled for you
parse_qs(urlparse("https://api.example.com/jobs?tag=py&tag=sql").query)
                                            # {'tag': ['py', 'sql']} — values are LISTS: params repeat
```
`requests`/`httpx` only change the transport; the engineering is in shaping payloads and walking pagination, which needs no network to practice.

**Exercise 21.3** — Drain a paginated endpoint.
```python
from collections.abc import Callable

def fetch_all(fetch: Callable[[int], dict]) -> list[dict]:
    # fetch(page) returns {"items": [...], "next": <page-number or None>}
    # start at page 1, follow "next" until None, concatenate the items
    # hint: a while loop whose cursor is the "next" field
    ...

pages = {
    1: {"items": [{"id": 1}, {"id": 2}], "next": 2},
    2: {"items": [{"id": 3}], "next": None},
}
assert fetch_all(pages.get) == [{"id": 1}, {"id": 2}, {"id": 3}]
```

### 21.4 sqlite3: a SQL engine in the stdlib

```python
import sqlite3

conn = sqlite3.connect(":memory:")           # a full SQL database, no server, one import
conn.execute("CREATE TABLE t (name TEXT, qty INTEGER)")
conn.execute("INSERT INTO t VALUES (?, ?)", ("bolt", 4))   # ? placeholders — NEVER f-strings (see 24.1)
conn.executemany("INSERT INTO t VALUES (?, ?)", [("nut", 10), ("screw", 1)])  # batch insert in one call
```
Let SQL do the set arithmetic — `GROUP BY`/`ORDER BY` in the engine beats reimplementing them in a Python loop, and knowing where to draw that line is what "DB at a high level" means in practice.

**Exercise 21.4** — One aggregation query, not a Python loop.
```python
import sqlite3

def top_sellers(sales: list[tuple[str, int]], n: int) -> list[tuple[str, int]]:
    # load sales into an in-memory table, then answer with ONE query:
    # total qty per product, highest total first, top n rows
    # hint: executemany; GROUP BY + SUM + ORDER BY ... DESC + LIMIT ?
    ...

data = [("bolt", 4), ("nut", 10), ("bolt", 3), ("screw", 1)]
assert top_sellers(data, 2) == [("nut", 10), ("bolt", 7)]
```

### 21.5 The ORM idea: rows ↔ objects

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row       # rows gain dict-like access: row["name"], dict(row)
# an ORM (SQLAlchemy, Django) automates exactly this row<->object mapping, plus SQL
# generation and change tracking — at the cost of a query layer you must still understand
```

**Exercise 21.5** — Hand-roll the mapping an ORM automates.
```python
import sqlite3
from dataclasses import dataclass

@dataclass
class Employee:
    id: int
    name: str
    dept: str

def load_employees(conn: sqlite3.Connection) -> list[Employee]:
    # map every row of table employees to an Employee, in id order
    # hint: sqlite3.Row rows convert with dict(); ** unpacking (ch 5)
    ...

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE employees (id INTEGER, name TEXT, dept TEXT)")
conn.executemany("INSERT INTO employees VALUES (?, ?, ?)",
                 [(1, "amy", "eng"), (2, "raj", "ops")])
assert load_employees(conn) == [Employee(1, "amy", "eng"), Employee(2, "raj", "ops")]
```

## Chapter 22 — A Web Framework in Practice

### 22.1 Path operations: typed params in, JSON out

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")                          # a decorator (ch 8) as a route-table entry
def read_item(item_id: int, q: str | None = None):    # hints VALIDATE and CONVERT: /items/7 -> int 7
    return {"item_id": item_id, "q": q}               # plain dicts serialize to JSON automatically
```

```python
from fastapi.testclient import TestClient

client = TestClient(app)                 # drives the app in-process — no server, no port
client.get("/items/7?q=x").json()        # {'item_id': 7, 'q': 'x'} — item_id came back an int
```

**Exercise 22.1** — Two endpoints, tested through the client.
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

# add GET /health      -> {"status": "ok"}
# add GET /echo/{word} -> {"word": word}, uppercased when query param
#     upper: bool = False is true
...

client = TestClient(app)
assert client.get("/health").json() == {"status": "ok"}
assert client.get("/echo/hi").json() == {"word": "hi"}
assert client.get("/echo/hi?upper=true").json() == {"word": "HI"}
```

### 22.2 Pydantic models: validation at the boundary

```python
from pydantic import BaseModel

class Order(BaseModel):        # the request schema as a class — this IS the input validation
    sku: str
    qty: int = 1               # type + default: "qty": "3" coerces, "qty": "??" is rejected

@app.post("/orders")
def create_order(order: Order):          # invalid payloads never reach this line — FastAPI answers 422
    return {"sku": order.sku, "qty": order.qty}
```
The model declaration replaces a page of hand-written `isinstance`/`KeyError` checks, and the 422 response enumerates every field error at once.

**Exercise 22.2** — A validated signup endpoint.
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()

# model Signup: username (str) and age (int); POST /signup accepts a Signup
# and returns {"welcome": <username>}
...

client = TestClient(app)
assert client.post("/signup", json={"username": "amy", "age": 33}).json() == {"welcome": "amy"}
assert client.post("/signup", json={"username": "amy", "age": "??"}).status_code == 422
```

### 22.3 Failing properly: HTTPException

```python
from fastapi import HTTPException

USERS = {1: "amy"}

@app.get("/users/{uid}")
def get_user(uid: int):
    if uid not in USERS:
        raise HTTPException(status_code=404, detail="no such user")   # rendered as a JSON error body
    return {"name": USERS[uid]}
```
Raise, don't return, error responses: the exception short-circuits the handler and keeps the happy path unindented — ch 13's EAFP shape at the HTTP layer.

**Exercise 22.3** — Lookup with a correct 404.
```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()
STOCK = {"bolt": 4}

# GET /stock/{name} -> {"name": name, "qty": <qty>} for known items,
# else 404 with detail "unknown item"
...

client = TestClient(app)
assert client.get("/stock/bolt").json() == {"name": "bolt", "qty": 4}
missing = client.get("/stock/gizmo")
assert missing.status_code == 404 and missing.json()["detail"] == "unknown item"
```

### 22.4 Depends: injection you can override in tests

```python
from fastapi import Depends

def get_db() -> dict:                            # any callable can be a dependency
    return {"bolt": 4}

@app.get("/count")
def count_items(db: dict = Depends(get_db)):     # FastAPI calls get_db per request, hands in the result
    return {"n": len(db)}

app.dependency_overrides[get_db] = lambda: {}    # tests swap real deps for fakes — no monkeypatching
```

**Exercise 22.4** — A feature flag behind a dependency.
```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

def get_settings() -> dict:
    return {"env": "prod", "feature_x": False}

# GET /features -> {"feature_x": <value from the settings dependency>}
...

client = TestClient(app)
assert client.get("/features").json() == {"feature_x": False}
app.dependency_overrides[get_settings] = lambda: {"env": "test", "feature_x": True}
assert client.get("/features").json() == {"feature_x": True}
```

## Chapter 23 — Design Patterns & Clean Architecture

### 23.1 Strategy: callables are the pattern

```python
def bulk_discount(price: float) -> float:
    return price * 0.9                       # a strategy is just a callable

STRATEGIES = {"bulk": bulk_discount, "none": lambda p: p}   # selection is a dict lookup
STRATEGIES["bulk"](100.0)                    # GoF Strategy with no class hierarchy in sight
```
In Python many classic patterns (Strategy, Command, Factory) collapse into first-class functions plus a dict; reaching for interface-and-subclasses first is a Java accent. A class earns its place only when the strategy carries state.

**Exercise 23.1** — Pluggable discount strategies.
```python
from collections.abc import Callable

def checkout(total: float, strategy: Callable[[float], float]) -> float:
    # apply the strategy, round to 2 decimals
    ...

# define two strategies: half_off, and free_over_100
# (total >= 100 -> everything free, otherwise unchanged)
...

assert checkout(80.0, half_off) == 40.0
assert checkout(120.0, free_over_100) == 0.0
assert checkout(99.0, free_over_100) == 99.0
```

### 23.2 Registry: a decorator-built factory

```python
from collections.abc import Callable

HANDLERS: dict[str, Callable] = {}

def handles(kind: str):
    def register(fn):
        HANDLERS[kind] = fn      # the side effect IS the wiring — a factory assembled at import time
        return fn                # returned unchanged: registration, not wrapping (contrast ch 8)
    return register
```
This is how web routes, CLI subcommands and plugin systems are wired; the dispatch table replaces the ever-growing `if kind == ...` chain.

**Exercise 23.2** — A command dispatcher.
```python
from collections.abc import Callable

REGISTRY: dict[str, Callable] = {}

def command(name: str):
    # decorator: register fn in REGISTRY under name, return fn unchanged
    ...

def dispatch(name: str, *args):
    # look up the command and call it with args
    ...

@command("add")
def add(a: int, b: int) -> int:
    return a + b

@command("upper")
def upper(s: str) -> str:
    return s.upper()

assert dispatch("add", 2, 3) == 5
assert dispatch("upper", "hey") == "HEY"
assert sorted(REGISTRY) == ["add", "upper"]
```

### 23.3 Ports as Protocols (the D in SOLID)

```python
from typing import Protocol

class Notifier(Protocol):                   # the port: what the core NEEDS, not what happens to exist
    def send(self, to: str, body: str) -> None: ...

def alert(notifier: Notifier, user: str) -> None:
    notifier.send(user, "quota exceeded")   # policy depends on a shape, never on smtplib
```
Dependency inversion in Python is structural: anything with the right methods satisfies the port (ch 12's Protocols), so the production adapter and the test fake are interchangeable without a common base class.

**Exercise 23.3** — A storage port with a test fake.
```python
from typing import Protocol

class Storage(Protocol):
    def save(self, key: str, data: bytes) -> None: ...

def archive(storage: Storage, name: str, text: str) -> str:
    # save text utf-8-encoded under key f"reports/{name}"; return the key
    ...

class FakeStorage:
    def __init__(self) -> None:
        self.saved: dict[str, bytes] = {}
    def save(self, key: str, data: bytes) -> None:
        self.saved[key] = data

fake = FakeStorage()
assert archive(fake, "q3", "revenue up") == "reports/q3"
assert fake.saved == {"reports/q3": b"revenue up"}
```

### 23.4 Functional core, imperative shell

```python
def price_after_tax(net: float, rate: float) -> float:
    return round(net * (1 + rate), 2)        # pure core: all decisions, zero I/O — tests need no mocks

def handle(payload: dict) -> dict:           # thin shell: unwrap, delegate, wrap — nowhere for bugs to hide
    return {"gross": price_after_tax(payload["net"], payload["rate"])}
```
This is single-responsibility at function scale: the core changes for business reasons, the shell for I/O reasons. Push every `if` toward the core and every `open`/`print` toward the shell.

**Exercise 23.4** — Split the total calculation from the file handling.
```python
from pathlib import Path

def order_total(lines: list[str]) -> float:
    # pure core: lines are "name,qty,price"; sum qty*price for qty > 0;
    # 5% off totals over 500; round to 2 decimals
    ...

def process_order(path: str) -> str:
    # thin shell: read the file, delegate to the core, return "order total: X.XX"
    # hint: Path.read_text().splitlines(); an f-string format spec (ch 1)
    ...

assert order_total(["bolt,4,0.10", "nut,0,9.99"]) == 0.4
assert order_total(["srv,2,300.00"]) == 570.0

import tempfile
p = Path(tempfile.mkdtemp()) / "order.csv"
p.write_text("bolt,4,0.10\nsrv,2,300.00\n")
assert process_order(str(p)) == "order total: 570.38"
```

## Chapter 24 — Security Essentials

### 24.1 Injection: keep data out of the parser

```python
# name = "x'; DROP TABLE users; --"   <- attacker-controlled input
conn.execute(f"SELECT * FROM users WHERE name = '{name}'")   # VULNERABLE: input becomes SQL syntax
conn.execute("SELECT * FROM users WHERE name = ?", (name,))  # FIXED: ? sends the value out-of-band
```
Shell injection (`subprocess` with `shell=True`), XSS and template injection are the same class: untrusted text reaching an interpreter. The fix is always structural — parameterize; never escape by hand.

**Exercise 24.1** — A lookup that treats input strictly as data.
```python
import sqlite3

def find_user(conn: sqlite3.Connection, name: str) -> list[tuple]:
    # exact-name lookup; the input must never reach the SQL parser
    # hint: ? placeholder + parameters tuple; fetchall()
    ...

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (name TEXT)")
conn.executemany("INSERT INTO users VALUES (?)", [("amy",), ("raj",)])
assert find_user(conn, "amy") == [("amy",)]
assert find_user(conn, "x' OR '1'='1") == []                      # payload comes back as plain data
assert conn.execute("SELECT count(*) FROM users").fetchone() == (2,)   # and the table survived
```

### 24.2 Path traversal: resolve, then verify

```python
from pathlib import Path

base = Path("/srv/uploads").resolve()
target = (base / user_filename).resolve()   # resolve() collapses every ../ BEFORE you check
target.is_relative_to(base)                 # the whole containment check in one call (3.9+)
```
Scanning the raw string for `".."` is the classic broken fix — encodings and symlinks route around it; compare resolved paths instead.

**Exercise 24.2** — Serve files only from inside the base directory.
```python
from pathlib import Path

def safe_path(base: str, filename: str) -> Path:
    # return the resolved path of filename under base;
    # raise ValueError if it escapes base
    # hint: resolve() both, then is_relative_to()
    ...

assert safe_path("/srv/uploads", "report.txt") == Path("/srv/uploads/report.txt")
try:
    safe_path("/srv/uploads", "../../etc/passwd")
    escaped = True
except ValueError:
    escaped = False
assert not escaped
```

### 24.3 Secrets: environment in, logs never

```python
import os, secrets

token = os.environ["API_TOKEN"]     # secrets come from the environment or a vault, never the repo
secrets.token_urlsafe(32)           # crypto-grade randomness; random.random() is predictable
# and keep credentials out of logs and repr() — leaked logs are the classic exfiltration path
```

**Exercise 24.3a** — Fail loudly when a secret is missing.
```python
def require_secret(name: str, env: dict[str, str]) -> str:
    # return env[name]; raise RuntimeError(f"missing secret: {name}")
    # when the key is absent OR its value is empty
    ...

assert require_secret("API_TOKEN", {"API_TOKEN": "s3cr3t"}) == "s3cr3t"
try:
    require_secret("API_TOKEN", {"API_TOKEN": ""})
    msg = "no error"
except RuntimeError as exc:
    msg = str(exc)
assert msg == "missing secret: API_TOKEN"
```

**Exercise 24.3b** — Compare tokens without leaking timing.
```python
def check_token(supplied: str, expected: str) -> bool:
    # equality that doesn't reveal how many leading characters matched
    # hint: hmac.compare_digest
    ...

assert check_token("abc123", "abc123")
assert not check_token("abc124", "abc123")
```

### 24.4 Password storage: slow hashes, fresh salt

```python
import hashlib, os

salt = os.urandom(16)                                       # per-user salt kills rainbow tables
key = hashlib.pbkdf2_hmac("sha256", b"pw", salt, 600_000)   # deliberately SLOW — that IS the security
# a bare sha256(pw) is brute-forceable at GPU speed; storing plaintext is an incident, not a bug
```

**Exercise 24.4** — Hash and verify, never store the password.
```python
def hash_password(pw: str) -> tuple[bytes, bytes]:
    # return (salt, digest): fresh 16-byte random salt,
    # pbkdf2_hmac sha256 at 100_000 rounds
    ...

def verify_password(pw: str, salt: bytes, digest: bytes) -> bool:
    # recompute with the STORED salt; compare timing-safely (24.3b's tool)
    ...

salt, digest = hash_password("hunter2")
assert verify_password("hunter2", salt, digest)
assert not verify_password("hunter3", salt, digest)
assert hash_password("hunter2")[0] != salt      # fresh salt every call -> no shared record
```

### 24.5 Deserialization: parsers, not interpreters

```python
import json, pickle
from ast import literal_eval

pickle.loads(blob)            # executes arbitrary code BY DESIGN — never on untrusted bytes
json.loads(text)              # data-only parser: the safe default at every trust boundary
literal_eval("[1, 2]")        # Python literals only; eval() is never input validation
```

**Exercise 24.5** — A settings parser with no code path to code.
```python
def parse_setting(text: str) -> object:
    # accept Python literals only (numbers, strings, lists, dicts, ...);
    # anything executable must raise ValueError — eval() is off the table
    # hint: ast.literal_eval already raises on non-literals
    ...

assert parse_setting("[1, 2, 3]") == [1, 2, 3]
assert parse_setting("{'debug': True}") == {"debug": True}
try:
    parse_setting("__import__('os').getcwd()")
    rejected = False
except ValueError:
    rejected = True
assert rejected
```

### How to work through this efficiently
Chapters 21 and 24 are one lesson taught twice: the `?` placeholder you use in 21.4 is the security control 24.1 names — connect them as you type. In chapter 22 the asserts double as API documentation; read them first and let the 422/404 cases tell you what the framework already handles so you don't re-implement it. In chapter 23 resist inventing classes — if a plain function passes the asserts, that *is* the pattern. And type the vulnerable lines of chapter 24's snippets too: recognizing the smell in someone else's diff is half the skill the chapter trains.
