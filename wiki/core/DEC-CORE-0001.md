---
id: DEC-CORE-0001
type: decision
origin: framework
since: 2.0.0
title: Turn-start state refresh instead of vocabulary-triggered checks
status: Rejected
date: 2026-08-15
tags: [workflow, anti-drift]
summary: Rejected — a check at the top of the turn goes stale within the same turn; the trigger must be the words, not the clock.
supersedes:
superseded_by:
revisit_if: do not revisit
---

<!-- ADF-MANAGED — framework record. Replaced on upgrade; do not edit. -->

## Context
After the agent asserted stale PR state, the obvious fix was a mandatory status
probe at the start of every turn, optionally wrapped in a helper script.

## Decision
Rejected. A turn-start refresh reproduces the failure it was meant to prevent:
the agent reads once at the top, then makes claims minutes later, after edits,
commits, and possibly human action — with the same confident tone and a
now-stale snapshot. It converts "stale across turns" into "stale within a turn"
and adds a false sense of diligence.

## Alternatives considered
- Vocabulary-triggered checks (adopted, RUL-CORE-0002) — the trigger is each
  perishable word at the moment it is written, so it fires wherever in the turn
  the claim appears, however many times.
- A cached status file refreshed by a hook — rejected: same staleness, plus a
  second source of truth that can itself drift.

## Consequences
Checks are more frequent but always current. The cost is tolerable because the
read commands are cheap and read-only; the benefit is that no claim can outlive
its evidence.
