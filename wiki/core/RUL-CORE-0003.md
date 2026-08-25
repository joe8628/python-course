---
id: RUL-CORE-0003
type: rule
origin: framework
since: 2.0.0
title: Hand off one gated step at a time; never a block that spans a human action
date: 2026-08-15
tags: [workflow, safety, anti-drift]
summary: Commands given to the human stop at the first step whose success the agent cannot verify — later steps are withheld, not printed under an "after X" heading.
applies_to: every command handed to the human under RUL-CORE-0001
---

<!-- ADF-MANAGED — framework record. Replaced on upgrade; do not edit. -->

## Rule
When handing over commands, print only what can be run **now**. Stop at the
first step that depends on an outcome not yet verified — a merge, a review, a
deploy, a push landing.

- A prose heading (`## After merge`, "once this passes") is **not** a gate. A
  reader with a terminal open runs a contiguous block of commands. If a step
  must not run yet, do not print it yet.
- After the human reports back, verify the gating step actually completed
  (RUL-CORE-0002), then hand over the next block.
- When a command's success is not obvious from its own output, **say what the
  human should see**, so a silent no-op is distinguishable from success.

## Rationale
A release-rebuild block was printed under an `## After merge` heading directly
below the command that preceded it. It was run before the merge: the build
script read an unchanged branch and reported "nothing to do", and a checkout
silently reverted the working tree to pre-fix files — output that reads as a
broken tool or lost work, when the process had simply run out of order.

The originating bug in that same incident was itself a silent-success failure:
`curl -O` (capital O) misread as `-0`. Without `-O`, curl prints to stdout,
writes no file, and exits 0. Any command that can no-op silently needs its
success check shipped alongside it.

The agent cannot run these commands and cannot watch them run, so sequencing is
the only control it has. Withholding a step costs one message; a prematurely run
step costs a debugging detour and erodes trust in the tooling.

## Exceptions
Consecutive commands whose outcomes need no verification between them — creating
two labels, `git add` then `git commit` — may be printed as one block. The gate
is the need for verification, not the number of commands.
