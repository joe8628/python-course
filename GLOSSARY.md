# GLOSSARY.md — Canonical Terms

> One canonical name per concept. When you're about to name a new thing, check
> here first; add the term here the moment it's coined. Naming drift across
> sessions ("chunk" vs "segment" vs "passage") quietly fractures a codebase.
> If a term needs more than one line, give it a `wiki/CON-XXXX.md` concept page
> and link it from its row here.

| Term | Canonical meaning | Not to be confused with |
|------|-------------------|-------------------------|
| Part | One `part-N.md` file; a chapter range per the FILE → CHAPTER MAP | a Chapter (a part holds 4–5) |
| Chapter | A numbered unit (0–28) with 3–5 concepts | a Part; a Concept |
| Concept snippet | A fenced code example with ≥1 grounding comment and ≤2 sentences of prose | an Exercise (learner-solved) |
| Grounding comment | The in-snippet `#` comment stating the gotcha/real behavior ([CON-0002](wiki/CON-0002.md)) | a Hint; narration comments |
| Exercise | A `**Exercise N.x**` block the learner solves ([CON-0001](wiki/CON-0001.md)) | a Concept snippet |
| Scaffold | The `def`/`class` skeleton with `...` the learner fills in | a Solution (never shipped) |
| Hint | `# hint:` line naming the technique, never the answer | a Grounding comment; a leak |
| Refactor exercise | Rewrite-this exercise: bad working code + rewrite comment; assert-exempt | a solution leak (it isn't) |
| Verification gate | The per-part done-check: /tmp reference solutions green under pytest + clean lint ([RUL-0002](wiki/RUL-0002.md)) | the lint gate alone |
| Lint gate | `tools/lint_workbook.py` — mechanical style enforcement | the Verification gate (superset) |
| Exemplar | `part-1.md`, the verbatim canonical style file — never edited | a template to copy text from |
| Running example | The workbook's own src-layout project that Part 0 teaches from | a real application |
| Perishable claim | A statement whose truth depends on when a command last ran ([RUL-0005](wiki/RUL-0005.md)) | a durable fact (file content you just wrote) |
| Fresh read | A check run in the current turn, after the last event that could have changed the answer | a read from an earlier turn; a recalled value |
| Baseline | A declared version pinning `main` and `release` with paired tags ([DEC-0010](wiki/DEC-0010.md)) | the current tip of either branch |

---

## Perishable vocabulary — every term below demands a fresh read

> These are trigger words. Writing one about an externally-mutable artifact —
> an issue, PR, branch, tag, remote ref, or published file — requires that a
> check ran **in the same turn, after the last event that could have changed
> it**. No fresh read, no claim: describe what you last saw and say when you saw
> it, or run the check.
>
> **The test:** *could a command run outside this session change whether this
> sentence is true?* If yes, the sentence is a Perishable claim.

| Category | Trigger terms | Fresh read |
|----------|---------------|------------|
| Artifact lifecycle | open, closed, merged, unmerged, draft, ready, filed, reopened, landed, deleted, published, released, tagged | `gh issue view` · `gh pr view` · `git tag` |
| Local↔remote sync | pushed, unpushed, ahead, behind, diverged, in sync, level, up to date, tracked, upstream | `git fetch` then `git log origin/…` · `git status -sb` |
| Ref identity | tip, HEAD, points at, latest, current commit, SHA, "is at" | `git rev-parse` · `git log -1` |
| Completion | done, complete, finished, shipped, outstanding, remaining, blocked, pending, green, passing, failing, clean, dirty | the gate command itself, rerun |
| Recency adverbs | now, currently, already, still, no longer, just, yet, as of, at this point | whatever the adverb modifies |
| Derived quantities | commit counts, "N ahead", timestamps, byte sizes, list lengths | recompute; never carry a number forward |
| **Inference verbs** | should be, must have, by now, presumably, that means, which leaves, so it is, assuming | **none — these substitute for a read; replace with one** |

The last row is the most dangerous: those phrases *feel* like reasoning but are
stale reads wearing a disguise. A status table assembled from them reads as a
summary of work just done, which is why it slips past a check aimed at
"about to assert."

Claiming freshness you do not have — "verified just now", "re-read rather than
recalled" — is worse than stating a stale value plainly, because it removes the
reader's last cue to check for themselves. Never write it unless the command
output is in the same turn.

---

## Naming conventions

- Part files are `part-N.md`, N = 0–7; chapters are globally numbered 0–28.
- Exercises and concepts number as `N.x` within chapter N (Exercise 5.2 lives
  in chapter 5).
- Wiki records: `CON-XXXX` concepts, `RUL-XXXX` binding rules, `DEC-XXXX`
  decisions (status Rejected = rejected idea); four digits, zero-padded.
- PROGRESS.md states are exactly: `pending`, `written`, `verified`, `linted`.
