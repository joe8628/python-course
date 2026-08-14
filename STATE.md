# STATE.md — Current State & Handoff

> Read at the **start** of every session; rewrite at the **end** of every session.
> This is your fast recovery point after `/clear` or compaction. Keep it current
> over comprehensive — stale state is worse than none.

**Last updated:** 2026-08-14
**Active branch / worktree:** main (+ orphan branch `release`, local only)

---

## Current Focus

> The ONE thing in flight right now. One or two sentences. This is the line the
> compaction directives are told to preserve verbatim.

Content is built and awaits **hands-on review by Joe** — that review declares the
**v1.0 baseline** (VERSIONS.md). Nothing is pushed: `main` is 7 commits ahead of
origin and `release` exists only locally. After v1.0, all work runs the
production flow in DEC-0010 (GitHub Issue → draft PR → merge), and direct
authoring on `main` stops.

## Done (recent, relevant)

- [x] **Review finding (2026-08-14):** chapter 0 broke RUL-0001. `part-0.md`
      quoted this repo's complete `pyproject.toml` and `.gitignore` verbatim and
      every exercise was *verify this repo*, so the one competency Part 0 names —
      stand up a project — was never exercised. Parts 1–7 unaffected.
- [x] **part-0.md rewritten** (gate green: lint OK, `verify_part0.py` 3/3 under
      pytest): 0.1 builds the skeleton in a non-crashing order, 0.2 IS writing
      `pyproject.toml` (9 tomllib asserts), 0.3b runs both real install failure
      modes, 0.5 pins `.gitignore` by assert. Numbering still 0.1–0.5 per SPEC.
      Recorded as **DEC-0009**.
- [x] **README.md + HOW-TO-USE.md rewritten** — where files come from (`release`
      branch), one course folder, per-part `curl` as you reach each part.
- [x] **RUL-0004** — agents commit and branch locally; pushing is always manual.
      Pinned in CLAUDE.md's Session Protocol so it survives compaction.
- [x] **DEC-0010** — production flow: GitHub Issues tracks problems, a draft PR
      per ticket tracks the change, `release` is rebuilt from `main` and never
      merged into, baselines pin both branches with paired tags.
- [x] **VERSIONS.md** (baseline ledger) + **tools/build-release.sh** (repeatable
      `release` rebuild; idempotent, never touches the working tree).

## In Progress

- [ ] `release` branch: **not pushed** (RUL-0004) — that is the only thing
      outstanding on it. Content is current (byte-identical to `main`'s
      published files; `build-release.sh` reports no rebuild due).
      It is an **orphan by design**: no parent commit, no shared history with
      `main`, so the anti-drift system is absent from its history and not just
      its worktree (DEC-0009). Disjoint histories are expected — `release` moves
      only via `tools/build-release.sh`, never by merge.

## Next

- [ ] **Joe:** hands-on review → push both branches → declare v1.0. Exact tag
      and push commands are in VERSIONS.md ("Declaring a baseline"); set the
      ledger row's Status to `released` afterwards.
- [ ] First ticket under DEC-0010: the parts 1–7 "this repo" sweep below.
      File the issue first — no branch until the ticket exists.

## Open Questions

- [ ] Parts 1–7 still say "this repo" in places written under the pre-DEC-0009
      framing, where the repo *was* the student's project. Not audited this
      session. Should be a tracked ticket, fixed before the next release refresh.

## Blockers

- none

## Files touched this session

- `python-crash-course/part-0.md` — full rewrite (build-it-yourself)
- `python-crash-course/README.md` · `HOW-TO-USE.md` — download + one-folder model
- `python-crash-course/PROGRESS.md` — part-0 re-verification entry
- `VERSIONS.md` (new) · `tools/build-release.sh` (new)
- `wiki/DEC-0009.md` · `wiki/RUL-0004.md` · `wiki/DEC-0010.md` (new) · `wiki/INDEX.md`
- `CLAUDE.md` (Git rule) · `ANCHOR.md` (2 locked lines) · `STATE.md`

## Run / test commands

```bash
python3 wiki/build_index.py && python3 wiki/build_index.py --test
cd python-crash-course && python3 tools/lint_workbook.py part-0.md   # …part-7.md
cd python-crash-course && .venv/bin/pytest /tmp/verify_partN.py -q   # throwaway; recreate per gate
cd python-crash-course && uvx ruff check . && uvx mypy src
tools/build-release.sh            # rebuild `release` from main; no-op when unchanged
git rev-parse baseline/v1.0       # resolve a baseline tag once declared
```
