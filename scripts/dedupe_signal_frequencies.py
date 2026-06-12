"""
Merge one or more group_entities_by_trait responses into the two files the rest
of the analysis chain needs — deterministically, so the agent never hand-types
trait_hash/prevalence pairs into calculate_trait_lift (the trait_frequencies_uri
chaining path is broken server-side; see SKILL.md Phase 6.3).

Phase 6.2 runs group_entities_by_trait per-domain (an intent-only call plus a
call for the remaining domains) so that low-prevalence intent topics aren't
crowded out of the top-N by ubiquitous demographic/household traits. Save each
response to its own JSON file, then:

    python3 scripts/dedupe_signal_frequencies.py \
        --responses intent_resp.json other_resp.json \
        --out-frequencies frequencies.json \
        --out-lift-input lift_input.json

Each input may be a raw group_entities_by_trait response ({"trait_frequencies":
[...]}) or a bare array of frequency rows. Output:

  frequencies.json  — merged, deduped-by-trait_hash array
                      (carries trait_name/value/domain/count/prev)
  lift_input.json   — [{trait_hash, audience_prevalence}, ...] for
                      calculate_trait_lift's audience_frequencies (inline path)

Dedupe keeps the highest audience_prevalence when a trait_hash repeats across
responses. No MCP calls, stdlib only, deterministic.
"""

import argparse
import json
import sys


def extract_rows(obj):
    if isinstance(obj, dict):
        return obj.get("trait_frequencies", [])
    if isinstance(obj, list):
        return obj
    return []


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--responses", nargs="+", required=True,
                   help="One or more JSON files: group_entities_by_trait responses or bare arrays.")
    p.add_argument("--out-frequencies", required=True)
    p.add_argument("--out-lift-input", required=True)
    args = p.parse_args(argv)

    merged = {}  # trait_hash -> row, keeping max prevalence
    no_hash = 0
    for path in args.responses:
        with open(path) as f:
            rows = extract_rows(json.load(f))
        for r in rows:
            th = r.get("trait_hash")
            if not th:
                no_hash += 1
                continue
            prev = float(r.get("audience_prevalence", 0.0))
            if th not in merged or prev > float(merged[th].get("audience_prevalence", 0.0)):
                merged[th] = r

    frequencies = sorted(merged.values(),
                         key=lambda r: -float(r.get("audience_prevalence", 0.0)))
    lift_input = [{"trait_hash": r["trait_hash"],
                   "audience_prevalence": float(r.get("audience_prevalence", 0.0))}
                  for r in frequencies]

    with open(args.out_frequencies, "w") as f:
        json.dump(frequencies, f, indent=2)
    with open(args.out_lift_input, "w") as f:
        json.dump(lift_input, f, indent=2)

    by_domain = {}
    for r in frequencies:
        by_domain[r.get("domain", "?")] = by_domain.get(r.get("domain", "?"), 0) + 1
    print(f"OK: merged {len(frequencies)} unique traits from {len(args.responses)} response(s).")
    print("  by domain: " + ", ".join(f"{d}={n}" for d, n in sorted(by_domain.items())))
    if no_hash:
        print(f"  skipped {no_hash} rows with no trait_hash", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
