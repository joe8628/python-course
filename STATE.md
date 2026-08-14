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

Content is built and now awaits **hands-on review by Joe** — that review is what
declares the **v1.0 baseline** (VERSIONS.md, DEC-0010). Nothing is pushed:
`main` is ahead by several commits and `release` exists only locally. After
v1.0, work moves to one-PR-per-issue; no more direct authoring on `main`.

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
      pushed, and never will be by an agent** — RUL-0004: commits are an agent's
      job, pushing is the human's. Waiting on `git push -u origin release`.

## Next

- [ ] **Joe:** hands-on review, then push both branches and declare v1.0 —
      exact tag + push commands are in VERSIONS.md ("Declaring a baseline").
- [ ] Confirm the raw URLs in README/HOW-TO-USE resolve once `release` is on
      origin; they 404 until then, **and only work at all if the repo is
      public** (never verified — the visibility check was declined).
- [ ] First PR under DEC-0010 will be the parts 1–7 "this repo" sweep below.

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
