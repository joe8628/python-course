# STATE.md — Current State & Handoff

> Read at the **start** of every session; rewrite at the **end** of every session.
> This is your fast recovery point after `/clear` or compaction. Keep it current
> over comprehensive — stale state is worse than none.

**Last updated:** 2026-08-14
**Active branch / worktree:** main (+ new orphan branch `release`, local only)

---

## Current Focus

> The ONE thing in flight right now. One or two sentences. This is the line the
> compaction directives are told to preserve verbatim.

Part 0 has been rewritten to build-it-yourself per DEC-0009 (it was shipping its
own answers), and the `release` branch now carries only verified, student-facing
files. Nothing is pushed — `release` exists locally and needs review before it
goes to origin.

## Done (recent, relevant)

- [x] **Review finding (2026-08-14):** chapter 0 broke RUL-0001. `part-0.md`
      quoted this repo's complete `pyproject.toml` and `.gitignore` verbatim and
      every exercise was *verify this repo*, so the one competency Part 0 names —
      stand up a project — was never exercised. Parts 1–7 unaffected.
- [x] **part-0.md rewritten** (gate green: lint OK, `verify_part0.py` 3/3 under
      pytest): 0.1 builds the skeleton in a non-crashing order, 0.2 IS writing
      `pyproject.toml` (9 tomllib asserts), 0.3b runs both real install failure
      modes, 0.5 pins `.gitignore` by assert. Numbering still 0.1–0.5 per SPEC.
- [x] **README.md + HOW-TO-USE.md rewritten** — where files come from (`release`
      branch), one course folder, per-part `curl` as you reach each part.
- [x] **DEC-0009** written + `wiki/build_index.py` rerun (self-test OK); ANCHOR
      Locked Decisions gained the one-line pointer.

## In Progress

- [ ] `release` branch: created locally as an orphan, content verified. **Not
      pushed.** Needs a human look before `git push -u origin release`.

## Next

- [ ] Review + push `release`; confirm the raw URLs in README/HOW-TO-USE resolve
      once it is on origin (they 404 until then).
- [ ] Decide whether refreshing `release` from `main` gets a script in `tools/`
      (DEC-0009 flags it as manual for now).

## Open Questions

- [ ] Parts 1–7 still say "this repo" in places written under the old framing.
      Not audited this session — worth a sweep before the next release refresh.

## Blockers

- none

## Files touched this session

- `python-crash-course/part-0.md` — full rewrite (build-it-yourself)
- `python-crash-course/README.md` · `HOW-TO-USE.md` — download + one-folder model
- `python-crash-course/PROGRESS.md` — part-0 re-verification entry
- `wiki/DEC-0009.md` (new) · `wiki/INDEX.md` (regenerated) · `ANCHOR.md`
- `STATE.md` — this handoff

## Run / test commands

```bash
python3 wiki/build_index.py && python3 wiki/build_index.py --test
cd python-crash-course && python3 tools/lint_workbook.py part-0.md   # …part-7.md
cd python-crash-course && .venv/bin/pytest /tmp/verify_part0.py -q   # throwaway; recreate per gate
cd python-crash-course && uvx ruff check . && uvx mypy src
git log --oneline release -1   # release branch: orphan, student-facing files only
```
