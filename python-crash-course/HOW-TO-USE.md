# How to Use This Course — Step by Step

A practical walkthrough for working the workbook from setup to capstone.
For what the course *is*, read [README.md](README.md); this file is about
*how to work it*.

---

## Step 1 — Confirm you're the intended reader

- You have shipped software before, in any language. The course reactivates
  and modernizes; it does not teach programming.
- You have Python **3.11+** (`python3 --version`), a terminal, and an editor.
  Nothing else is required.

## Step 2 — Set up the repo once

The repo is itself a real `src/`-layout project (it's Part 0's running
example), so set it up like one:

```bash
cd python-crash-course
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"        # installs ruff, mypy, pytest
```

Sanity check — all three should succeed:

```bash
ruff check .
mypy src
pytest                          # a near-empty suite passing is expected
```

## Step 3 — Create a scratch file

All exercise work happens in a throwaway file, e.g. `scratch.py` at the repo
root (or anywhere outside `src/`). You will overwrite it constantly; it is
never committed and never graded — the asserts inside it are the grading.

## Step 4 — Work Part 0 first

Open [part-0.md](part-0.md). It defines modern project structure
(`pyproject.toml`, `src/` layout, dev extras) using this very repo as the
example. Later chapters (14, 15, 18) drill this material and assume you've
seen it — don't skip it, even if packaging feels familiar.

## Step 5 — The core loop (repeat for every exercise)

1. **Read the concept snippet.** The `#` comments state the gotcha or real
   behavior — they are the teaching payload, not decoration.
2. **Copy the exercise scaffold into `scratch.py`**, asserts included. The
   asserts ARE the spec: they define exactly what "correct" means.
3. **Replace the `...` with your implementation.** The hint names a
   technique (`# hint: generator expression inside sum()`), never the answer.
4. **Run it:** `python scratch.py`.
   - **Silence** = every assert passed. Move on.
   - **`AssertionError`** = read the failing assert; it tells you what
     behavior you're missing. Fix and rerun.
5. **Attempt before you look anything up.** The order is: attempt → fail →
   *then* consult docs. Failing an assert first is what makes the lookup
   stick.

There are no worked solutions anywhere in this repo, by design. The asserts
are the only oracle, and they are sufficient.

## Step 6 — Handle the two exercise types

- **Function-building** (the default): scaffold + `...` + hint + asserts.
  Done when the asserts pass silently.
- **Refactor ("rewrite this code")**: the only type without asserts. Rewrite
  the given code idiomatically, then judge your version against the chapter's
  concepts. If your rewrite doesn't use the idiom the chapter just taught,
  it isn't done.

## Step 7 — Go in order, and don't re-read backward

Work the parts strictly in sequence:

| Order | File | Covers |
|-------|------|--------|
| 0 | [part-0.md](part-0.md) | Modern Python Project Structure |
| 1 | [part-1.md](part-1.md) | Ch 1–4 — Reactivating the Fundamentals |
| 2 | [part-2.md](part-2.md) | Ch 5–8 — Writing Pythonic Code |
| 3 | [part-3.md](part-3.md) | Ch 9–12 — Object-Oriented & Typed Python |
| 4 | [part-4.md](part-4.md) | Ch 13–16 — Structuring Real Projects |
| 5 | [part-5.md](part-5.md) | Ch 17–20 — Engineering Practices |
| 6 | [part-6.md](part-6.md) | Ch 21–24 — Applied Python for the Role |
| 7 | [part-7.md](part-7.md) | Ch 25–28 — Closing the Loop for the Job Hunt |

Skills compound: later exercises silently rely on earlier idioms
(comprehensions, dataclasses, type hints) without re-teaching them. If a
later exercise feels impossible, the gap is usually an earlier chapter —
go redo *that exercise*, not the whole part.

## Step 8 — Use the toolchain as you go, not at the end

From Part III onward, make `mypy` and `ruff` part of your loop: type your
scratch solutions and run `mypy scratch.py` and `ruff check scratch.py`
alongside `python scratch.py`. From Chapter 17 onward, write exercise
solutions as pytest tests when the scaffold is test-shaped. Tool fluency is
part of what the course trains — running the tools *is* the exercise.

## Step 9 — When you're stuck

- Reread the failing assert literally. It encodes the exact expected
  behavior, including edge cases you may have skipped.
- Reread the concept snippet's `#` comments — the gotcha you're hitting is
  usually stated there.
- Reread the hint and search the *named technique* in the official docs,
  not the exercise text.
- Still stuck after a real attempt? Move on and return. Do not hunt for
  solutions online — recognizing an answer teaches nothing; producing one
  does.

## Step 10 — Finish with the capstone

Chapter 28 (in [part-7.md](part-7.md)) is a production-shaped project:
typing, tests, packaging, logging, CI. It deliberately exercises everything
before it. Treat it as your proof of readiness — if the capstone goes
smoothly, you're prepared for the role this course targets.

---

## Pacing guideline

One chapter per sitting is a sustainable default (3–5 concepts, 1–2
exercises each). Speed matters less than never skipping the
attempt-fail-lookup loop — that loop is the entire mechanism of the course.
