# STATE.md — Current State & Handoff

> Read at the **start** of every session; rewrite at the **end** of every session.
> This is your fast recovery point after `/clear` or compaction. Keep it current
> over comprehensive — stale state is worse than none.

**Last updated:** 2026-07-01
**Active branch / worktree:** main

---

## Current Focus

> The ONE thing in flight right now. One or two sentences. This is the line the
> compaction directives are told to preserve verbatim.

part-1.md exemplar is in — verbatim, verified (12/12 asserts green), linted;
the lint gate is calibrated to it (DEC-0007). Next: author part-0, then parts
2–7 in PROGRESS.md order, each rereading part-1.md IN FULL first and passing
the verification gate (RUL-0002).

## Done (recent, relevant)

- [x] Created `python-crash-course/` scaffold: SPEC.md, PROGRESS.md, README.md,
      pyproject.toml, src/crash_course/ stub, tools/lint_workbook.py,
      part-0..7 H1-only placeholders, .gitignore, .venv with dev extras.
- [x] Verified: pyproject parses (tomllib), ruff/mypy/pytest run clean,
      lint_workbook.py passes on placeholders and catches planted violations.
- [x] Migrated workbook style rules into the root CLAUDE.md (single operating
      contract — DEC-0003/RUL-0003); nested CLAUDE.md deleted (DEC-0004).
- [x] Populated the anti-drift system per SETUP.md: ANCHOR.md (north star,
      anti-scope, 6 locked decisions), root SPEC.md (FR-1..7, NFRs, non-goals;
      drafted from python-crash-course/SPEC.md), ARCHITECTURE.md (components,
      data flow, contracts), GLOSSARY.md (12 terms), wiki (CON-0001/2,
      RUL-0001/2/3, DEC-0001..6 incl. 2 rejected ideas), INDEX.md rebuilt.

## In Progress

- [ ] none — part-1 is `linted`; all other parts `pending`.

## Next

- [ ] Author part-0, then parts 2–7 in PROGRESS.md order, each rereading
      part-1.md IN FULL first and passing the verification gate (RUL-0002).

## Open Questions

- [ ] none

## Blockers

- none

## Files touched this session

- `python-crash-course/part-1.md` — verbatim exemplar dropped in (now frozen)
- `python-crash-course/tools/lint_workbook.py` — calibrated to the exemplar
  (DEC-0007): refactor/predict exercises exempt from `...`/assert checks;
  `...` exercise blocks tolerate SyntaxError
- `python-crash-course/PROGRESS.md` — part-1 -> linted, linter change noted
- `python-crash-course/README.md` — part-1 title matched to the exemplar
- `wiki/DEC-0007.md` + `wiki/INDEX.md` — decision recorded, index rebuilt
- root `SPEC.md` — part-1 open question resolved; `STATE.md` — this handoff
- previous sessions: anti-drift docs populated, wiki seeded, repo
  git-initialized and scaffold committed (`ea8cdc1`)

## Run / test commands

```bash
python3 wiki/build_index.py && python3 wiki/build_index.py --test
bash .claude/hooks/session-start.sh
cd python-crash-course && .venv/bin/ruff check . && .venv/bin/mypy src && .venv/bin/pytest
python3 tools/lint_workbook.py part-N.md   # from python-crash-course/
```
