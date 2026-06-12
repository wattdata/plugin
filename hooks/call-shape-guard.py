#!/usr/bin/env python3
"""PreToolUse guard on the resolve tools' call shape (soundness.md rules).

Denies, with the corrective rule in the reason, three deterministic
mis-shapes of entity_resolve / resolve_and_enrich_rows:

- Wrong server — a staging/experimental Watt server, not production (both).
- Address trap — entity_resolve resolving by address without identifier_types
  covering "address"; the default ["email"] 500s (entity_resolve only).
- Inline batch blowup — entity_resolve inlining over 3,000 identifier values;
  the CSV-upload path is one call regardless of size (entity_resolve only).

Fails open on any internal error: a hook bug must never block a legitimate call.
"""
import json
import re
import sys

INLINE_VALUE_CAP = 3000
ADDRESS_IDENTIFIER_TYPES = '["name","email","phone","address"]'


def deny(reason):
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


def wrong_server(tool_name):
    """The server segment of an mcp__<server>__<tool> name names a non-prod
    Watt graph. Staging and experimental are separate graphs whose numbers
    must never be trusted as production's."""
    lowered = tool_name.lower()
    return "staging" in lowered or "experimental" in lowered


def resolves_by_address(tool_input):
    identifiers = tool_input.get("identifiers")
    if isinstance(identifiers, list):
        for group in identifiers:
            if isinstance(group, dict) and group.get("id_type") == "address":
                return True
    lookup = tool_input.get("lookup_columns")
    if isinstance(lookup, dict):
        address = lookup.get("address")
        if isinstance(address, dict) and address.get("names"):
            return True
    return False


def identifier_types_cover_address(tool_input):
    types = tool_input.get("identifier_types")
    return isinstance(types, list) and "address" in types


def inline_value_total(tool_input):
    identifiers = tool_input.get("identifiers")
    if not isinstance(identifiers, list):
        return 0
    total = 0
    for group in identifiers:
        if isinstance(group, dict):
            values = group.get("values")
            if isinstance(values, list):
                total += len(values)
    return total


def gate(payload):
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return

    if wrong_server(tool_name):
        deny(
            "This call targets a staging or experimental Watt server, not "
            "production. Experimental and staging are separate graphs — their "
            "counts and matches must never be passed off as production's. "
            "Re-issue against the production Watt server (the one the plugin "
            "ships pinned in .mcp.json)."
        )
        return

    is_entity_resolve = tool_name.endswith("__entity_resolve")
    if not is_entity_resolve:
        # resolve_and_enrich_rows is CSV-only — no identifier_types, no inline
        # identifiers — so the server pin above is the only shape it can trip.
        return

    if resolves_by_address(tool_input) and not identifier_types_cover_address(tool_input):
        deny(
            "This entity_resolve resolves by address but its identifier_types "
            "doesn't include \"address\" — the default ([\"email\"]) 500s on "
            "address resolution. That's the real address trap. Re-issue with "
            "identifier_types: " + ADDRESS_IDENTIFIER_TYPES + " so address "
            "matching can run."
        )
        return

    total = inline_value_total(tool_input)
    if total > INLINE_VALUE_CAP:
        deny(
            "This entity_resolve inlines " + str(total) + " identifier values "
            "(over the " + str(INLINE_VALUE_CAP) + " inline ceiling). A large "
            "inline batch turns into a 30+ minute run — the forbidden "
            "fallback. Use the CSV-upload path instead: generate_upload_url, "
            "then pass csv_resource_uri with lookup_columns — one call "
            "regardless of size."
        )
        return


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    try:
        if payload.get("hook_event_name", "") == "PreToolUse":
            gate(payload)
    except Exception:
        # Fail open — never block a legitimate call on a hook bug.
        return


if __name__ == "__main__":
    main()
