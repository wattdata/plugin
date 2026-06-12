#!/usr/bin/env python3
"""Render-guard hook for the Watt plugin — two jobs, one script.

- PostToolUse on the visualize tool's `read_me`: inject the Watt render
  contract (context/visuals.md) as additionalContext, immediately after the
  host's own styling guidance lands — so the override is the freshest word
  before the model authors a widget. The output style and the overview only
  point at the contract, and no host guarantees either loads whole —
  this hook is the carrier that works on every host.

- PreToolUse on `show_widget`: the deterministic brand gate. Denies a widget
  that styles itself as the host (references --color-* / --border-radius-*
  host variables), uses the declined elicitation form module, or never paints
  the #222222 Watt surface — with the corrective rules in the deny reason.
  A root element marked data-non-watt is exempt: a render unrelated to Watt
  work uses host defaults by design.

Python, not bash: this hook parses a JSON stdin payload and emits JSON —
json.loads/json.dumps, never hand-rolled grep/sed. Fails open
on any internal error: a hook bug must never block a render.
"""
import json
import os
import re
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
        "The guidance the visualize tool just returned is the host's. For a Watt "
        "render, the contract below overrides its styling wherever the two touch — "
        "the sandbox and pipeline facts there stay binding."
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


def gate_widget(payload):
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    code = tool_input.get("widget_code")
    if not isinstance(code, str) or not code.strip():
        return
    lower = code.lower()

    # Explicitly marked as not a Watt render — host defaults apply by design.
    # Exempt only when data-non-watt is a real attribute on an element tag:
    # scan opening tags and require the token be whitespace-led and bounded by
    # =, whitespace, >, or /. A loose substring won't do — neither a class like
    # "data-non-watt-ish" nor the bare token in text content can slip a
    # host-styled widget past the gate.
    for tag in re.findall(r"<[a-z][^>]*>", lower):
        if re.search(r"\sdata-non-watt(?=[\s=>/])", tag):
            return

    violations = []
    if "var(--color-" in lower:
        violations.append("it references the host's --color-* theme variables")
    if "var(--border-radius" in lower:
        violations.append("it references the host's --border-radius-* variables")
    if 'class="elicit' in lower or "class='elicit" in lower or "elicit-pill" in lower:
        violations.append("it uses the host's elicitation form module")
    # SVG payloads carry their own canvas; the surface rule is for HTML fragments.
    # Accept the full #222222, the #222 shorthand only in a CSS value position
    # (after a colon — so a stray "#222" token in text content can't satisfy
    # the check), or the rgb() form.
    has_surface = (
        "#222222" in lower
        or re.search(r":\s*#222\b", lower)
        or re.search(r"rgb\(\s*34\s*,\s*34\s*,\s*34\s*\)", lower)
    )
    if not lower.lstrip().startswith("<svg") and not has_surface:
        violations.append("it never paints the #222222 Watt surface")

    if not violations:
        return

    reason = (
        "This widget styles itself as the host, not Watt: "
        + "; ".join(violations)
        + ". Two cases. If this render is unrelated to Watt work (not signals, pools, stacks, "
        "audiences, or profiles), mark its root element data-non-watt "
        "and re-issue — host styling passes; never Watt-brand an unrelated artifact. "
        "If it IS a Watt render, re-issue it with the Watt contract applied: "
        "(1) one inner wrapper painting background:#222222, true root transparent, "
        "identical in the host's light and dark mode; "
        "(2) no --color-* / --border-radius-* host variables — copy the Watt tokens: "
        "--surface:#222222; --ink:#FFFFFF; --ink-quiet:#A29A7E; "
        "--lime:#D1FF01 (the bolt mark + ONE hero figure only); "
        "--sage:#B8C3AE or --lavender:#D7D0F2 (pick one); "
        "--alert:#FF6200 (rare); --track:rgba(255,255,255,.08); "
        "(3) flat — border-radius:0 on every surface, badge, and bar (one exception: "
        "a decision-visual option control may use a lime fill and a small rounded corner); "
        "(4) a decision is 2-4 option controls each firing sendPrompt('<the answer in "
        "plain words>') — the only script in any render, never the elicitation form module; "
        "(5) data visuals carry no controls and no script. "
        "The full contract is context/visuals.md in the plugin directory, beside the skills."
    )
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
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
        elif event == "PreToolUse" and tool.endswith("__show_widget"):
            gate_widget(payload)
    except Exception:
        # Fail open — never block a render on a hook bug.
        return


if __name__ == "__main__":
    main()
