#!/usr/bin/env bash
#
# session-start-updates.sh — Watt plugin update check.
#
# Wired with "asyncRewake": true in hooks.json, so the host runs it in the
# background (never blocking session start) and, on exit code 2, surfaces this
# script's stdout to Claude as a system reminder. So the script itself is plain
# synchronous:
#
#   1) read the installed version from disk,
#   2) fetch the hosted CHANGELOG (raw markdown of
#      https://github.com/wattdata/plugin/blob/main/CHANGELOG.md),
#   3) if the latest released version differs, print the consolidated list of
#      changes and exit 2 (which wakes Claude with the notice).
#
# Up to date, or any failure (missing file, no fetch tool, network error) —
# exit 0, silent.

set -uo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
MANIFEST="$PLUGIN_ROOT/.claude-plugin/plugin.json"
CHANGELOG_URL="https://raw.githubusercontent.com/wattdata/plugin/main/CHANGELOG.md"
UPDATE_URL="https://claude.ai/customize/plugins/watt%40plugin/connectors"

# 1) installed version from disk
[ -f "$MANIFEST" ] || exit 0
local_version=$(grep -m1 '"version"' "$MANIFEST" \
  | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')
[ -n "$local_version" ] || exit 0
local_core=${local_version%%-*}   # strip any -pre marker for comparison

# 2) hosted changelog
fetch() {
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --max-time 5 "$1"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- --timeout=5 "$1"
  fi
}
changelog=$(fetch "$CHANGELOG_URL") || exit 0
[ -n "$changelog" ] || exit 0

# Latest released version = first "## [x.y.z]" header (skips "## [Unreleased]").
latest_version=$(printf '%s\n' "$changelog" \
  | grep -m1 -E '^## \[[0-9]' \
  | sed -E 's/^## \[([^]]+)\].*/\1/')
[ -n "$latest_version" ] || exit 0

# 3) notify only when the latest release is strictly NEWER than installed.
#    (A plain "different" check misfires on dev/pre installs that run ahead of
#    the public release — it would advertise an older version as available.)
ver_gt() {  # true if $1 is a higher major.minor.patch than $2
  local a1 a2 a3 b1 b2 b3
  IFS=. read -r a1 a2 a3 <<<"${1%%-*}"
  IFS=. read -r b1 b2 b3 <<<"${2%%-*}"
  a1=${a1:-0}; a2=${a2:-0}; a3=${a3:-0}
  b1=${b1:-0}; b2=${b2:-0}; b3=${b3:-0}
  [ "$a1" -ne "$b1" ] && { [ "$a1" -gt "$b1" ]; return; }
  [ "$a2" -ne "$b2" ] && { [ "$a2" -gt "$b2" ]; return; }
  [ "$a3" -gt "$b3" ]
}
ver_gt "$latest_version" "$local_core" || exit 0

# Different → consolidate every released section newer than the installed one
# (changelog is newest-first; "## [Unreleased]" is skipped).
changes=$(printf '%s\n' "$changelog" | awk -v installed="$local_core" '
  /^## \[/ {
    v = $0; sub(/^## \[/, "", v); sub(/\].*/, "", v)
    if (v == installed) exit
    printing = (v ~ /^[0-9]/)
  }
  printing { print }
')

cat <<EOF
A newer version of the Watt plugin is available: $latest_version (you're on $local_version).
Update it at: $UPDATE_URL

What's changed since $local_version:

$changes
EOF

exit 2   # wake Claude with the notice above (asyncRewake)
