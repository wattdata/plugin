#!/usr/bin/env python3
"""SessionStart hook for the Watt plugin.

Reads ${CLAUDE_PLUGIN_DATA}/state.json to decide whether to greet a first-time
user with the quickstart suggestion or a returning user with the short menu,
then injects the always-on overview as SessionStart additionalContext.

Python, not bash: this hook parses JSON (state.json) and emits JSON. json.loads
reads the state file robustly and json.dumps escapes the (large, multi-line)
overview payload correctly — both things hand-rolled grep/sed get wrong on
quotes, escapes, and newlines. Python is batteries-included and zero-setup in
the Cowork runtime (preinstalled, no network step); jq is not guaranteed and a
raw bash JSON parse is fragile.
"""
import json
import os
import sys

SCHEMA_VERSION = 1


def schema_matches(version):
    """True when the state file's version coerces to SCHEMA_VERSION (mirrors JS Number()===)."""
    try:
        return int(version) == SCHEMA_VERSION
    except (TypeError, ValueError):
        return False


state_dir = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(
    os.path.expanduser("~"), ".claude", "plugins", "data", "watt"
)
state_file = os.path.join(state_dir, "state.json")

first_run = True
last_workflow = ""

try:
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)
    # Trust the file only if the schema version matches; otherwise treat as first run.
    if schema_matches(state.get("version")):
        if state.get("first_run_complete") is True:
            first_run = False
        if isinstance(state.get("last_workflow"), str):
            last_workflow = state["last_workflow"]
except Exception:
    # Missing or unparseable state -> first run.
    pass

# Read the always-injected context: overview (orientation + voice), the
# capability index (what each surface does, for "what can I do with Watt?"),
# and the docs pointer (the docs root help and the surfaces point to for depth).
watt_overview = ""
watt_index = ""
watt_docs = ""
plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
try:
    with open(os.path.join(plugin_root, "context", "overview.md"), "r", encoding="utf-8") as f:
        watt_overview = f.read()
except Exception:
    # Overview is best-effort; absence just means a thinner greeting.
    pass
try:
    with open(os.path.join(plugin_root, "context", "index.md"), "r", encoding="utf-8") as f:
        watt_index = f.read()
except Exception:
    # Index is best-effort too.
    pass
try:
    with open(os.path.join(plugin_root, "context", "docs.md"), "r", encoding="utf-8") as f:
        watt_docs = f.read()
except Exception:
    # Docs pointer is best-effort too.
    pass

if first_run:
    state_blurb = (
        "This is the user's first session with the Watt plugin. Greet them briefly and suggest "
        "running /watt:quickstart for a short guided first run that builds a real audience from "
        "a plain-English description — pick a starter audience or describe your own, watch Watt "
        "stack the signals behind it into a measured audience, then export it, see who's in it, "
        "or keep exploring. Do not auto-run it — let them decide."
    )
elif last_workflow:
    state_blurb = (
        f"Returning user. Last workflow used: {last_workflow}. Don't re-onboard. If they describe "
        "people they're curious about, route them to /watt:explore to discover the signals behind "
        "the idea; if they want the guided first run again, /watt:quickstart."
    )
else:
    state_blurb = (
        "Returning user. Don't re-onboard. Available: /watt:explore to discover the signals behind "
        "an idea about people, /watt:quickstart to replay the guided first run."
    )

context = f"""<watt-plugin>
{state_blurb}

---

{watt_overview}

---

{watt_index}

---

{watt_docs}
</watt-plugin>"""

sys.stdout.write(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        },
        ensure_ascii=False,
    )
    + "\n"
)
