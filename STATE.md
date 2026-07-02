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

Anti-drift system is populated and live (ANCHOR/SPEC/ARCHITECTURE/GLOSSARY/wiki
filled; repo git-initialized). Next: obtain and drop in part-1.md verbatim (the
never-edited style exemplar — see SPEC.md Open Questions), then author parts in
PROGRESS.md order through the verification gate.

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

- [ ] none — all workbook parts still `pending` in PROGRESS.md by design.

## Next

- [ ] Drop in part-1.md verbatim (canonical exemplar; never edit after) —
      blocked on its source, see Open Questions.
- [ ] Write part-0, then parts 2–7 in PROGRESS.md order, each through the
      verification gate (RUL-0002).

## Open Questions

- [ ] Where does the verbatim part-1.md exemplar come from? (Tracked in root
      SPEC.md Open Questions; resolving it should produce a DEC entry.)

## Blockers

- part-1.md source not yet provided — blocks part authoring start (part-0
  could proceed first if decided; that decision is open).

## Files touched this session

- `ANCHOR.md`, `SPEC.md`, `ARCHITECTURE.md`, `GLOSSARY.md` — populated from
  templates (SPEC drafted from `python-crash-course/SPEC.md`)
- `wiki/CON-0001..2, RUL-0001..3, DEC-0001..6` — real records replace the
  pipeline examples; `wiki/INDEX.md` regenerated
- `STATE.md` — this handoff
- repo git-initialized; scaffold committed

## Run / test commands

```bash
python3 wiki/build_index.py && python3 wiki/build_index.py --test
bash .claude/hooks/session-start.sh
cd python-crash-course && .venv/bin/ruff check . && .venv/bin/mypy src && .venv/bin/pytest
python3 tools/lint_workbook.py part-N.md   # from python-crash-course/
```
