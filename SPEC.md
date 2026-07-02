# SPEC.md — Source of Truth for Intent

> The **what** and **why**. When code and this document disagree, this document
> wins (or this document is wrong and must be updated first, explicitly).
> Update via a normal edit; significant changes should also add a `wiki/DEC-XXXX.md` entry.
>
> **Read by section, not whole.** Jump to the heading you need:
> Problem · Purpose · Consumers · Functional Requirements · Non-Functional
> Requirements · Success Criteria · Non-Goals · Open Questions.
>
> **Layering:** this file is the *project* spec. Chapter-level content detail
> (the FILE → CHAPTER MAP, per-chapter topics, PRE-DECIDED CHOICES, size
> guardrail, verification-gate steps) lives in `python-crash-course/SPEC.md`,
> which is authoritative at that level — reference it, never duplicate it.

**Last reviewed:** 2026-07-01

---

## Problem

An experienced-but-rusty engineer is prepping for a Python developer role at a
multinational software corporation. Textbooks are too slow and passive;
tutorials are too shallow and beginner-oriented. Reading solutions does not
rebuild recall — writing code against a checkable target does. There is no
compact, verifiable, modern-Python (3.11+) drill path for someone who can
already code.

## Purpose & Outcome

A self-contained workbook in `python-crash-course/`: 9 markdown part files
covering project structure (Part 0) and chapters 1–28, where every concept is
a short grounded snippet and every exercise is a scaffold whose asserts define
correctness. Worked end to end, it leaves the reader interview- and job-ready
in idiomatic, typed, tested, production-shaped Python — with zero solutions
ever shipped, because every assert was proven achievable before release.

## Consumers / Interfaces

- **The learner** — reads `part-N.md` in order, copies exercise scaffolds into
  scratch files, runs them until the asserts pass silently.
- **Authoring sessions (Claude Code)** — write part files under the root
  CLAUDE.md's Workbook Style Rules and the verification gate (RUL-0002).
- **`tools/lint_workbook.py`** — CLI gate; takes part-file paths, exits 1 on
  any style violation.
- **The toolchain** (`ruff check .`, `mypy src`, `pytest`) — runs against the
  workbook's own src-layout project, which doubles as Part 0's running example.

---

## Functional Requirements

> Number these so decisions and code can reference them (FR-1, FR-2 …).

- **FR-1:** Ship 9 part files (`part-0.md`–`part-7.md` + part-1 exemplar)
  covering exactly the FILE → CHAPTER MAP in `python-crash-course/SPEC.md`
  (Part 0 structure; chapters 1–28 through the Part VII capstone).
- **FR-2:** Every chapter delivers 3–5 concepts, each a snippet with ≥1
  grounding comment (CON-0002) and ≤2 sentences of prose, plus 1–2 exercises
  per concept.
- **FR-3:** Every function-building exercise ships as scaffold + `...` +
  technique-naming hint + asserts (DEC-0001); refactor exercises are the only
  assert-exempt type (CON-0001).
- **FR-4:** The workbook directory is a real, valid src-layout project
  (`pyproject.toml`, `src/crash_course/`, dev extras) that Part 0 teaches from
  and chapters 14/15/18 reference back to (DEC-0006).
- **FR-5:** `tools/lint_workbook.py` mechanically enforces the style rules
  (placeholders, asserts, grounding comments, numbering, parseability,
  solution-leak ban) with `file:line` output and exit 1 on failure.
- **FR-6:** Each part passes the verification gate before shipping: reference
  solutions green under pytest against the part's exact asserts, then a clean
  lint run (RUL-0002).
- **FR-7:** `python-crash-course/PROGRESS.md` tracks every part through
  pending → written → verified → linted.

## Non-Functional Requirements

- **Correctness:** every fenced snippet parses as Python 3.11+; every shipped
  assert is proven achievable (gate, FR-6); `pyproject.toml` always valid TOML.
- **Zero-solution guarantee:** no worked solutions anywhere in shipped files —
  lint-enforced (RUL-0001), including hint leaks and "solution" headings.
- **Self-containedness:** stdlib-only tooling for the lint gate; course content
  needs only Python 3.11+ and the dev extras (ruff, mypy, pytest; FastAPI only
  for chapter 22).
- **Reproducibility:** the toolchain (`ruff check .`, `mypy src`, `pytest`)
  runs clean at all times on a fresh `pip install -e ".[dev]"`.
- **Compactness:** size guardrail per `python-crash-course/SPEC.md` — cut
  concepts before shrinking grounding comments; prose budget ≤2 sentences.

## Success Criteria (Definition of Done)

- [ ] 9 part files + README + pyproject.toml, internally consistent (FR-1, FR-4).
- [ ] Zero worked solutions anywhere in shipped files (RUL-0001).
- [ ] All snippets valid modern Python 3.11+; pyproject.toml valid TOML.
- [ ] PROGRESS.md shows every part verified + linted (FR-6, FR-7).
- [ ] `ruff check .`, `mypy src`, `pytest` all green on the workbook project.

---

## Non-Goals (Anti-Scope)

> Explicitly out of scope. Re-state the most tempting ones; these are the
> features that quietly creep in across sessions.

- No textbook prose: no analogies, no hand-holding, no long explanations
  (DEC-0002 — the most tempting drift).
- No worked solutions, answer keys, or "solutions" sections, ever (RUL-0001).
- No beginner content — the reader has shipped software before.
- No external services, databases, or network dependencies in exercises
  (chapter 21 is stdlib-only; chapter 22 is in-process TestClient).
- No delivery platform: no website, notebooks, videos, or interactive runner —
  plain markdown worked in an editor + terminal.
- No expansion of `src/crash_course` into a real library; it stays a stub
  teaching prop for Part 0.

## Open Questions

> Unresolved spec-level questions. Resolving one usually produces a `wiki/DEC-XXXX.md` entry.

- [x] ~~part-1.md exemplar source~~ — resolved 2026-07-01: provided by the user
  and dropped in verbatim; verified (12/12 asserts green) and linted. The lint
  gate was calibrated to it (DEC-0007). part-1.md is now frozen (never edit).
- [ ] none open.
