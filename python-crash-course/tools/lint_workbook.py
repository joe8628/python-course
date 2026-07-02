#!/usr/bin/env python3
"""Mechanical style gate for workbook part files.

Checks (per SPEC.md and the Workbook Style Rules in the repo-root CLAUDE.md;
calibrated against the part-1.md exemplar, which is ground truth):
- Every function-building exercise's first fenced code block contains `...`
  and the exercise contains >= 1 `assert`. Assert-exempt exercises
  (refactor/predict: no def/class scaffold + a rewrite/refactor/predict/
  convert instruction in the exercise line or a comment) are exempt from
  both the `...` and the assert check.
- No exercise def body has > 2 statements besides docstring / `...`
  (solution-leak guard).
- Every concept code fence (not under an Exercise block) has >= 1 comment.
- Heading chapter numbering is monotonic and inside the range SPEC.md's
  FILE -> CHAPTER MAP assigns to the filename.
- Every fenced non-bash block parses under ast.parse, EXCEPT exercise
  blocks containing `...` — a scaffold placeholder may legally occupy a
  position the grammar requires filled (e.g. the body of `match`).
- No headings or code comments matching /solution|answer key/i.

Usage: python tools/lint_workbook.py part-N.md [part-M.md ...]
Exit code 1 if any issue is found; issues print as file:line: message.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# FILE -> CHAPTER MAP from SPEC.md (part-0 uses chapter number 0, sections 0.1-0.5).
CHAPTER_RANGES: dict[str, tuple[int, int]] = {
    "part-0": (0, 0),
    "part-1": (1, 4),
    "part-2": (5, 8),
    "part-3": (9, 12),
    "part-4": (13, 16),
    "part-5": (17, 20),
    "part-6": (21, 24),
    "part-7": (25, 28),
}

FENCE_RE = re.compile(r"^\s*```(\w*)\s*$")
EXERCISE_RE = re.compile(r"\*\*Exercise", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
# Chapter number opening a heading: "## 5 Functions..." / "## Chapter 5 ..." / "### 5.2 ...".
HEADING_NUM_RE = re.compile(r"^(?:Chapter\s+)?(\d+)(?:\.(\d+))?\b")
LEAK_RE = re.compile(r"solution|answer\s*key", re.IGNORECASE)
EXEMPT_RE = re.compile(r"rewrite|refactor|predict|convert", re.IGNORECASE)


@dataclass
class CodeBlock:
    lang: str
    start_line: int  # 1-based line of the opening fence
    lines: list[str] = field(default_factory=list)
    exercise_id: int | None = None  # which **Exercise marker this block belongs to
    exercise_text: str = ""  # the marker line's prose (instruction)

    @property
    def in_exercise(self) -> bool:
        return self.exercise_id is not None

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


@dataclass
class Issue:
    line: int
    message: str


def parse_blocks(lines: list[str]) -> tuple[list[CodeBlock], list[tuple[int, str]]]:
    """Split a part file into fenced code blocks and (line, text) headings.

    A block belongs to the exercise whose "**Exercise" marker most recently
    preceded it; any non-exercise heading ends the exercise's scope.
    """
    blocks: list[CodeBlock] = []
    headings: list[tuple[int, str]] = []
    current: CodeBlock | None = None
    exercise_id: int | None = None
    exercise_text = ""
    next_id = 0

    for lineno, line in enumerate(lines, start=1):
        fence = FENCE_RE.match(line)
        if current is not None:
            if fence:
                blocks.append(current)
                current = None
            else:
                current.lines.append(line)
            continue
        if fence:
            current = CodeBlock(lang=fence.group(1).lower(), start_line=lineno,
                                exercise_id=exercise_id, exercise_text=exercise_text)
            continue
        heading = HEADING_RE.match(line)
        if heading and not EXERCISE_RE.search(heading.group(2)):
            headings.append((lineno, heading.group(2).strip()))
            exercise_id, exercise_text = None, ""
            continue
        if heading:
            headings.append((lineno, heading.group(2).strip()))
        if EXERCISE_RE.search(line):
            exercise_id, exercise_text = next_id, line
            next_id += 1

    if current is not None:
        blocks.append(current)  # unterminated fence; the parse check will flag it
    return blocks, headings


def group_exercise_blocks(blocks: list[CodeBlock]) -> list[list[CodeBlock]]:
    """Group code blocks by their **Exercise marker; each group is one exercise."""
    groups: dict[int, list[CodeBlock]] = {}
    for block in blocks:
        if block.exercise_id is not None:
            groups.setdefault(block.exercise_id, []).append(block)
    return [groups[eid] for eid in sorted(groups)]


def is_exempt_exercise(group: list[CodeBlock]) -> bool:
    """Assert-exempt exercises (refactor/predict): no def/class scaffold, plus a
    rewrite/refactor/predict/convert instruction in the exercise line or a comment."""
    text = "\n".join(b.text for b in group)
    has_scaffold = re.search(r"^\s*(def|class)\s", text, re.MULTILINE) is not None
    has_instruction = bool(EXEMPT_RE.search(group[0].exercise_text)) or any(
        EXEMPT_RE.search(line) for line in text.splitlines() if "#" in line
    )
    return not has_scaffold and has_instruction


def def_body_statements(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Count body statements, excluding a leading docstring and `...` placeholders."""
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    return sum(
        1 for stmt in body
        if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                and stmt.value.value is Ellipsis)
    )


def check_file(path: Path) -> list[Issue]:
    issues: list[Issue] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks, headings = parse_blocks(lines)

    # --- solution-leak markers in headings and code comments -----------------
    for lineno, text in headings:
        if LEAK_RE.search(text):
            issues.append(Issue(lineno, f"solution-leak marker in heading: {text!r}"))
    for block in blocks:
        for offset, line in enumerate(block.lines, start=1):
            if "#" in line and LEAK_RE.search(line.split("#", 1)[1]):
                issues.append(Issue(block.start_line + offset,
                                    "solution-leak marker in code comment"))

    # --- every non-bash fence must parse --------------------------------------
    # Exception: exercise blocks containing `...` — the placeholder may occupy
    # a position the grammar requires filled (e.g. the body of `match`).
    for block in blocks:
        if block.lang in ("bash", "sh", "shell", "console", "text", "toml"):
            continue
        if block.in_exercise and "..." in block.text:
            continue
        try:
            ast.parse(block.text)
        except SyntaxError as exc:
            bad_line = block.start_line + (exc.lineno or 1)
            issues.append(Issue(bad_line, f"code block does not parse: {exc.msg}"))

    parsable = [b for b in blocks
                if b.lang not in ("bash", "sh", "shell", "console", "text", "toml")]

    # --- concept fences need >= 1 comment --------------------------------------
    for block in parsable:
        if not block.in_exercise and not any("#" in line for line in block.lines):
            issues.append(Issue(block.start_line,
                                "concept code block has no grounding `#` comment"))

    # --- exercise block rules ---------------------------------------------------
    for group in group_exercise_blocks(parsable):
        first = group[0]
        if not is_exempt_exercise(group):
            if "..." not in first.text:
                issues.append(Issue(first.start_line,
                                    "exercise's first code block has no `...` placeholder"))
            combined = "\n".join(b.text for b in group)
            if not re.search(r"^\s*assert\b", combined, re.MULTILINE):
                issues.append(Issue(first.start_line,
                                    "function-building exercise has no assert"))
        for block in group:
            try:
                tree = ast.parse(block.text)
            except SyntaxError:
                continue  # already reported above
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and def_body_statements(node) > 2:
                    issues.append(Issue(
                        block.start_line + node.lineno,
                        f"exercise def {node.name!r} looks like a complete "
                        "implementation (>2 statements besides docstring/`...`)"))

    # --- heading numbering: monotonic and inside the file's chapter range ------
    chapter_range = CHAPTER_RANGES.get(path.stem)
    if chapter_range is None:
        issues.append(Issue(1, f"filename {path.name!r} not in SPEC.md's FILE -> CHAPTER MAP"))
    else:
        low, high = chapter_range
        prev: tuple[int, int] = (-1, -1)
        for lineno, text in headings:
            match = HEADING_NUM_RE.match(text)
            if not match:
                continue
            chapter = int(match.group(1))
            section = int(match.group(2) or 0)
            if not (low <= chapter <= high):
                issues.append(Issue(
                    lineno,
                    f"heading chapter {chapter} outside range {low}-{high} for {path.name}"))
            if (chapter, section) < prev:
                issues.append(Issue(
                    lineno,
                    f"heading numbering not monotonic: {chapter}.{section} after "
                    f"{prev[0]}.{prev[1]}"))
            prev = (chapter, section)

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Mechanical style gate for workbook part files (see SPEC.md)."
    )
    parser.add_argument("files", nargs="+", type=Path, metavar="part-file",
                        help="one or more part-N.md files to lint")
    args = parser.parse_args(argv)

    failed = False
    for path in args.files:
        if not path.is_file():
            print(f"{path}:0: file not found", file=sys.stderr)
            failed = True
            continue
        issues = check_file(path)
        for issue in sorted(issues, key=lambda i: i.line):
            print(f"{path}:{issue.line}: {issue.message}")
        if issues:
            failed = True
        else:
            print(f"{path}: OK", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
