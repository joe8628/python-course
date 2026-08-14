# VERSIONS.md — Baseline ledger

> One row per baseline. A baseline pins **both** branches at once: the `main`
> commit that was reviewed, and the `release` commit derived from it. Tags are
> the link; this file is the human-readable record of what each one contains.
>
> Tag scheme — `baseline/vX.Y` on `main`, `release/vX.Y` on `release`.
> Resolve either to its commit with `git rev-parse baseline/v1.0`.
> Full recipe and rationale: DEC-0010.

| Version | Date | Status | `main` tag | `release` tag | Scope |
|---------|------|--------|------------|---------------|-------|
| v1.0 | 2026-08-14 | **pending hands-on review** | `baseline/v1.0` | `release/v1.0` | First reviewed baseline. Chapters 0–28 across 8 parts, all verified and linted; Part 0 rewritten build-it-yourself (DEC-0009); `release` established as the orphan distribution branch. |

## Declaring a baseline

Run after the hands-on review passes, from a clean tree, with both branches at
the commits you intend to freeze:

```bash
git tag -a baseline/v1.0 main    -m "v1.0 baseline — reviewed by hand"
git tag -a release/v1.0 release  -m "v1.0 release — derived from baseline/v1.0"
git push origin main release            # branches first
git push origin baseline/v1.0 release/v1.0
```

Then set this file's Status column to `released` and record anything the review
changed. If the review moves either branch, move the tag with `git tag -f` —
tags are cheap until pushed, and a pushed tag should never be moved.

## Numbering

- **MINOR** (`v1.1`, `v1.2`) — a batch of merged fixes; content corrections,
  clarified instructions, assert repairs.
- **MAJOR** (`v2.0`) — structural change to how the course is worked: chapter
  map, exercise format, distribution model.

A baseline is only declared once `main` is green (every part linted, its verify
file pytest-green per RUL-0002) **and** `release` has been rebuilt from that
exact `main` commit.
