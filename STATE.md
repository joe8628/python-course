# STATE.md — Current State & Handoff

> Read at the **start** of every session; rewrite at the **end** of every session.
> This is your fast recovery point after `/clear` or compaction. Keep it current
> over comprehensive — stale state is worse than none.

**Last updated:** 2026-07-06
**Active branch / worktree:** main

---

## Current Focus

> The ONE thing in flight right now. One or two sentences. This is the line the
> compaction directives are told to preserve verbatim.

ALL parts (0–7, chapters 0–28) are authored, verified, and linted, and the
final integrity sweep is DONE — the workbook meets SPEC's Definition of Done.
Only remaining action: commit the uncommitted work (part-7, PROGRESS, sweep fixes).

## Done (recent, relevant)

- [x] Final integrity sweep (2026-07-06): lint clean on all 8 parts; part-1.md
      byte-identical to the e3172db exemplar (git-verified); zero solution
      leaks; numbering 0.1–0.5 + ch 1–28 gap/dupe-free and matches SPEC's map;
      all 98 cross-references valid and backward-only (5 prose previews aside);
      README links all 8 parts; ruff/mypy/tomllib/pytest all green.
- [x] Doc fix from the sweep: SPEC.md + ANCHOR.md said "9 part files" —
      corrected to 8 (part-0…part-7), matching the authoritative FILE → CHAPTER
      MAP. No pedagogy changed; no part file edited.
- [x] Parts 6 and 7 authored + verified in prior sessions (see PROGRESS.md
      entries dated 2026-07-06); parts 0–5 committed through `dfc3159`.

## In Progress

- [ ] none — every PROGRESS.md line is `linted`; final-sweep is `done`.

## Next

- [ ] Commit: `python-crash-course/part-7.md` (new content), `PROGRESS.md`
      (part-7 + final-sweep entries), `SPEC.md` + `ANCHOR.md` (9→8 fix),
      `STATE.md`. Then the project is complete per SPEC's Definition of Done.

## Open Questions

- [ ] none

## Blockers

- none

## Files touched this session

- `python-crash-course/SPEC.md` — Definition of Done: "9 part files" → 8
- `ANCHOR.md` — North Star: "9 part files" → 8
- `python-crash-course/PROGRESS.md` — final-sweep: pending → done (with audit log)
- `STATE.md` — this handoff

## Run / test commands

```bash
python3 wiki/build_index.py && python3 wiki/build_index.py --test
bash .claude/hooks/session-start.sh
cd python-crash-course && python3 tools/lint_workbook.py part-0.md part-1.md part-2.md part-3.md part-4.md part-5.md part-6.md part-7.md
cd python-crash-course && .venv/bin/pytest -q          # local venv: pytest+fastapi+httpx (no ruff/mypy)
cd python-crash-course && uvx ruff check . && uvx mypy src   # root .venv is gone; uvx works
```
