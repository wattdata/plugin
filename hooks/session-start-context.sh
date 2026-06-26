#!/usr/bin/env bash
#
# session-start-context.sh — Watt's always-on session context (synchronous).
#
# Publishes the bundle root and cats the two context docs the plugin needs in
# scope every session, wrapped for the model to read: the resolved bundle root
# (the path the model substitutes for ${CLAUDE_PLUGIN_ROOT}, which is NOT set in
# its shell), the overview (orientation + voice), and the record contract (the
# durable-record rule, re-injected on compact so it survives a context reset).
# Plain stdout is added to the session context for SessionStart, so no JSON and
# nothing to escape. Best-effort: a missing file just thins the context.
#
# Wired (hooks.json) on startup|clear|compact — the events where this context is
# absent or being rebuilt — and deliberately NOT on resume. A resume replays the
# transcript with this context already in it; re-injecting would insert a second
# copy near the front of the prompt, shifting every downstream token and busting
# the prompt cache for the whole conversation (a full-price re-prefill). Don't
# add `resume` back to the matcher.
#
# Kept deliberately under the 10,000-char SessionStart output cap (the docs plus
# the bundle-root block are ~7.9k together).

set -uo pipefail

# Resolve the bundle root from THIS script's own path — reliable wherever the
# hook runs from the mounted bundle, and independent of $CLAUDE_PLUGIN_ROOT
# (which the model's shell doesn't get). Fall back to the env var only if
# self-location somehow misses. Mirrors render-guard.py's resolution.
SELF="${BASH_SOURCE[0]:-$0}"
PLUGIN_ROOT="$(cd "$(dirname "$SELF")/.." 2>/dev/null && pwd)"
[ -d "$PLUGIN_ROOT/context" ] || PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
OVERVIEW="$PLUGIN_ROOT/context/overview.md"
RECORD="$PLUGIN_ROOT/context/record.md"

printf '<watt-plugin>\n'
printf 'Bundle root: %s\n' "$PLUGIN_ROOT"
printf 'This is where the Watt plugin is mounted in your shell. Wherever a Watt skill or agent instruction writes ${CLAUDE_PLUGIN_ROOT}, use this path in its place — the variable is not set in your shell, so passing it unexpanded to cat or python3 reads nothing. Reach bundled files (scripts, context docs) here, through the shell.\n\n'
[ -f "$OVERVIEW" ] && cat "$OVERVIEW"
printf '\n\n---\n\n'
[ -f "$RECORD" ] && cat "$RECORD"
printf '\n</watt-plugin>\n'
