---
id: RUL-CORE-0001
type: rule
origin: framework
since: 2.0.0
title: Never push; publishing to a remote is always manual
date: 2026-08-15
tags: [workflow, git, safety]
summary: An agent may commit and create local branches, but never pushes — every remote update is done by hand.
applies_to: every git operation in this repository, every session
---

<!-- ADF-MANAGED — framework record. Replaced on upgrade; do not edit. -->

## Rule
An agent may stage, commit, and create or delete **local** branches. An agent
must never run `git push` (with or without `--force`, `-u`, or a refspec), and
must not reach a remote by any other route: no `gh pr create`, `gh issue
create`, `gh release create`, `gh repo edit`, or API call that writes to the
remote. Read-only remote commands (`git fetch`, `git log origin/...`,
`gh issue view`, `gh pr view`) are fine and are how the agent picks up context.

Work is handed over by leaving the commit or branch local and saying plainly
what is ready and the exact command. The human runs it.

## Rationale
Pushing is the moment work becomes public and hard to retract — it can expose
content, trigger CI, notify watchers, and be mirrored or indexed even if the
branch is deleted afterward. That call belongs to the repository owner.

This rule is also what creates the parallel-actor condition behind
RUL-CORE-0002: once the human performs remote actions, the agent's picture of
remote state decays between turns.

## Exceptions
none. An explicit, in-the-moment instruction to push is an instruction to print
the command for the human to run.

## Adapting
If this project genuinely needs the agent to push, override it with a **project**
rule (`RUL-XXXX`) that names this record and states the narrower boundary. Do not
edit this file — an upgrade will overwrite it. Note that RUL-CORE-0002 still
applies: CI, teammates, and scheduled jobs are parallel actors too.
