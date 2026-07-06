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

Parts 0–5 are authored, verified, and linted (chapters 0–20). Next: author
part-6 (ch 21–24, honoring the ch21 stdlib-only and ch22 FastAPI/TestClient
pre-decided choices), then part-7 — each rereading part-1.md IN FULL first and
passing the verification gate (RUL-0002) in a separate session.

## Done (recent, relevant)

- [x] Parts 0–5 through the full gate (author session + verify session each):
      reference solutions green under pytest, asserts copied byte-exact, lint
      clean, bash drills executed for real. No linter changes were needed after
      DEC-0007 — predict exercises are designed def-free to fit its exemption.
- [x] Repo fix from part-0 verification: `tests/test_smoke.py` added — an empty
      suite made bare `pytest` exit 5 (DEC-0008); part-0's 0.1 tree updated.
- [x] Part-0 content fixes found by verification: 0.3 checks `which python3`
      after deactivate (distro ships no bare `python`); 0.4 pre-commit entries
      cd in from the git root, where pre-commit actually runs.
- [x] Root `.gitignore` gained `.venv/` (user-created repo-root venv is the
      working env; install: `../.venv/bin/python -m pip install -e ".[dev]"`
      from python-crash-course/). pre-commit is installed in that venv.

## In Progress

- [ ] none — parts 0–5 `linted`; parts 6–7 and final-sweep `pending`.

## Next

- [ ] Author part-6.md (ch 21–24): ch21 stdlib-only (json/csv/sqlite3), ch22
      FastAPI + in-process TestClient, ch23 patterns/SOLID, ch24 security.
- [ ] Verify part-6 (separate session), then author + verify part-7 (ch 25–28,
      capstone), then final-sweep per SPEC's Definition of Done.

## Open Questions

- [ ] none

## Blockers

- none

## Files touched this session

- `python-crash-course/part-5.md` — authored (ch 17–20) and verified green
  (18/18; ch 17 mirrored at module level so given tests ran for real)
- `python-crash-course/PROGRESS.md` — part-5 -> linted
- `wiki/DEC-0008.md` + `wiki/INDEX.md` — smoke-test decision recorded, index rebuilt
- `STATE.md` — this handoff
- prior sessions this cycle: parts 0–4 authored/verified/committed
  (`e3172db`…`281aba4`), tests/test_smoke.py, root .gitignore

## Run / test commands

```bash
python3 wiki/build_index.py && python3 wiki/build_index.py --test
bash .claude/hooks/session-start.sh
cd python-crash-course && ../.venv/bin/ruff check . && ../.venv/bin/mypy src && ../.venv/bin/pytest
python3 tools/lint_workbook.py part-N.md    # from python-crash-course/
../.venv/bin/pytest /tmp/verify_part-N.py -q   # verification gate, then delete the file
```
