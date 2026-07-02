# Workbook Spec (authoritative — every session rereads this)

Audience: experienced-but-rusty engineer prepping for a Python developer
role at a multinational software corporation. This is a WORKBOOK, not a
textbook. part-1.md is the canonical style exemplar; never deviate.

## FILE → CHAPTER MAP (authoritative)
part-0.md: 0.1–0.5 (Modern Python Project Structure)
part-1.md: ch 1–4  (verbatim exemplar — never edit)
part-2.md: ch 5–8   | Part II  — Writing Pythonic Code
part-3.md: ch 9–12  | Part III — Object-Oriented & Typed Python
part-4.md: ch 13–16 | Part IV  — Structuring Real Projects
part-5.md: ch 17–20 | Part V   — Engineering Practices
part-6.md: ch 21–24 | Part VI  — Applied Python for the Role
part-7.md: ch 25–28 | Part VII — Closing the Loop for the Job Hunt

## CHAPTER CONTENTS
5 Functions, Arguments & Scope (*args/**kwargs, kw-only, default-arg trap,
  closures, LEGB)
6 Idiomatic Python (EAFP vs LBYL, unpacking, enumerate/zip, review-signal idioms)
7 Iterators & Generators (iterator protocol, laziness, yield, itertools)
8 Decorators & Context Managers (functools, with protocol, contextlib)
9 Classes & Objects (dunders, properties, class/instance/static methods)
10 Inheritance & Composition (MRO, mixins, ABCs, composition-over-inheritance)
11 Dataclasses & Modern Modeling (@dataclass, __slots__, enums, frozen)
12 Type Hints & Static Typing (generics, Optional/Union, Protocols, running mypy)
13 Errors & Exceptions (hierarchy, custom, EAFP handling, chaining)
14 Modules, Packages & Layout (imports, __init__, src layout, namespace pkgs)
15 Dependency & Environment Management (venvs, lockfiles, pyproject, packaging)
16 Logging & Debugging (logging done right, structured logs, pdb)
17 Testing (unit, fixtures, parametrization, mocking, coverage, TDD)
18 Code Quality & Tooling (formatters, linters, pre-commit, CI/CD fit)
19 Concurrency & Parallelism (threading vs multiprocessing vs async, GIL, asyncio)
20 Performance & Profiling (measure-first, profilers, complexity, caching)
21 Working with Data (JSON/CSV, serialization, REST, DB/ORM high level)
22 A Web Framework in Practice (FastAPI end-to-end)
23 Design Patterns & Clean Architecture (patterns worth knowing, SOLID, separation)
24 Security Essentials (input validation, secrets, common vuln classes)
25 System & Code Design Exercises
26 Coding Challenge Patterns
27 Reading & Reviewing Code
28 Capstone (production-shaped project: typing/tests/packaging/logging/CI)

## PRE-DECIDED CHOICES (do not relitigate)
- ch17: pytest only, no plugins beyond pytest itself.
- ch19: asserts check ordering/results, NEVER wall-clock timing.
- ch21: stdlib only (json, csv, sqlite3); no external services.
- ch22: FastAPI + TestClient, in-process; asserts framework-light.

## SIZE GUARDRAIL
3–5 concepts per chapter, 1–2 exercises per concept. If a chapter wants
more, cut concepts; never shrink grounding comments.

## EXERCISE TYPES
- Function-building exercises: scaffold + `...` + hint + asserts (the spec).
- Refactor exercises (rewrite-this-code): the ONLY assert-exempt type.

## CROSS-PART RULES
- Skills compound: later exercises may rely on earlier idioms; don't re-teach.
- Ch 14/15/18 overlap Part 0: Part 0 DEFINES structure; these chapters
  drill it with exercises. Reference back, never repeat.

## VERIFICATION GATE (per part, mechanical, non-negotiable)
1. Write /tmp/verify_partN.py: a reference solution per exercise + the
   EXACT asserts copied from the part file.
2. Run `pytest /tmp/verify_partN.py -q`; must be green; show output.
3. Run `python tools/lint_workbook.py part-N.md`; must pass.
4. Update PROGRESS.md; delete the /tmp file.
If an assert is unachievable/ambiguous, fix the assert in the part file —
never compensate by leaking the answer in a hint.

## DEFINITION OF DONE (whole repo)
- 9 part files + README + pyproject.toml, internally consistent.
- Zero worked solutions anywhere in shipped files.
- All snippets valid modern Python 3.11+; pyproject.toml valid.
- PROGRESS.md shows every part verified+linted.
