#!/usr/bin/env python3
"""SubagentStop activity marker for the Watt plugin.

Emits one short, voiced completion line when a Watt advisor or worker finishes,
so the close of each dispatch reads as activity rather than an opaque pause.

Spawn announcements are owned by the per-matcher ``statusMessage`` strings in
hooks.json — each names, in plain customer language, what that advisor is doing
("Watt: composing toward your size band…", "Watt: reading who this audience
reaches…"). They already cover every wired advisor. So this hook deliberately
adds *nothing* on ``start``: a second spawn line would only duplicate that
statusMessage, and — critically — the internal worker name (signal-finder,
strategy-greedy, audience-resolver, …) must never reach the user, who speaks in
signals and audiences, not worker names. The completion marker is therefore
generic and name-free by design.

Python, not bash: it drains a JSON payload on stdin and emits JSON on stdout —
json.dumps guarantees well-formed output where hand-rolled echo/printf would
mangle quotes and the emoji. Python is batteries-included and zero-setup in the
Cowork runtime; jq is not guaranteed.

Usage: subagent-activity.py <start|stop>   (phase passed from hooks.json)
"""
import json
import sys

phase = sys.argv[1] if len(sys.argv) > 1 else "start"

# Drain stdin so the harness never blocks on an unread pipe, then ignore it:
# the marker carries no per-agent detail (see the module docstring for why).
try:
    sys.stdin.read()
except Exception:
    pass

# On start there is nothing to add — hooks.json's voiced statusMessage already
# announces the spawn. Only the stop phase emits a marker.
if phase != "stop":
    sys.exit(0)

# systemMessage is the user-visible channel; hookSpecificOutput.hookEventName
# identifies the event back to the harness. The line never names the worker.
sys.stdout.write(
    json.dumps(
        {
            "systemMessage": "✓ Watt — done.",
            "hookSpecificOutput": {"hookEventName": "SubagentStop"},
        },
        ensure_ascii=False,
    )
    + "\n"
)
