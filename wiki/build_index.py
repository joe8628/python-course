#!/usr/bin/env python3
"""Regenerate wiki/INDEX.md from the frontmatter of every record in this directory.

Record types (by ID prefix, or explicit `type:` frontmatter):
    CON-XXXX  concept   — canonical mental models and definitions
    RUL-XXXX  rule      — binding constraints an agent must not violate
    DEC-XXXX  decision  — choices made; status Rejected = a rejected idea

Two namespaces, both indexed together:
    wiki/*.md        project records — `RUL-0002`, `DEC-0003`, … (the project
                     owns this numeric space; upgrades never touch it)
    wiki/core/*.md   framework records — `RUL-CORE-0001`, `DEC-CORE-0001`, …
                     (shipped by the framework, replaced wholesale on upgrade)

`origin:` frontmatter is `framework` for the latter and defaults to `project`
when absent — so records written before the namespace existed stay valid with
no migration. A `-CORE-` ID still types from its first three characters, so no
record needs an explicit `type:` to land in the right section.

Run after adding or changing any record:
    python3 wiki/build_index.py
Run the built-in regression tests:
    python3 wiki/build_index.py --test

No external dependencies. Parses the simple `key: value` frontmatter block
(between the first pair of `---` lines) of every record. Files starting with
`_` (templates) and INDEX.md itself are skipped.
"""
import datetime
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = "core"
PREFIX_TYPE = {"CON": "concept", "RUL": "rule", "DEC": "decision"}


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    meta = {}
    for line in text[3:end].strip("\n").splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        # Strip inline comments: only a `#` preceded by whitespace starts one,
        # so values like "C#" or "issue#42" survive intact.
        val = re.split(r"\s#", val, maxsplit=1)[0].strip()
        meta[key.strip()] = val
    return meta


def esc(cell: str) -> str:
    """Escape characters that would break a Markdown table cell."""
    return cell.replace("|", "\\|")


def record_type(meta: dict) -> str:
    """Explicit `type:` wins; otherwise infer from the ID prefix."""
    t = meta.get("type", "").lower()
    if t in PREFIX_TYPE.values():
        return t
    return PREFIX_TYPE.get(meta.get("id", "")[:3].upper(), "")


def record_origin(meta: dict) -> str:
    """`framework` only when declared; everything else is a project record."""
    return "framework" if meta.get("origin", "").lower() == "framework" else "project"


def sort_key(r: dict) -> tuple:
    """Project records first, then framework ones; alphabetical within each."""
    return (r["origin"] == "framework", r["id"])


def group(rows: list) -> dict:
    """Split records into the four index sections."""
    g = {"concept": [], "rule": [], "decision": [], "rejected": []}
    for r in rows:
        if r["type"] == "decision" and r["status"].lower() == "rejected":
            g["rejected"].append(r)
        elif r["type"] in g:
            g[r["type"]].append(r)
    return g


def collect() -> list:
    """Read every record in wiki/ and wiki/core/ into index rows."""
    paths = sorted(glob.glob(os.path.join(HERE, "*.md"))) + sorted(
        glob.glob(os.path.join(HERE, CORE_DIR, "*.md"))
    )
    rows = []
    for path in paths:
        name = os.path.basename(path)
        if name == "INDEX.md" or name.startswith("_"):
            continue
        with open(path, encoding="utf-8") as f:
            meta = parse_frontmatter(f.read())
        if not meta.get("id"):
            continue
        # Link relative to wiki/, so core records resolve as core/<file>.md.
        rel = os.path.relpath(path, HERE).replace(os.sep, "/")
        rows.append(
            {
                "id": meta.get("id", ""),
                "type": record_type(meta),
                "origin": record_origin(meta),
                "title": meta.get("title", ""),
                "status": meta.get("status", ""),
                "tags": meta.get("tags", "").strip("[]"),
                "date": meta.get("date", ""),
                "summary": meta.get("summary", ""),
                "file": rel,
            }
        )
    rows.sort(key=sort_key)
    return rows


def _selftest() -> None:
    """Regression tests for parsing, escaping, typing, grouping (run: --test)."""
    fm = parse_frontmatter(
        "---\n"
        "id: DEC-0042\n"
        "title: Use C# bindings | not FFI   # inline comment\n"
        "tags: [lang, interop]  # e.g. comment\n"
        "---\nbody\n"
    )
    assert fm["id"] == "DEC-0042", fm
    # '#' inside a token survives; ' #' starts a comment and is stripped.
    assert fm["title"] == "Use C# bindings | not FFI", fm
    assert fm["tags"].strip("[]") == "lang, interop", fm
    # '|' is escaped so it cannot break the Markdown table.
    assert esc(fm["title"]) == "Use C# bindings \\| not FFI"
    assert parse_frontmatter("no frontmatter here") == {}
    # Type comes from `type:` or falls back to the ID prefix.
    assert record_type({"id": "CON-0001"}) == "concept"
    assert record_type({"id": "RUL-0002", "type": "rule"}) == "rule"
    assert record_type({"id": "XYZ-0001"}) == ""
    # A -CORE- ID types from its prefix exactly like a project ID.
    assert record_type({"id": "RUL-CORE-0001"}) == "rule"
    assert record_type({"id": "DEC-CORE-0001"}) == "decision"
    # Origin defaults to project, so pre-namespace records need no migration.
    assert record_origin({}) == "project"
    assert record_origin({"origin": "framework"}) == "framework"
    assert record_origin({"origin": "Framework"}) == "framework"
    assert record_origin({"origin": "project"}) == "project"
    # Project records sort ahead of framework ones within a section.
    unsorted = [
        {"id": "RUL-CORE-0001", "origin": "framework"},
        {"id": "RUL-0002", "origin": "project"},
        {"id": "RUL-0001", "origin": "project"},
    ]
    assert [r["id"] for r in sorted(unsorted, key=sort_key)] == [
        "RUL-0001",
        "RUL-0002",
        "RUL-CORE-0001",
    ]
    # A Rejected decision lands in the Rejected Ideas section, core or not.
    rows = [
        {"id": "DEC-0001", "type": "decision", "status": "Accepted"},
        {"id": "DEC-0002", "type": "decision", "status": "Rejected"},
        {"id": "DEC-CORE-0001", "type": "decision", "status": "Rejected"},
        {"id": "CON-0001", "type": "concept", "status": ""},
        {"id": "RUL-0001", "type": "rule", "status": ""},
    ]
    g = group(rows)
    assert [r["id"] for r in g["rejected"]] == ["DEC-0002", "DEC-CORE-0001"]
    assert [r["id"] for r in g["decision"]] == ["DEC-0001"]
    assert len(g["concept"]) == len(g["rule"]) == 1
    print("self-test OK")


def main() -> None:
    rows = collect()
    g = group(rows)
    core_count = sum(1 for r in rows if r["origin"] == "framework")

    def table(records, with_status=False):
        if not records:
            return ["*(none yet)*", ""]
        head = "| ID | Title | Status | Tags | Date | Summary |" if with_status \
            else "| ID | Title | Tags | Date | Summary |"
        sep = "|----|-------|--------|------|------|---------|" if with_status \
            else "|----|-------|------|------|---------|"
        out = [head, sep]
        for r in records:
            cells = [f"[{esc(r['id'])}]({r['file']})", esc(r["title"])]
            if with_status:
                cells.append(esc(r["status"]))
            cells += [esc(r["tags"]), esc(r["date"]), esc(r["summary"])]
            out.append("| " + " | ".join(cells) + " |")
        out.append("")
        return out

    lines = [
        "# WIKI INDEX — Concepts · Rules · Decisions · Rejected Ideas",
        "",
        "> AUTO-GENERATED by `build_index.py` — do not edit by hand.",
        f"> Last generated: {datetime.date.today().isoformat()}  ·  "
        f"{len(g['concept'])} concepts · {len(g['rule'])} rules · "
        f"{len(g['decision'])} decisions · {len(g['rejected'])} rejected ideas "
        f"({core_count} shipped by the framework).",
        "",
        "Read this index first; then open only the single record you need.",
        "**Check Rejected Ideas before proposing any approach.**",
        "",
        "IDs containing `-CORE-` live in `wiki/core/` and are shipped by the",
        "framework: they are replaced wholesale on upgrade, so do not edit them",
        "and do not allocate new `-CORE-` IDs. Everything else is yours.",
        "",
        "## Concepts",
        "",
        *table(g["concept"]),
        "## Rules (binding — do not violate)",
        "",
        *table(g["rule"]),
        "## Decisions",
        "",
        *table(g["decision"], with_status=True),
        "## Rejected Ideas — do not re-propose",
        "",
        *table(g["rejected"]),
    ]

    out = os.path.join(HERE, "INDEX.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip("\n") + "\n")
    print(
        f"Wrote {out} ({len(rows)} records: {len(g['concept'])} concepts, "
        f"{len(g['rule'])} rules, {len(g['decision'])} decisions, "
        f"{len(g['rejected'])} rejected; {core_count} framework)"
    )


if __name__ == "__main__":
    if "--test" in sys.argv[1:]:
        _selftest()
    else:
        main()
