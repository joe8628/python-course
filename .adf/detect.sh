#!/usr/bin/env bash
# Detect how this repo relates to the anti-drift framework, and print a verdict.
# Read-only: it writes nothing and changes nothing.
#
#   bash .adf/detect.sh
#
# Safe to paste into a repo that does not have it yet — it has no prerequisites
# beyond bash, and python3 only if a manifest exists.
#
# The governing rule: **a scaffold present without a readable version is an
# UPGRADE, never a fresh install.** Upgrading is idempotent and non-destructive;
# installing over filled-in content destroys it. When the two readings compete,
# upgrade wins.
set -uo pipefail

# Files that only this framework creates. Any one of them means a scaffold.
STRONG="ANCHOR.md
wiki/INDEX.md
wiki/build_index.py
wiki/_TEMPLATE-decision.md
wiki/_TEMPLATE-concept.md
wiki/_TEMPLATE-rule.md
wiki/core
.claude/core/RULES.md
.claude/commands/reground.md"

# Files the framework uses but that any project might have on its own.
WEAK="STATE.md
SPEC.md
ARCHITECTURE.md
GLOSSARY.md
WORKFLOW.md"

found_strong=""; found_weak=""; other_config=""
while IFS= read -r f; do [ -e "$f" ] && found_strong+="  $f"$'\n'; done <<< "$STRONG"
while IFS= read -r f; do [ -e "$f" ] && found_weak+="  $f"$'\n'; done <<< "$WEAK"
for f in CLAUDE.md .claude/settings.json AGENTS.md; do
  [ -e "$f" ] && other_config+="  $f"$'\n'
done

version=""; manifest_state="none"
if [ -f .adf/manifest.json ]; then
  manifest_state="malformed"
  version="$(python3 -c 'import json,sys
try:
    v = json.load(open(".adf/manifest.json")).get("framework_version") or ""
except Exception:
    v = ""
sys.stdout.write(str(v))' 2>/dev/null || true)"
  [ -n "$version" ] && manifest_state="ok"
fi

echo "=== anti-drift detection"
echo "manifest:       ${manifest_state}${version:+ (version $version)}"
echo "strong markers:"; [ -n "$found_strong" ] && printf '%s' "$found_strong" || echo "  (none)"
echo "weak markers:";   [ -n "$found_weak" ]   && printf '%s' "$found_weak"   || echo "  (none)"
echo "other config:";   [ -n "$other_config" ] && printf '%s' "$other_config" || echo "  (none)"
echo

verdict() { echo "VERDICT: $1"; echo "ACTION:  $2"; }

if [ "$manifest_state" = "ok" ]; then
  case "$version" in
    2.0.0)
      verdict "D — already at v2" \
              "Verify only. Do not reinstall. SETUP.md > Scenario D." ;;
    1.*)
      verdict "C — upgrade from v$version" \
              "Follow UPGRADE_PROMPT.md. SETUP.md > Scenario C." ;;
    *)
      verdict "UNKNOWN VERSION ($version) — cannot compare to v2.0.0" \
              "STOP and ask. If it is newer than v2, do not downgrade." ;;
  esac
elif [ "$manifest_state" = "malformed" ]; then
  verdict "C — manifest present but unreadable, version unknown" \
          "Treat as an upgrade. Follow UPGRADE_PROMPT.md; it is idempotent, so \
re-applying costs nothing. Report the unreadable manifest."
elif [ -n "$found_strong" ]; then
  verdict "C — versionless scaffold (the original, pre-versioning release)" \
          "UPGRADE, do not install. Follow UPGRADE_PROMPT.md. Some files may be \
missing; the upgrade writes the framework-owned ones and you fill the rest."
elif [ -n "$found_weak" ]; then
  verdict "AMBIGUOUS — files the framework uses, but nothing unique to it" \
          "STOP and ask whether these are a damaged install or the project's own \
files. Do not overwrite them. If it is a damaged install, treat as C."
elif [ -n "$other_config" ]; then
  verdict "B — no scaffold, but Claude config exists" \
          "Merge install: fold the scaffold into the existing config, never \
overwrite it. SETUP.md > Scenario B."
else
  verdict "A — no scaffold, no Claude config" \
          "Fresh install from RECREATE_PROMPT.md. SETUP.md > Scenario A."
fi
