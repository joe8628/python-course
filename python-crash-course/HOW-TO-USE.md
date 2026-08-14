# How to Use This Course — Step by Step

A practical walkthrough for working the workbook from setup to capstone.
For what the course *is*, read [README.md](README.md); this file is about
*how to work it*.

---

## Step 1 — Confirm you're the intended reader

- You have shipped software before, in any language. The course reactivates
  and modernizes; it does not teach programming.
- You have Python **3.11+** (`python3 --version`), `git`, a terminal, and an
  editor. Nothing else is required.

## Step 2 — Create the course folder and download Part 0

The parts live on the **`release` branch**: only files that have passed the
verification gate, none of the authoring machinery. Everything you do — reading
and writing alike — happens in one directory, which you create now and build
out in Part 0:

```bash
mkdir -p ~/projects/crash-course && cd ~/projects/crash-course
BASE=https://raw.githubusercontent.com/joe8628/python-course/release
curl -O $BASE/part-0.md          # start here; fetch part-1.md when Part 0 is done
```

Prefer everything up front? `git clone --branch release --single-branch
https://github.com/joe8628/python-course.git ~/projects/crash-course` and build
Part 0 inside that clone. One part at a time is the better default: it keeps you
from skimming ahead, and the release branch is where corrections land, so a part
fetched later is a part fetched fresher.

## Step 3 — Know what that folder becomes

By the end, the one directory holds both halves of the course:

| In `~/projects/crash-course/` | What it is | You edit it? |
|-------------------------------|------------|--------------|
| `part-0.md` … `part-7.md` | the parts you've downloaded so far | no |
| `pyproject.toml`, `src/`, `tests/`, `.venv/` | the project you build in Part 0 | yes |
| `scratch.py` | where every exercise gets worked | yes, constantly |

There is nothing to install before Part 0. You do not `pip install` the
workbook; it is markdown sitting in the folder. Every command in the course
runs from that folder's root.

## Step 4 — Work Part 0 first, and actually build it

Open [part-0.md](part-0.md). Part 0 is not a tour of a finished project — it
has you create one from an empty directory: package layout, `pyproject.toml`,
venv, editable install, ruff/mypy/pytest, pre-commit, `.gitignore`. Exercise
0.2 (writing `pyproject.toml` until its asserts pass) is the spine of the
part; everything after it depends on that file being right.

Do not skip Part 0 even if packaging feels familiar. Chapters 14, 15, and 18
drill this material and assume you built it once by hand.

## Step 5 — Create a scratch file

From Part 1 on, all exercise work happens in a throwaway file — `scratch.py`
at your project root (anywhere outside `src/`). You will overwrite it
constantly; it is never committed and never graded — the asserts inside it
are the grading.

## Step 6 — The core loop (repeat for every exercise)

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

There are no worked solutions anywhere in this course, by design. The asserts
are the only oracle, and they are sufficient.

## Step 7 — Handle the two exercise types

- **Function-building** (the default): scaffold + `...` + hint + asserts.
  Done when the asserts pass silently.
- **Refactor ("rewrite this code")**: the only type without asserts. Rewrite
  the given code idiomatically, then judge your version against the chapter's
  concepts. If your rewrite doesn't use the idiom the chapter just taught,
  it isn't done.

## Step 8 — Go in order, and don't re-read backward

Work the parts strictly in sequence, fetching each as you reach it:

| Order | File | Covers |
|-------|------|--------|
| 0 | part-0.md | Modern Python Project Structure |
| 1 | part-1.md | Ch 1–4 — Reactivating the Fundamentals |
| 2 | part-2.md | Ch 5–8 — Writing Pythonic Code |
| 3 | part-3.md | Ch 9–12 — Object-Oriented & Typed Python |
| 4 | part-4.md | Ch 13–16 — Structuring Real Projects |
| 5 | part-5.md | Ch 17–20 — Engineering Practices |
| 6 | part-6.md | Ch 21–24 — Applied Python for the Role |
| 7 | part-7.md | Ch 25–28 — Closing the Loop for the Job Hunt |

```bash
curl -O $BASE/part-3.md          # same BASE as Step 2; substitute the part you've reached
```

Skills compound: later exercises silently rely on earlier idioms
(comprehensions, dataclasses, type hints) without re-teaching them. If a
later exercise feels impossible, the gap is usually an earlier chapter —
go redo *that exercise*, not the whole part.

## Step 9 — Use the toolchain as you go, not at the end

From Part III onward, make `mypy` and `ruff` part of your loop: type your
scratch work and run `mypy scratch.py` and `ruff check scratch.py` alongside
`python scratch.py`. From Chapter 17 onward, write exercise work as pytest
tests when the scaffold is test-shaped. Tool fluency is part of what the
course trains — running the tools *is* the exercise.

## Step 10 — When you're stuck

- Reread the failing assert literally. It encodes the exact expected
  behavior, including edge cases you may have skipped.
- Reread the concept snippet's `#` comments — the gotcha you're hitting is
  usually stated there.
- Reread the hint and search the *named technique* in the official docs,
  not the exercise text.
- Still stuck after a real attempt? Move on and return. Do not hunt for
  answers online — recognizing one teaches nothing; producing one does.

## Step 11 — Finish with the capstone

Chapter 28 (in part-7.md) is a production-shaped project: typing, tests,
packaging, logging, CI. It deliberately exercises everything before it. Treat
it as your proof of readiness — if the capstone goes smoothly, you're
prepared for the role this course targets.

---

## Pacing guideline

One chapter per sitting is a sustainable default (3–5 concepts, 1–2
exercises each). Speed matters less than never skipping the
attempt-fail-lookup loop — that loop is the entire mechanism of the course.
