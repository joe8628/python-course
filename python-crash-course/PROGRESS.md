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
part-2: pending
part-3: pending
part-4: pending
part-5: pending
part-6: pending
part-7: pending
final-sweep: pending
Legend: pending -> written -> verified (asserts green) -> linted
