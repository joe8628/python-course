#!/usr/bin/env python3
"""Anti-Drift Framework upgrader — deterministic half of an upgrade.

An upgrade has three tiers, split by who owns the bytes:

  Tier 1  replace wholesale   wiki/core/, .claude/core/RULES.md, wiki/build_index.py
                              — zero project content. Written from UPGRADE_PROMPT.md
                              before this script runs; verified here.
  Tier 2  managed block       STATE.md, GLOSSARY.md — the framework owns a region
                              delimited by <!-- ADF:BEGIN id vX --> markers, the
                              project owns the rest of the file. This script
                              inserts or replaces the region, by marker identity.
  Tier 3  agent merge         CLAUDE.md, ANCHOR.md — too customized for a script.
                              CLAUDE.md needs one import line, which this script
                              adds when it can find the @ANCHOR.md anchor and
                              otherwise reports for the agent to place by hand.
                              ANCHOR.md is pure project content: never touched.

Everything here is idempotent. Re-running changes nothing.

    python3 .adf/upgrade.py --check      # report version + local drift, write nothing
    python3 .adf/upgrade.py --dry-run    # print the plan, write nothing
    python3 .adf/upgrade.py              # apply, then rebuild the wiki index
    python3 .adf/upgrade.py --test       # self-test the block machinery

No external dependencies.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

VERSION = "2.0.0"
BASELINE_VERSION = "1.0.0"  # assumed when no manifest exists

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(HERE, "manifest.json")

# --- Tier 1: files the framework replaces wholesale -------------------------

CORE_FILES = [
    ".claude/core/RULES.md",
    "wiki/core/RUL-CORE-0001.md",
    "wiki/core/RUL-CORE-0002.md",
    "wiki/core/RUL-CORE-0003.md",
    "wiki/core/DEC-CORE-0001.md",
    "wiki/build_index.py",
]

# --- Tier 2: framework-owned regions inside project-owned files -------------

STATE_HEADER = """\
> **Do not record perishable facts here.** Branch sync, PR/issue status, and test
> results are derivable and go stale silently — this file is injected into every
> session by the SessionStart hook, so a stale line is asserted as truth. Record
> *intent and decisions*; name the command that yields live state
> (RUL-CORE-0002). Identifiers are fine — a branch *name* is durable, its
> *position* is not.
>
> | Instead of | Write |
> |---|---|
> | "main is 7 commits ahead of origin" | sync: `git status -sb` |
> | "the branch is not pushed" | sync: `git log origin/<branch>..<branch>` |
> | "PR #12 is awaiting review" | PR #12 — status: `gh pr view 12` |
> | "tests are green" | gate: `<test command>` |"""

GLOSSARY_VOCAB = """\
---

## Perishable vocabulary — every term below demands a fresh read

> Framework-owned section (RUL-CORE-0002). *Perishable claim* and *Fresh read*
> are defined in the term table above. Replaced on upgrade — add your own trigger
> terms as a project record, not by editing inside these markers.

> These are trigger words. Writing one about an externally-mutable artifact —
> an issue, PR, branch, tag, remote ref, deployment, or published file —
> requires that a check ran **in the same turn, after the last event that could
> have changed it**. No fresh read, no claim: describe what you last saw and say
> when you saw it, or run the check.
>
> **The test:** *could a command run outside this session change whether this
> sentence is true?* If yes, the sentence is a Perishable claim.

| Category | Trigger terms | Fresh read |
|----------|---------------|------------|
| Artifact lifecycle | open, closed, merged, unmerged, draft, ready, filed, reopened, landed, deleted, published, released, tagged, deployed | `gh issue view` · `gh pr view` · `git tag` |
| Local↔remote sync | pushed, unpushed, ahead, behind, diverged, in sync, level, up to date, tracked, upstream | `git fetch` then `git log origin/…` · `git status -sb` |
| Ref identity | tip, HEAD, points at, latest, current commit, SHA, "is at" | `git rev-parse` · `git log -1` |
| Completion | done, complete, finished, shipped, outstanding, remaining, blocked, pending, green, passing, failing, clean, dirty | the gate command itself, rerun |
| Recency adverbs | now, currently, already, still, no longer, just, yet, as of, at this point | whatever the adverb modifies |
| Derived quantities | commit counts, "N ahead", timestamps, byte sizes, list lengths | recompute; never carry a number forward |
| **Inference verbs** | should be, must have, by now, presumably, that means, which leaves, so it is, assuming | **none — these substitute for a read; replace with one** |

The last row is the most dangerous: those phrases *feel* like reasoning but are
stale reads wearing a disguise. A status table assembled from them reads as a
summary of work just done, which is why it slips past a check aimed at
"about to assert."

Claiming freshness you do not have — "verified just now", "re-read rather than
recalled" — is worse than stating a stale value plainly, because it removes the
reader's last cue to check for themselves. Never write it unless the command
output is in the same turn."""

BLOCKS = [
    {"id": "state-header", "path": "STATE.md",
     "placement": "before-first-heading", "body": STATE_HEADER},
    {"id": "glossary-vocab", "path": "GLOSSARY.md",
     "placement": "append", "body": GLOSSARY_VOCAB},
]

# --- Tier 2b: framework rows inside a project-owned table -------------------
# GLOSSARY.md's term table has a fixed column signature, so rows can be appended
# to it deterministically. Rows are identified by their first cell, never by
# position, so the project's own terms are never read, moved, or rewritten.
# These belong in the real term table (not the section below it) so that a
# lookup for "Perishable claim" finds them where every other term lives.

MANAGED_ROWS = [
    {
        "id": "terms",
        "path": "GLOSSARY.md",
        "header": ["Term", "Canonical meaning", "Not to be confused with"],
        "rows": [
            ["Perishable claim",
             "A statement whose truth depends on when a command last ran "
             "([RUL-CORE-0002](wiki/core/RUL-CORE-0002.md))",
             "a durable fact (file content you just wrote)"],
            ["Fresh read",
             "A check run in the current turn, after the last event that could "
             "have changed the answer",
             "a read from an earlier turn; a recalled value"],
        ],
    },
]

# --- Tier 3: the single line CLAUDE.md ever needs ---------------------------

IMPORT_LINE = "@.claude/core/RULES.md"
IMPORT_ANCHOR = "@ANCHOR.md"


# --- block machinery --------------------------------------------------------

def marker_re(block_id: str):
    """Match a whole managed block, whatever version stamp it carries."""
    return re.compile(
        r"<!-- ADF:BEGIN " + re.escape(block_id) + r"(?: v[^\s>]+)? -->\n"
        r".*?"
        r"\n<!-- ADF:END " + re.escape(block_id) + r" -->",
        re.DOTALL,
    )


def render_block(block_id: str, body: str) -> str:
    return (f"<!-- ADF:BEGIN {block_id} v{VERSION} -->\n"
            f"{body}\n"
            f"<!-- ADF:END {block_id} -->")


def extract_block(text: str, block_id: str):
    """Return the block's body, or None when the block is absent."""
    m = marker_re(block_id).search(text)
    if not m:
        return None
    inner = m.group(0).split("\n", 1)[1]
    return inner.rsplit("\n", 1)[0]


def apply_block(text: str, block_id: str, body: str, placement: str) -> str:
    """Insert or replace a managed block. Idempotent."""
    rendered = render_block(block_id, body)
    pattern = marker_re(block_id)
    if pattern.search(text):
        return pattern.sub(lambda _: rendered, text, count=1)
    if placement == "before-first-heading":
        m = re.search(r"^## ", text, re.MULTILINE)
        if m:
            return text[:m.start()] + rendered + "\n\n" + text[m.start():]
    return text.rstrip("\n") + "\n\n" + rendered + "\n"


# --- managed-row machinery --------------------------------------------------

def split_row(line: str) -> list:
    """Cells of a Markdown table row, or [] when the line is not one."""
    s = line.strip()
    if not s.startswith("|"):
        return []
    return [c.strip() for c in s.strip("|").split("|")]


def render_row(cells: list) -> str:
    return "| " + " | ".join(cells) + " |"


def is_separator(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def find_table(lines: list, header: list):
    """Locate a table by its column names. Returns (first_row, end) or None.

    `end` is exclusive, so rows are lines[first_row:end]. Matching is on the
    header cells only — column widths and separator style are irrelevant.
    """
    want = [h.strip().lower() for h in header]
    for i, line in enumerate(lines):
        if [c.lower() for c in split_row(line)] != want:
            continue
        if i + 1 >= len(lines) or not is_separator(lines[i + 1]):
            continue
        end = i + 2
        while end < len(lines) and split_row(lines[end]):
            end += 1
        return i + 2, end
    return None


def extract_rows(text: str, spec: dict):
    """The framework's rows as they currently appear, or None if absent."""
    lines = text.split("\n")
    found = find_table(lines, spec["header"])
    if not found:
        return None
    start, end = found
    wanted = {r[0] for r in spec["rows"]}
    present = [ln for ln in lines[start:end]
               if split_row(ln) and split_row(ln)[0] in wanted]
    return "\n".join(present) if present else None


def apply_rows(text: str, spec: dict):
    """Append or update the framework's rows in a project-owned table.

    Returns (text, status). Idempotent: a row already correct is left alone, a
    row that moved keeps its position, and the project's rows are never touched.
    """
    lines = text.split("\n")
    found = find_table(lines, spec["header"])
    if not found:
        return text, "no-table"
    start, end = found
    changed = False
    for cells in spec["rows"]:
        rendered = render_row(cells)
        for i in range(start, end):
            row = split_row(lines[i])
            if row and row[0] == cells[0]:
                if lines[i] != rendered:
                    lines[i] = rendered
                    changed = True
                break
        else:
            lines.insert(end, rendered)
            end += 1
            changed = True
    return "\n".join(lines), ("updated" if changed else "current")


def ensure_import(text: str) -> tuple:
    """Add the RULES.md import after @ANCHOR.md. Returns (text, status)."""
    if IMPORT_LINE in text:
        return text, "present"
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == IMPORT_ANCHOR:
            lines.insert(i + 1, IMPORT_LINE)
            return "\n".join(lines), "added"
    return text, "manual"


# --- helpers ----------------------------------------------------------------

def sha(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def exists(rel: str) -> bool:
    return os.path.exists(os.path.join(ROOT, rel))


def read(rel: str) -> str:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(rel: str, text: str) -> None:
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_manifest() -> tuple:
    """Returns (manifest, state) with state in none | ok | malformed.

    A manifest that will not parse is never fatal: the installed version is
    simply unknown, and an unknown version is treated as an upgrade. Every
    step is idempotent, so re-applying costs nothing — whereas refusing to
    proceed, or assuming a fresh install, would strand the repo.
    """
    if not os.path.exists(MANIFEST):
        return {"framework_version": BASELINE_VERSION, "managed": {}}, "none"
    try:
        with open(MANIFEST, encoding="utf-8") as f:
            man = json.load(f)
        if not isinstance(man, dict) or not man.get("framework_version"):
            raise ValueError("no framework_version")
        man.setdefault("managed", {})
        return man, "ok"
    except Exception:
        return {"framework_version": None, "managed": {}}, "malformed"


def parse_version(v):
    """('2', '0', '0') -> (2, 0, 0); anything unparseable -> None."""
    if not v:
        return None
    parts = str(v).strip().lstrip("v").split(".")
    if not 1 <= len(parts) <= 4 or not all(p.isdigit() for p in parts):
        return None
    return tuple(int(p) for p in parts) + (0,) * (3 - len(parts))


def describe(installed, state: str) -> str:
    if state == "malformed":
        return "unknown (manifest unreadable)"
    if state == "none":
        return f"{installed} (assumed — no manifest)"
    return str(installed)


def current_hashes() -> dict:
    """Hash every managed region as it exists on disk right now."""
    out = {}
    for rel in CORE_FILES:
        out[rel] = sha(read(rel))
    for b in BLOCKS:
        body = extract_block(read(b["path"]), b["id"])
        out[f"{b['path']}#{b['id']}"] = sha(body) if body is not None else "absent"
    for s in MANAGED_ROWS:
        rows = extract_rows(read(s["path"]), s)
        out[f"{s['path']}#rows:{s['id']}"] = sha(rows) if rows is not None else "absent"
    return out


def missing_core() -> list:
    return [r for r in CORE_FILES if not os.path.exists(os.path.join(ROOT, r))]


# --- commands ---------------------------------------------------------------

def cmd_check() -> int:
    man, state = load_manifest()
    installed = man.get("framework_version")
    print(f"installed: {describe(installed, state)}   available: {VERSION}")
    if state == "none":
        print("no manifest — treating as a versionless install (upgrade).")
    elif state == "malformed":
        print("manifest unreadable — treating as a versionless install (upgrade).")

    newer = parse_version(installed)
    if newer and newer > parse_version(VERSION):
        print(f"REFUSING: installed v{installed} is newer than this upgrader "
              f"(v{VERSION}). Downgrading would delete features. Get the newer "
              f"UPGRADE_PROMPT.md instead.")
        return 2

    gone = missing_core()
    if gone:
        print("missing framework files (write them from UPGRADE_PROMPT.md first):")
        for r in gone:
            print(f"  - {r}")

    recorded, now = man.get("managed", {}), current_hashes()
    drifted = [k for k, v in recorded.items() if k in now and now[k] != v]
    if drifted:
        print("locally modified since last upgrade — will NOT be overwritten:")
        for k in drifted:
            print(f"  - {k}")
    elif recorded:
        print("no local drift in managed regions.")

    if state == "ok" and installed == VERSION and not gone and not drifted:
        print("up to date.")
        return 0
    return 1


def cmd_apply(dry_run: bool) -> int:
    man, state = load_manifest()
    installed = man.get("framework_version")
    recorded = man.get("managed", {})
    now = current_hashes()
    tag = "[dry-run] " if dry_run else ""

    newer = parse_version(installed)
    if newer and newer > parse_version(VERSION):
        print(f"REFUSING: installed v{installed} is newer than this upgrader "
              f"(v{VERSION}). Downgrading would delete features. Get the newer "
              f"UPGRADE_PROMPT.md instead.")
        return 2

    # No manifest, or one that will not parse, means the version is unknown —
    # never that the repo is new. Every step below is idempotent, so upgrading
    # a repo that was already current is a no-op; assuming a fresh install
    # would overwrite filled-in content. Unknown always resolves to upgrade.
    if state != "ok":
        why = "no manifest" if state == "none" else "manifest unreadable"
        print(f"{tag}{why} — version unknown; upgrading as versionless "
              f"-> {VERSION}")
    else:
        print(f"{tag}upgrading {installed} -> {VERSION}")

    gone = missing_core()
    if gone:
        print("ERROR: framework files absent. Write them from UPGRADE_PROMPT.md, "
              "then re-run:")
        for r in gone:
            print(f"  - {r}")
        return 2

    changed = []

    # Tier 3: the one CLAUDE.md line.
    claude = read("CLAUDE.md")
    if not exists("CLAUDE.md"):
        print("  ! CLAUDE.md not found — skipped")
    elif not claude.strip():
        print("  ! CLAUDE.md is empty — add the imports by hand (agent step)")
    else:
        new_claude, status = ensure_import(claude)
        if status == "added":
            changed.append("CLAUDE.md: added import line")
            if not dry_run:
                write("CLAUDE.md", new_claude)
        elif status == "manual":
            print(f"  ! CLAUDE.md: no '{IMPORT_ANCHOR}' line found — add "
                  f"'{IMPORT_LINE}' by hand (agent step)")
        else:
            print("  = CLAUDE.md: import already present")

    # Tier 2: managed blocks.
    for b in BLOCKS:
        key = f"{b['path']}#{b['id']}"
        text = read(b["path"])
        if not exists(b["path"]):
            print(f"  ! {b['path']} not found — skipped")
            continue
        existing = extract_block(text, b["id"])
        if existing is not None and key in recorded and now[key] != recorded[key]:
            print(f"  ! {key}: locally modified — left untouched")
            continue
        if existing == b["body"]:
            print(f"  = {key}: current")
            continue
        updated = apply_block(text, b["id"], b["body"], b["placement"])
        changed.append(f"{key}: {'replaced' if existing is not None else 'inserted'}")
        if not dry_run:
            write(b["path"], updated)

    # Tier 2b: framework rows inside a project-owned table.
    for s in MANAGED_ROWS:
        key = f"{s['path']}#rows:{s['id']}"
        text = read(s["path"])
        if not exists(s["path"]):
            print(f"  ! {s['path']} not found — skipped")
            continue
        existing = extract_rows(text, s)
        if existing is not None and key in recorded and now[key] != recorded[key]:
            print(f"  ! {key}: locally modified — left untouched")
            continue
        updated, status = apply_rows(text, s)
        if status == "no-table":
            cols = " | ".join(s["header"])
            print(f"  ! {s['path']}: no table with columns [{cols}] — add these "
                  f"rows by hand (agent step):")
            for cells in s["rows"]:
                print(f"      {render_row(cells)}")
            continue
        if status == "current":
            print(f"  = {key}: current")
            continue
        changed.append(f"{key}: {'updated' if existing else 'inserted'}")
        if not dry_run:
            write(s["path"], updated)

    for c in changed:
        print(f"  + {c}")

    if dry_run:
        print("[dry-run] nothing written")
        return 0

    # Rebuild the index so new core records land in it.
    idx = os.path.join(ROOT, "wiki", "build_index.py")
    if os.path.exists(idx):
        subprocess.run([sys.executable, idx], check=True)

    write_manifest()
    print(f"upgraded to {VERSION}")
    return 0


def write_manifest() -> None:
    payload = {
        "framework_version": VERSION,
        "upgraded": datetime.date.today().isoformat(),
        "managed": current_hashes(),
    }
    os.makedirs(HERE, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


# --- self-test --------------------------------------------------------------

def _selftest() -> None:
    # Insert before the first heading, then confirm re-applying is a no-op.
    doc = "# Title\n\nintro\n\n---\n\n## First\n\nbody\n"
    once = apply_block(doc, "state-header", "BODY", "before-first-heading")
    assert "<!-- ADF:BEGIN state-header v" in once
    assert once.index("BODY") < once.index("## First"), once
    twice = apply_block(once, "state-header", "BODY", "before-first-heading")
    assert twice == once, "insert must be idempotent"

    # Replacing a block keeps everything outside the markers byte-identical.
    updated = apply_block(once, "state-header", "NEWBODY", "before-first-heading")
    assert "NEWBODY" in updated and "BODY\n" not in updated.replace("NEWBODY", "")
    assert updated.startswith("# Title\n\nintro\n\n---\n\n")
    assert updated.endswith("## First\n\nbody\n")

    # A block carrying an older version stamp is still matched and replaced.
    stale = ("x\n\n<!-- ADF:BEGIN glossary-vocab v1.9.0 -->\nOLD\n"
             "<!-- ADF:END glossary-vocab -->\n")
    fresh = apply_block(stale, "glossary-vocab", "NEW", "append")
    assert "OLD" not in fresh and f"v{VERSION}" in fresh, fresh
    assert fresh.count("ADF:BEGIN glossary-vocab") == 1

    # Append lands at EOF when the block is absent.
    appended = apply_block("tail\n", "glossary-vocab", "B", "append")
    assert appended == ("tail\n\n<!-- ADF:BEGIN glossary-vocab "
                        f"v{VERSION} -->\nB\n<!-- ADF:END glossary-vocab -->\n")

    # Round-trip: what we write is what we extract.
    assert extract_block(once, "state-header") == "BODY"
    assert extract_block(doc, "state-header") is None
    multi = apply_block("z\n", "state-header", "l1\nl2\nl3", "append")
    assert extract_block(multi, "state-header") == "l1\nl2\nl3"

    # --- managed rows -------------------------------------------------------
    spec = {"id": "terms", "path": "G.md",
            "header": ["Term", "Canonical meaning", "Not to be confused with"],
            "rows": [["Perishable claim", "def A", "not A"],
                     ["Fresh read", "def B", "not B"]]}
    doc = ("# G\n\nintro\n\n"
           "| Term | Canonical meaning | Not to be confused with |\n"
           "|------|-------------------|-------------------------|\n"
           "| Chunk | project term | a Block |\n"
           "| Block | another | a Chunk |\n"
           "\n## Naming conventions\n\n- x\n")
    out, status = apply_rows(doc, spec)
    assert status == "updated"
    # Project rows are untouched and keep their order and position.
    assert "| Chunk | project term | a Block |" in out
    assert out.index("| Chunk") < out.index("| Block") < out.index("| Perishable claim")
    # Rows land inside the table, never after the following section.
    assert out.index("| Fresh read") < out.index("## Naming conventions")
    assert out.endswith("\n## Naming conventions\n\n- x\n")
    # Idempotent.
    again, status = apply_rows(out, spec)
    assert status == "current" and again == out, "row insert must be idempotent"
    # A hand-changed managed row is rewritten in place, not duplicated.
    edited = out.replace("| Perishable claim | def A | not A |",
                         "| Perishable claim | MINE | not A |")
    fixed, status = apply_rows(edited, spec)
    assert status == "updated"
    assert fixed.count("| Perishable claim |") == 1 and "MINE" not in fixed
    # Extraction sees only the framework's rows, in table order.
    assert extract_rows(out, spec) == ("| Perishable claim | def A | not A |\n"
                                       "| Fresh read | def B | not B |")
    assert extract_rows(doc, spec) is None
    # Column matching ignores width and case; an unrelated table is not touched.
    wide = doc.replace("|------|-------------------|-------------------------|",
                       "| :--- | :---------------- | :---------------------- |")
    assert apply_rows(wide, spec)[1] == "updated"
    other = "| Name | Value |\n|---|---|\n| a | b |\n"
    assert apply_rows(other, spec) == (other, "no-table")
    # A separator line is not mistaken for a data row.
    assert is_separator("|------|----|") and is_separator("| :--- | ---: |")
    assert not is_separator("| Chunk | a |")

    # Import insertion: after the anchor, once, with a manual fallback.
    md = "# CLAUDE\n\n@ANCHOR.md\n\n---\n"
    added, status = ensure_import(md)
    assert status == "added"
    assert added == f"# CLAUDE\n\n@ANCHOR.md\n{IMPORT_LINE}\n\n---\n", repr(added)
    again, status = ensure_import(added)
    assert status == "present" and again == added
    _, status = ensure_import("# CLAUDE\n\nno anchor here\n")
    assert status == "manual"

    # Version parsing: only clean dotted digits count as a readable version.
    assert parse_version("2.0.0") == (2, 0, 0)
    assert parse_version("v1.2") == (1, 2, 0)
    assert parse_version("1.0.0") < parse_version("2.0.0")
    assert parse_version("2.0.1") > parse_version("2.0.0")
    for bad in (None, "", "  ", "main", "2.x", "abc123", "1.0.0-rc1"):
        assert parse_version(bad) is None, bad

    # An unreadable manifest reports state 'malformed', never a version — so the
    # caller upgrades rather than assuming the repo is current or new.
    import tempfile
    global MANIFEST
    keep = MANIFEST
    try:
        with tempfile.TemporaryDirectory() as d:
            MANIFEST = os.path.join(d, "manifest.json")
            man, state = load_manifest()
            assert state == "none" and man["framework_version"] == BASELINE_VERSION
            for junk in ("{not json", "[]", '{"managed": {}}', '{"framework_version": ""}'):
                with open(MANIFEST, "w", encoding="utf-8") as f:
                    f.write(junk)
                man, state = load_manifest()
                assert state == "malformed", junk
                assert man["framework_version"] is None, junk
            with open(MANIFEST, "w", encoding="utf-8") as f:
                f.write('{"framework_version": "1.0.0"}')
            man, state = load_manifest()
            assert state == "ok" and man["framework_version"] == "1.0.0"
            assert man["managed"] == {}
    finally:
        MANIFEST = keep

    print("self-test OK")


def main() -> int:
    args = sys.argv[1:]
    if "--test" in args:
        _selftest()
        return 0
    if "--check" in args:
        return cmd_check()
    return cmd_apply(dry_run="--dry-run" in args)


if __name__ == "__main__":
    sys.exit(main())
