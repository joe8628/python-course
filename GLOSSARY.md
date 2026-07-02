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

---

## Naming conventions

- Part files are `part-N.md`, N = 0–7; chapters are globally numbered 0–28.
- Exercises and concepts number as `N.x` within chapter N (Exercise 5.2 lives
  in chapter 5).
- Wiki records: `CON-XXXX` concepts, `RUL-XXXX` binding rules, `DEC-XXXX`
  decisions (status Rejected = rejected idea); four digits, zero-padded.
- PROGRESS.md states are exactly: `pending`, `written`, `verified`, `linted`.
