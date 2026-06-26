#!/usr/bin/env python3
"""SubagentStart/Stop activity hook for the Watt plugin.

On START: publishes the resolved bundle root into the subagent's context. The
subagent's shell does not get $CLAUDE_PLUGIN_ROOT, so a script path built from
that variable reads nothing; this injects the absolute path the subagent
substitutes for it, resolved from this script's own location (mirrors
render-guard.py). It is model context only — the user-visible spawn line is
owned by the per-matcher ``statusMessage`` strings in hooks.json (each names, in
plain customer language, what that advisor is doing), and the internal worker
name (signal-finder, strategy-greedy, audience-resolver, …) must never reach the
user.

On STOP: emits one short, voiced completion line so the close of each dispatch
reads as activity rather than an opaque pause. Generic and name-free by design,
for the same reason.

Python, not bash: it drains a JSON payload on stdin and emits JSON on stdout —
json.dumps guarantees well-formed output where hand-rolled echo/printf would
mangle quotes and the emoji. Python is batteries-included and zero-setup in the
Cowork runtime; jq is not guaranteed.

Usage: subagent-activity.py <start|stop>   (phase passed from hooks.json)
"""
import json
import os
import sys

phase = sys.argv[1] if len(sys.argv) > 1 else "start"

# Drain stdin so the harness never blocks on an unread pipe, then ignore it:
# the marker carries no per-agent detail (see the module docstring for why).
try:
    sys.stdin.read()
except Exception:
    pass

if phase == "start":
    # Resolve the bundle root from this script's own path (reliable wherever the
    # hook runs from the mounted bundle); fall back to the env var only if that
    # misses. Publish it as the subagent's substitute for ${CLAUDE_PLUGIN_ROOT}.
    root = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    )
    if not os.path.isdir(os.path.join(root, "scripts")):
        root = os.environ.get("CLAUDE_PLUGIN_ROOT", root)
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStart",
                    "additionalContext": (
                        "Watt bundle root: " + root + "\n"
                        "Wherever a Watt instruction writes ${CLAUDE_PLUGIN_ROOT}, use this "
                        "absolute path in its place — the variable is not set in your shell, "
                        "so an unexpanded ${CLAUDE_PLUGIN_ROOT} reads nothing. Reach bundled "
                        'scripts here through the shell, e.g. python3 "'
                        + root
                        + '/scripts/<file>.py".'
                    ),
                }
            },
            ensure_ascii=False,
        )
        + "\n"
    )
    sys.exit(0)

# Stop phase: the completion marker. systemMessage is the user-visible channel;
# hookSpecificOutput.hookEventName identifies the event back to the harness. The
# line never names the worker.
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
