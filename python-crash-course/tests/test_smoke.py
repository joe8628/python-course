"""Smoke test: keeps the workbook project's pytest gate green (DEC-0006).

An empty suite makes bare `pytest` exit 5, which would break Part 0's
verify-it exercises (0.4a triad chain, 0.4b pre-commit hook).
"""

from crash_course import __version__


def test_package_importable_and_versioned() -> None:
    assert __version__ == "0.1.0"
