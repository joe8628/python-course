#!/usr/bin/env bash
# Rebuild the `release` branch from a commit on main.  DEC-0009 / DEC-0010.
#
#   tools/build-release.sh [source-ref]      # default: main
#
# `release` is an orphan distribution branch: it is never merged into and never
# developed on, only rebuilt.  This script reads the student-facing files out of
# <source-ref>, flattens them to the root of a fresh tree, and commits that tree
# onto `release` — so `release` keeps a readable log of published versions while
# sharing no history with main.
#
# Everything below is local.  Pushing is manual, always (RUL-CORE-0001).
set -euo pipefail

SRC_REF="${1:-main}"
SRC_DIR="python-crash-course"

# The published surface.  Everything not listed here is deliberately withheld:
# the anti-drift system, the authoring specs, tools/, and — because they are
# Part 0's answer key — pyproject.toml, src/, tests/.
FILES=(
    part-0.md part-1.md part-2.md part-3.md part-4.md
    part-5.md part-6.md part-7.md
    README.md HOW-TO-USE.md
)

cd "$(git rev-parse --show-toplevel)"

if [ "$(git symbolic-ref -q --short HEAD || true)" = "release" ]; then
    echo "error: release is checked out; run this from main" >&2
    exit 1
fi
git rev-parse --verify -q "$SRC_REF^{commit}" >/dev/null \
    || { echo "error: no such ref: $SRC_REF" >&2; exit 1; }

# --- build the tree in a scratch index so the working tree is never touched ---
tree=$(
    GIT_INDEX_FILE=$(mktemp -u "${TMPDIR:-/tmp}/relindex.XXXXXX")
    export GIT_INDEX_FILE
    trap 'rm -f "$GIT_INDEX_FILE"' EXIT
    git read-tree --empty
    for f in "${FILES[@]}"; do
        blob=$(git rev-parse -q --verify "$SRC_REF:$SRC_DIR/$f") \
            || { echo "error: $SRC_DIR/$f missing in $SRC_REF" >&2; exit 1; }
        git update-index --add --cacheinfo 100644,"$blob","$f"
    done
    git write-tree
)

src_sha=$(git rev-parse --short "$SRC_REF")
parent=$(git rev-parse -q --verify release || true)

if [ -n "$parent" ] && [ "$(git rev-parse "$parent^{tree}")" = "$tree" ]; then
    echo "release is already identical to $SRC_REF ($src_sha) — nothing to do"
    exit 0
fi

message="Release: verified workbook parts (from $SRC_REF $src_sha)

Student-facing files only, per DEC-0009.  Rebuilt by tools/build-release.sh."

if [ -n "$parent" ]; then
    commit=$(git commit-tree "$tree" -p "$parent" -m "$message")
else
    commit=$(git commit-tree "$tree" -m "$message")   # first release: orphan root
fi

git branch -f release "$commit"
echo "release -> $(git rev-parse --short release)  (from $SRC_REF $src_sha)"
git ls-tree -r release --name-only | sed 's/^/  /'
echo
echo "Not pushed.  When the review passes:  git push origin release"
