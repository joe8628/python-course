# Build state (update at end of every session)
part-1: linted    # verbatim exemplar dropped in 2026-07-01; verify green (12/12 under pytest).
                  # Linter change (exemplar is ground truth): `...`/assert checks now apply only
                  # to function-building exercises — refactor/predict exercises (no def/class
                  # scaffold + rewrite/refactor/predict/convert instruction) are exempt from
                  # both; exercise blocks containing `...` tolerate SyntaxError (a placeholder
                  # may occupy a grammar-required position, e.g. the body of `match`).
part-0: written   # 2026-07-01; sections 0.1–0.5 authored against the repo's real files
                  # (pyproject/.gitignore/tree quoted accurately; pre-commit config and
                  # [project.scripts] explicitly marked "not in this repo"). Verification
                  # gate (verify + lint) deliberately deferred to the next session.
part-2: pending
part-3: pending
part-4: pending
part-5: pending
part-6: pending
part-7: pending
final-sweep: pending
Legend: pending -> written -> verified (asserts green) -> linted
