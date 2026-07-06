# ANCHOR.md — Always in Context

> The only project content loaded by default (pulled into CLAUDE.md via `@ANCHOR.md`).
> **Hard cap: one screen.** If it grows, push detail into SPEC / ARCHITECTURE /
> decisions and leave a one-line pointer here. Volatile state (current task) lives
> in STATE.md and is injected by the SessionStart hook — keep it out of this file.

## North Star

**Purpose (one sentence):**
An assert-driven Python proficiency workbook (`python-crash-course/`, 8 part
files, chapters 0–28) that re-skills an experienced-but-rusty engineer for a
professional Python developer role — every exercise verified mechanically
before it ships.

**This is NOT:**  *(anti-scope — drift violates these first)*
- a textbook — no long explanations, no analogies, no hand-holding, and
  **zero worked solutions anywhere in shipped files**
- beginner material — the reader has shipped software before
- a real application — `src/crash_course` is only Part 0's running example
- a platform — plain markdown + stdlib tooling; no site, video, or services

## Locked Decisions (Invariants)

> Non-negotiable. Do not contradict or re-open without an explicit instruction to
> do so. Each links to its full rationale in `wiki/<id>.md`.

- [LOCKED] Asserts ARE the spec; exercises ship as scaffold + `...` + hint + asserts — DEC-0001
- [LOCKED] Zero solutions in shipped files; hints name techniques only — DEC-0002 / RUL-0001
- [LOCKED] Only the repo-root CLAUDE.md governs; nested CLAUDE.md files banned — DEC-0003 / RUL-0003
- [LOCKED] No part ships without the verification gate (pytest-green asserts + lint) — DEC-0005 / RUL-0002
- [LOCKED] The workbook is a real src-layout project (hatchling; ruff/mypy/pytest must stay green) — DEC-0006
- [LOCKED] File→chapter map and PRE-DECIDED CHOICES in `python-crash-course/SPEC.md` are binding; part-1.md is the never-edited style exemplar
