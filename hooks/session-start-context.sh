#!/usr/bin/env bash
#
# session-start-context.sh — Watt's always-on session context (synchronous).
#
# Cats the two context docs the plugin needs in scope every session, wrapped for
# the model to read: the overview (orientation + voice) and the record contract
# (the durable-record rule, re-injected on compact so it survives a context
# reset). Plain stdout is added to the session context for SessionStart, so no
# JSON and nothing to escape. Best-effort: a missing file just thins the context.
#
# Kept deliberately under the 10,000-char SessionStart output cap (the two docs
# are ~7.4k together).

set -uo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
OVERVIEW="$PLUGIN_ROOT/context/overview.md"
RECORD="$PLUGIN_ROOT/context/record.md"

printf '<watt-plugin>\n'
[ -f "$OVERVIEW" ] && cat "$OVERVIEW"
printf '\n\n---\n\n'
[ -f "$RECORD" ] && cat "$RECORD"
printf '\n</watt-plugin>\n'
