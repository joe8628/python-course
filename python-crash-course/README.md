# Python Proficiency Crash Course

A workbook — not a textbook — for the experienced-but-rusty engineer prepping
for a Python developer role. Every concept is a short, grounded code snippet;
every exercise is a scaffold whose **asserts are the spec**. You write the body
until the asserts pass. No worked solutions exist anywhere in this repo.

## Prerequisites

- You have shipped software before, in some language. This course does not
  teach programming; it teaches *modern Python* to someone who can already code.
- Python **3.11+** installed (`python3 --version`).
- A terminal and an editor. Nothing else.

## Tooling setup

This repo doubles as the running example for Part 0: a real, minimal
`src/`-layout project. Set it up once:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"        # installs ruff, mypy, pytest
```

Sanity check:

```bash
ruff check .
mypy src
pytest                          # collecting nothing yet is fine
```

## The working method (assert-driven)

1. Read a concept snippet. The `#` comments state the gotcha or real
   behavior — they are the point, not decoration.
2. Copy the exercise scaffold (with its asserts) into a scratch file, e.g.
   `scratch.py`.
3. Replace the `...` with your implementation. The hint names a technique,
   never the answer.
4. Run `python scratch.py`. Silence means every assert passed — move on.
   An `AssertionError` means the asserts have more to teach you.
5. Don't peek ahead, don't look things up first. Attempt, fail, then look up.

Skills compound: later parts assume the idioms of earlier ones.

## The parts (work in order)

| Part | File | Covers |
|------|------|--------|
| 0 | [part-0.md](part-0.md) | Modern Python Project Structure (0.1–0.5) |
| I | [part-1.md](part-1.md) | Chapters 1–4 — Core Language Foundations |
| II | [part-2.md](part-2.md) | Chapters 5–8 — Writing Pythonic Code |
| III | [part-3.md](part-3.md) | Chapters 9–12 — Object-Oriented & Typed Python |
| IV | [part-4.md](part-4.md) | Chapters 13–16 — Structuring Real Projects |
| V | [part-5.md](part-5.md) | Chapters 17–20 — Engineering Practices |
| VI | [part-6.md](part-6.md) | Chapters 21–24 — Applied Python for the Role |
| VII | [part-7.md](part-7.md) | Chapters 25–28 — Closing the Loop for the Job Hunt |

The authoritative chapter map and content spec live in [SPEC.md](SPEC.md).
Build state lives in [PROGRESS.md](PROGRESS.md).
