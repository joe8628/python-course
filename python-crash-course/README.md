# Python Proficiency Crash Course

A workbook — not a textbook — for the experienced-but-rusty engineer prepping
for a Python developer role. Every concept is a short, grounded code snippet;
every exercise is a scaffold whose **asserts are the spec**. You write the body
until the asserts pass. No worked solutions exist anywhere in this course.

## Prerequisites

- You have shipped software before, in some language. This course does not
  teach programming; it teaches *modern Python* to someone who can already code.
- Python **3.11+** installed (`python3 --version`).
- A terminal, an editor, and `git`. Nothing else.

## Getting the course

The parts are published on the **`release` branch**: only files that have passed
the verification gate, with none of the authoring machinery. You are never one
`curl` away from an unfinished part or a spec you have no use for.

There is one directory for the whole course — Part 0 has you create it, and every
part file you download lands in it, next to the code you write:

```bash
mkdir -p ~/projects/crash-course && cd ~/projects/crash-course
curl -O https://raw.githubusercontent.com/joe8628/python-course/release/part-0.md
ls part-0.md
```

That flag is `-O` — a capital letter **O**, not a zero. It is what saves the
response to a file named after the URL; without it `curl` prints the whole part
to your terminal and writes nothing. That is why `ls` is the third line: a
failed download still exits `0`, so seeing the filename is the only proof.

Fetch each later part the same way when you reach it — same URL, same folder,
part number changed. Nothing carries over between commands, so it works just as
well weeks from now in a new terminal.

Prefer everything up front? `git clone --branch release --single-branch
https://github.com/joe8628/python-course.git` and work inside that clone — but
one part at a time is the better default: it keeps you from skimming ahead, and
the release branch is where corrections land, so a part fetched later is fresher.

By the end you have a single folder holding your package, its tests, your scratch
file, and the parts you've worked. There is nothing to install before Part 0 —
building it *is* Part 0.

## The working method (assert-driven)

1. Read a concept snippet. The `#` comments state the gotcha or real
   behavior — they are the point, not decoration.
2. Copy the exercise scaffold (with its asserts) into a scratch file, e.g.
   `scratch.py`, in your project.
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
| I | [part-1.md](part-1.md) | Chapters 1–4 — Reactivating the Fundamentals |
| II | [part-2.md](part-2.md) | Chapters 5–8 — Writing Pythonic Code |
| III | [part-3.md](part-3.md) | Chapters 9–12 — Object-Oriented & Typed Python |
| IV | [part-4.md](part-4.md) | Chapters 13–16 — Structuring Real Projects |
| V | [part-5.md](part-5.md) | Chapters 17–20 — Engineering Practices |
| VI | [part-6.md](part-6.md) | Chapters 21–24 — Applied Python for the Role |
| VII | [part-7.md](part-7.md) | Chapters 25–28 — Closing the Loop for the Job Hunt |

A step-by-step guide to working the course lives in [HOW-TO-USE.md](HOW-TO-USE.md).
