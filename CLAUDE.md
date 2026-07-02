# CLAUDE.md

> Auto-loads every session; survives `/clear` and compaction. This is the
> **operating contract**. Keep it skimmable in under 60 seconds.
> Project invariants live in ANCHOR.md (imported just below); volatile state
> lives in STATE.md (injected by the SessionStart hook).

@ANCHOR.md

---

## Canonical Documents — retrieve on demand, never `cat` whole

| Doc | Read it when | How to read |
|-----|--------------|-------------|
| `SPEC.md` | Adding/changing a capability | by section (see its TOC) |
| `ARCHITECTURE.md` | Touching a boundary / contract / data flow | by section (see its TOC) |
| `wiki/INDEX.md` | **Before proposing any approach** | read index, then the one record |
| `wiki/<id>.md` | You need a concept, rule, or decision in full | single file |
| `STATE.md` | Start of every session | whole (it's small) |
| `GLOSSARY.md` | A term is ambiguous or you're naming something | lookup |

**Retrieval rule:** grep/section-read, don't bulk-read. For SPEC/ARCHITECTURE,
open only the heading you need. For the wiki, read `wiki/INDEX.md` first, then
fetch the single relevant record (`CON-`, `RUL-`, or `DEC-XXXX.md`). This keeps
context lean as the project grows.

---

## Compaction Directives

When compacting (auto or manual), preserve verbatim where possible:
1. The North Star and the full Locked Decisions list (from ANCHOR.md).
2. The Current Focus section of STATE.md.
3. Files modified this session and any test/run commands.
4. Unresolved open questions and blockers.

Discard freely: verbose tool output, full file dumps already on disk, and
exploratory tangents that changed no decision.

---

## Session Protocol

**Start:** run `/reground` (or rely on the SessionStart hook, which injects the
Current Focus). Restate the North Star, today's binding constraints, and the
current task before writing code.

**After any compaction / if context feels off:** run `/reground` before continuing.
Do not resume from memory alone.

**Decision made, idea rejected, or new concept/rule established:** create the
`wiki/` record from the matching `_TEMPLATE-*.md`, then run
`python3 wiki/build_index.py` to refresh the index — before moving on.

**End:** update STATE.md (done / in-progress / next / open questions / blockers /
files touched / run commands). Promote any now-permanent decision into ANCHOR.md's
Locked Decisions list.

---

## Drift Self-Check (before implementing anything)

- Conflicts with the North Star or a Locked Decision? → **stop and flag.**
- Re-introduces an idea from `wiki/INDEX.md`'s **Rejected Ideas**? → **stop and flag.**
- Violates a binding `RUL-XXXX` rule? → **stop and flag.**
- Violates a **Workbook Style Rule** (section below)? → **stop and flag.**
- Expands scope beyond SPEC.md? → **stop and ask.**
- About to create, edit, or follow a `CLAUDE.md` anywhere other than the repo
  root? → **stop.** This root file is the ONLY operating contract; nested
  `CLAUDE.md` files (e.g. `python-crash-course/CLAUDE.md`) were deliberately
  removed to prevent conflicting instructions. Never recreate them.

If unsure which decision applies, ask rather than guess. A wrong assumption that
compounds across sessions is the failure mode this file exists to prevent.

---

## Workbook Style Rules (pinned — apply to every part file in `python-crash-course/`)

> Migrated here from `python-crash-course/CLAUDE.md` (now deleted) so a single
> file governs. `SPEC.md`, `PROGRESS.md`, `part-N.md`, and `tools/` below all
> live under `python-crash-course/`.

- The asserts ARE the spec. Every shipped exercise: scaffold + `...` +
  asserts. Zero solutions anywhere — not in bodies, comments, or
  "solution" sections.
- Hints name the technique, never the answer: `# hint: generator
  expression inside sum()`, never the expression itself.
- Every concept snippet carries grounding comments stating the gotcha or
  real behavior (`# stop is exclusive`), at least one per concept.
- Prose budget: ≤2 sentences per concept, engineer-level, why/gotcha
  only. No analogies, no hand-holding.
- Modern Python 3.11+ only: `list[str]`, `match`, `:=`, dataclasses,
  pathlib, f-strings. Every snippet must parse.
- Numbering: Chapter N → N.x concept → Exercise N.x; chapters globally
  numbered per the FILE → CHAPTER MAP in `python-crash-course/SPEC.md`.
- Each part opens with a one-line framing of how its asserts work and
  closes with a short "How to work through this efficiently" paragraph.
- Before writing any part: reread part-1.md IN FULL — it is canonical
  style and your memory of it is stale after compaction.
- A part is done only when /tmp/verify_partN.py ran green under pytest
  AND tools/lint_workbook.py passes AND PROGRESS.md is updated.
- If an assert is unachievable or ambiguous, fix the assert — never
  compensate by leaking the answer in a hint.
- Refactor exercises (rewrite-this) are the only assert-exempt type.
- Never edit part-1.md.
