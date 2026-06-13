#!/usr/bin/env python3
"""Render-guard hook for the Watt plugin — delivers the render contract.

PostToolUse on the visualize tool's `read_me`: inject the Watt render contract
(context/visuals.md) as additionalContext, right after the visualize tool's
`read_me` lands — so the contract is the freshest word before the model authors
a widget. The output style and the overview only point at the contract, and no
host guarantees either loads whole — this hook is the carrier that works on
every host.

Python, not bash: this hook parses a JSON stdin payload and emits JSON —
json.loads/json.dumps, never hand-rolled grep/sed. Fails open on any internal
error: a hook bug must never block a render.
"""
import json
import os
import sys


def contract_text():
    """The shipped render contract; script-relative first, env as fallback."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [os.path.join(here, "..", "context", "visuals.md")]
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        candidates.append(os.path.join(plugin_root, "context", "visuals.md"))
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            continue
    return ""


def inject_contract():
    contract = contract_text()
    if not contract:
        return
    preamble = (
        "The contract below is Watt's render guidance — what to render and when. "
        "How to build the widget is the visualize tool's own guidance; follow that."
    )
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        "<watt-render-contract>\n"
                        + preamble
                        + "\n\n"
                        + contract
                        + "\n</watt-render-contract>"
                    ),
                }
            },
            ensure_ascii=False,
        )
        + "\n"
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    try:
        event = payload.get("hook_event_name", "")
        tool = payload.get("tool_name", "")
        if event == "PostToolUse" and tool.endswith("__read_me"):
            inject_contract()
    except Exception:
        # Fail open — never block a render on a hook bug.
        return


if __name__ == "__main__":
    main()
