# STATE.md — Current State & Handoff

> Read at the **start** of every session; rewrite at the **end** of every session.
> This is your fast recovery point after `/clear` or compaction. Keep it current
> over comprehensive — stale state is worse than none.

**Last updated:** 2026-08-16
**Branches:** `main` (integration) · `release` (orphan distribution, DEC-0009)
— positions and sync: `git status -sb`, `git log origin/<branch>..<branch>`

---

<!-- ADF:BEGIN state-header v2.0.0 -->
> **Do not record perishable facts here.** Branch sync, PR/issue status, and test
> results are derivable and go stale silently — this file is injected into every
> session by the SessionStart hook, so a stale line is asserted as truth. Record
> *intent and decisions*; name the command that yields live state
> (RUL-CORE-0002). Identifiers are fine — a branch *name* is durable, its
> *position* is not.
>
> | Instead of | Write |
> |---|---|
> | "main is 7 commits ahead of origin" | sync: `git status -sb` |
> | "the branch is not pushed" | sync: `git log origin/<branch>..<branch>` |
> | "PR #12 is awaiting review" | PR #12 — status: `gh pr view 12` |
> | "tests are green" | gate: `<test command>` |
<!-- ADF:END state-header -->

## Current Focus

> The ONE thing in flight right now. One or two sentences. This is the line the
> compaction directives are told to preserve verbatim.

Content is built and awaits **hands-on review by Joe** — that review declares the
**v1.0 baseline** (VERSIONS.md; baseline status: `git tag`). All work now runs the
production flow in DEC-0010 (GitHub Issue → draft PR → merge); direct authoring
on `main` has stopped.

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
- [x] **RUL-CORE-0001** — agents commit and branch locally; pushing is always
      manual. Pinned in CLAUDE.md's Session Protocol so it survives compaction.
      (Was the project's RUL-0004 until the v2.0.0 framework upgrade absorbed it.)
- [x] **DEC-0010** — production flow: GitHub Issues tracks problems, a draft PR
      per ticket tracks the change, `release` is rebuilt from `main` and never
      merged into, baselines pin both branches with paired tags.
- [x] **VERSIONS.md** (baseline ledger) + **tools/build-release.sh** (repeatable
      `release` rebuild; idempotent, never touches the working tree).

## In Progress

- [ ] **Issue #3** — agent handoff rules (the `drafts/` convention plus the
      live-state rules the framework later absorbed). Branch
      `fix/3-handoff-rules`. Status: `gh issue view 3`, `gh pr list --head
      fix/3-handoff-rules`. Lands before the anti-drift upgrade below.
- [ ] **Anti-drift framework upgrade to v2.0.0.** Branch
      `chore/adf-upgrade-2.0.0`, stacked on `fix/3-handoff-rules`. Adds
      `wiki/core/` (`RUL-CORE-0001..0003`, `DEC-CORE-0001`),
      `.claude/core/RULES.md`, `.adf/`. Installed version: `python3
      .adf/upgrade.py --check`. **Rule retirement done in this branch:** the
      project's `RUL-0004`/`0005`/`0006` were deleted as exact duplicates of
      `RUL-CORE-0001`/`0002`/`0003`, every reference repointed, and the
      hand-written Perishable vocabulary section dropped in favour of the
      framework-managed block in `GLOSSARY.md`. The `-CORE-` records are
      framework-owned: replaced on upgrade, never edited here.

> `release` is an **orphan by design**: no parent commit, no shared history with
> `main`, so the anti-drift system is absent from its history and not just its
> worktree (DEC-0009). Disjoint histories are expected — it moves only via
> `tools/build-release.sh`, never by merge. Whether a rebuild is due:
> `tools/build-release.sh` (it is a no-op when current).

## Next

- [ ] **Joe:** hands-on review → declare v1.0. Tag and push commands are in
      VERSIONS.md ("Declaring a baseline"); set the ledger row's Status to
      `released` afterwards. Baseline status: `git tag`.
- [ ] Ticket for the parts 1–7 "this repo" sweep below. File the issue first —
      no branch until the ticket exists (DEC-0010).

## Open Questions

- [ ] Parts 1–7 still say "this repo" in places written under the pre-DEC-0009
      framing, where the repo *was* the student's project. Not audited this
      session. Should be a tracked ticket, fixed before the next release refresh.

## Blockers

- none

## Files touched this session

- `wiki/RUL-0004.md` · `RUL-0005.md` · `RUL-0006.md` (deleted) — retired as
  duplicates of `RUL-CORE-0001`/`0002`/`0003`; refs repointed
- `GLOSSARY.md` — framework Perishable vocabulary block replaces ours
- `CLAUDE.md` — live-state block removed (imported); `wiki/DEC-0010.md` ·
  `tools/build-release.sh` — repointed to RUL-CORE-0001
- `wiki/core/` · `.claude/core/RULES.md` · `.adf/` (new) — framework v2.0.0
- `STATE.md` — perishable facts replaced with the commands that derive them
- `drafts/` (gitignored) — issue/PR bodies + `ANTIDRIFT_UPDATE_PROMPT.md`

### Earlier (part-0 / issue #1, merged)

- `python-crash-course/part-0.md` — full rewrite (build-it-yourself)
- `python-crash-course/README.md` · `HOW-TO-USE.md` — download + one-folder model
- `python-crash-course/PROGRESS.md` — part-0 re-verification entry
- `VERSIONS.md` (new) · `tools/build-release.sh` (new)
- `wiki/DEC-0009.md` · `wiki/DEC-0010.md` (new) · `wiki/INDEX.md`
- `CLAUDE.md` (Git rule) · `ANCHOR.md` (2 locked lines) · `STATE.md`

## Run / test commands

```bash
python3 wiki/build_index.py && python3 wiki/build_index.py --test
cd python-crash-course && python3 tools/lint_workbook.py part-0.md   # …part-7.md
cd python-crash-course && .venv/bin/pytest /tmp/verify_partN.py -q   # throwaway; recreate per gate
cd python-crash-course && uvx ruff check . && uvx mypy src
tools/build-release.sh            # rebuild `release` from main; no-op when unchanged
python3 .adf/upgrade.py --check   # installed framework version + managed-region drift
bash .adf/detect.sh               # read-only: what scaffold this repo has
git rev-parse baseline/v1.0       # resolve a baseline tag once declared
```
