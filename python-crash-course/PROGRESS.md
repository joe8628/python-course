# Build state (update at end of every session)
part-1: linted    # verbatim exemplar dropped in 2026-07-01; verify green (12/12 under pytest).
                  # Linter change (exemplar is ground truth): `...`/assert checks now apply only
                  # to function-building exercises — refactor/predict exercises (no def/class
                  # scaffold + rewrite/refactor/predict/convert instruction) are exempt from
                  # both; exercise blocks containing `...` tolerate SyntaxError (a placeholder
                  # may occupy a grammar-required position, e.g. the body of `match`).
part-0: linted    # 2026-07-02; verify green (2/2: exercises 0.2/0.5 under pytest); every
                  # command-based verify-it executed for real against this repo, incl. the
                  # 0.4a break-the-gates drill (F401/return-value/B006 each caught by the
                  # predicted tool) and 0.4b pre-commit run --all-files. Repo fix: added
                  # tests/test_smoke.py — an empty suite made bare `pytest` exit 5, breaking
                  # 0.4a/0.4b as written. Part fixes found by verification: 0.1 tree gained
                  # tests/; 0.3 checks `which python3` after deactivate (this distro ships
                  # no bare `python`); 0.4 hook entries cd in from the git root, where
                  # pre-commit actually runs (one level above this dir). Linter unchanged.
part-2: linted    # 2026-07-02; verify green first run (17/17 under pytest: 14 function-
                  # building references + 5.3/5.4b/6.4 refactor-predict equivalence checks);
                  # all 35 asserts copied byte-exact into the verify file; lint clean with
                  # no linter change (predict exercises def-free by design, DEC-0007 exemption
                  # applied as calibrated). Spot-check (random: 5.1, 5.4a, 6.3): each solvable
                  # from scaffold+hint+asserts using only idioms from parts 1–2. No assert
                  # or hint edits were needed.
part-3: linted    # 2026-07-02; verify green (16/16 under pytest; all 40 asserts copied
                  # byte-exact); 12.4's second leg verified for real: solved scratch_12.py
                  # passes `mypy --strict scratch_12.py` and `python scratch_12.py`. Lint
                  # clean first run, no linter change. One harness-only fix during verify
                  # (11.1's Ticket moved to module scope — nested dataclasses repr with
                  # __qualname__; the shipped assert is correct for a scratch file). Spot-
                  # check (random: 10.3, 11.3, 11.4): each solvable from scaffold+hint+
                  # asserts with idioms from parts 1–3. No assert or hint edits needed.
part-4: pending
part-5: pending
part-6: pending
part-7: pending
final-sweep: pending
Legend: pending -> written -> verified (asserts green) -> linted
