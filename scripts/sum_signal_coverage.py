"""
Turn an entity_traits per-person 0/1 matrix into the SPECIFIED-half aggregates
the audience-profiler returns — deterministically, so the model never reads the
sample rows (the matrix stays in the advisor's pass; only aggregates leave it).

The audience-profiler runs entity_traits over its deterministic sample with one
expression per `core` (OR) signal (label = the signal's display name → the matrix
column header), downloads the matrix CSV, and runs:

    python3 scripts/sum_signal_coverage.py --matrix matrix.csv --signals signals.json

  --matrix   the entity_traits 0/1 CSV (rows = sampled people, columns = signals)
  --signals  JSON array, one object per core signal:
             {label, name?, value?, domain?, trait_hash?, size?, similarity_score?, skew?}
             `label` must match the matrix column header exactly.

Emits (stdout) a JSON object whose field names are the build_report_membership.py --profile
shape's own, so the leaf passes it straight through with no renaming:

  {
    "specified": [ { trait_hash, name, value, domain, audience_prevalence,
                     reach, match_to_brief, concentration, actively_searching } ],
    "coverage":  [ { signals_hit, people } ],
    "rows_scored": N,
    "missing_columns": [ ... ]            # labels not found in the matrix header
  }

audience_prevalence = column mean (share of the sample expressing the signal).
coverage = histogram of how many of the signals each sampled person hits (≥1).
No MCP calls, stdlib only, deterministic: same matrix + same signals → same output.
"""

import argparse
import csv
import json
import sys


def main(argv=None):
    p = argparse.ArgumentParser(description="entity_traits matrix -> SPECIFIED aggregates")
    p.add_argument("--matrix", required=True, help="entity_traits 0/1 CSV path")
    p.add_argument("--signals", required=True, help="JSON array of core signals")
    args = p.parse_args(argv)

    with open(args.signals) as f:
        signals = json.load(f)
    if not isinstance(signals, list):
        print("sum_signal_coverage: --signals must be a JSON array", file=sys.stderr)
        return 1

    labels = [s["label"] for s in signals]
    col_hits = {lab: 0 for lab in labels}
    coverage_counter = {}
    n_rows = 0

    with open(args.matrix, newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        present = [lab for lab in labels if lab in header]
        missing = [lab for lab in labels if lab not in header]
        for row in reader:
            n_rows += 1
            hits = 0
            for lab in present:
                try:
                    v = int(float(row[lab]))
                except (TypeError, ValueError):
                    v = 0
                if v:
                    col_hits[lab] += 1
                    hits += 1
            coverage_counter[hits] = coverage_counter.get(hits, 0) + 1

    specified = []
    for s in signals:
        lab = s["label"]
        count = col_hits.get(lab, 0)
        prevalence = (count / n_rows) if n_rows else 0.0
        specified.append({
            "trait_hash": s.get("trait_hash", ""),
            "name": s.get("name", lab),
            "value": s.get("value", ""),
            "domain": s.get("domain", ""),
            "audience_prevalence": prevalence,
            "reach": int(s.get("size", 0) or 0),
            "match_to_brief": (round(float(s["similarity_score"]), 3)
                               if s.get("similarity_score") is not None else None),
            "concentration": (round(abs(float(s["skew"])), 3)
                              if s.get("skew") is not None else None),
            "actively_searching": (s.get("domain", "") == "intent"),
        })
    specified.sort(key=lambda r: -r["audience_prevalence"])

    max_hits = max(coverage_counter) if coverage_counter else 0
    coverage = [{"signals_hit": k, "people": coverage_counter.get(k, 0)}
                for k in range(1, max_hits + 1)]

    json.dump({
        "specified": specified,
        "coverage": coverage,
        "rows_scored": n_rows,
        "missing_columns": missing,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if missing:
        print(f"sum_signal_coverage: {len(missing)} signal label(s) not in the matrix header: "
              + ", ".join(missing), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
