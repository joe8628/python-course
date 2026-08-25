<!-- ADF-MANAGED FILE — framework-owned, v2.0.0.
     Replaced wholesale on upgrade. Do not edit; project rules go in CLAUDE.md. -->

# Core Operating Rules (framework)

> Imported by CLAUDE.md, so this is always in context. It holds the rules the
> **framework** owns; everything project-specific stays in CLAUDE.md and ANCHOR.md.

## Live-State Discipline

Semantic drift and state staleness fail differently. `/reground` fixes the first
by re-reading the durable record — it cannot fix the second, because those files
are themselves snapshots. **Because you don't run the remote commands, you don't
know their outcome:**

- **Perishable vocabulary triggers a fresh read (RUL-CORE-0002).** The trigger is
  the *word*, not your intent to assert. GLOSSARY.md's **Perishable vocabulary**
  table lists them: merged/open/draft, pushed/ahead/in sync, done/blocked/
  outstanding, now/already/still, commit counts — and the inference verbs that
  impersonate a read (*should be, must have, by now*). Writing one about an
  issue, PR, branch, tag, or remote ref requires the check to have run in the
  *same turn*, after the last event that could have changed it. Test: could a
  command run outside this session make this sentence false?
- **Never carry a status table forward, and never claim freshness you lack.**
  "Verified just now" is itself a perishable claim — permitted only with the
  command output in the same turn. A false freshness claim is worse than a stale
  value: it removes the reader's cue to check.
- **Hand over one gated step at a time (RUL-CORE-0003).** Print only what can run
  now; stop at the first step whose outcome you have not verified. An "after X"
  heading is not a gate — a contiguous block gets pasted whole. Say what success
  looks like when a command can no-op silently.
- **Surprising output → check the process first.** When something looks wrong,
  establish which workflow step is incomplete before explaining why a tool's
  output is technically correct.

**Drift Self-Check — additional gate.** Alongside the checks in CLAUDE.md:

- About to write a **Perishable vocabulary** term (GLOSSARY.md) without a fresh
  read in this turn, or to print commands that run past a step you haven't
  verified? → **stop and re-check** (RUL-CORE-0002 / RUL-CORE-0003).

## The `-CORE-` namespace

Wiki records with `-CORE-` in the ID (`RUL-CORE-0001`, `DEC-CORE-0001`, …) live
in `wiki/core/` and are shipped by the framework. They are replaced wholesale on
upgrade — **do not edit them**, and do not allocate `-CORE-` IDs. Project records
keep the plain numeric space (`RUL-0002`, `DEC-0003`) and are never touched by an
upgrade. Both appear in `wiki/INDEX.md` and are read the same way.
