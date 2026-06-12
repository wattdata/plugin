#!/usr/bin/env python3
"""Notification (auth_success) hook for the Watt plugin.

Confirms the browser OAuth round-trip in-session the moment it completes —
the overview promises "OAuth happens automatically", but without this the
user can't tell they're signed in until the next tool call succeeds or fails.

auth_success fires for ANY MCP server's auth, so the script checks the
payload's message names the Watt server before saying anything; other
servers' sign-ins stay silent.

Python, not bash: it reads the message field out of the stdin JSON payload.
json.loads extracts it correctly even when the message carries escaped quotes
or newlines (hand-rolled grep/sed corrupts those). Python is batteries-included
and zero-setup in the Cowork runtime; jq is not guaranteed.
"""
import json
import re
import sys

try:
    raw = sys.stdin.read() or "{}"
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        payload = {}
except Exception:
    # Malformed payload -> stay silent.
    sys.exit(0)

message = payload.get("message") if isinstance(payload.get("message"), str) else ""

# Only speak for the Watt server; stay silent for any other MCP auth.
if not re.search(r"[Ww]att", message):
    sys.exit(0)

sys.stdout.write(
    json.dumps(
        {
            "systemMessage": "✓ Signed in to Watt — the Signal Graph is ready.",
            "hookSpecificOutput": {"hookEventName": "Notification"},
        },
        ensure_ascii=False,
    )
    + "\n"
)
