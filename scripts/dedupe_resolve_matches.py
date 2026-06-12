"""
Dedupe entity_resolve match exports, apply the quality floor, and write the
entity-ID CSV the audience-resolver uploads — deterministically, so the model
never hand-dedupes a quality-filtered set across resolve exports (that drifts and
can't be audited).

The resolver runs entity_resolve with format='csv' (the inline format='none' path
caps at the top 100 entities — unusable for a real list) and downloads the export.
Each export row is one matched entity: columns `entity_id`, `overall_quality_score`,
`matches_json`, `identifier_*`. Across multiple exports — input batches, paginated
csv_resource_uri pages, or several identifier groups — the same entity_id
legitimately recurs, each occurrence carrying its own overall_quality_score (the
Noisy-OR match confidence). This script reads every export, keeps the HIGHEST score
seen per entity_id, drops anything below the floor, and writes the survivors as a
single-column CSV.

    python3 scripts/dedupe_resolve_matches.py \
        --exports export1.csv export2.csv … \
        --quality-floor 0.5 \
        --out entity_ids.csv

  --exports        one or more entity_resolve exports. CSV (format='csv', the
                   default path) read by column; .json/.jsonl (a saved
                   format='none'/'jsonl' response or bare entity array) also
                   accepted. Each entity needs an entity_id and
                   overall_quality_score.
  --quality-floor  minimum overall_quality_score to keep (default 0.5).
  --out            CSV path to write (one `entity_id` column, header included).

Emits (stdout) a JSON summary the agent reports verbatim:
  { "resolved_count": N, "below_floor_count": M, "quality_floor": F, "out": "<path>" }

resolved_count = distinct entities kept (≥ floor); below_floor_count = distinct
entities whose best score was under the floor. No MCP calls, stdlib only,
deterministic: same inputs + same floor → same CSV (entity_ids sorted).
"""

import argparse
import csv
import json
import sys


def rows_from_csv(path):
    """Yield (entity_id, score) from a format='csv' resolve export."""
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            yield row.get("entity_id"), row.get("overall_quality_score", 0.0)


def rows_from_json(path):
    """Yield (entity_id, score) from a format='none'/'jsonl' response or array."""
    with open(path) as f:
        text = f.read().strip()
    # Try a single JSON document first; fall back to JSONL (one object per line).
    docs = []
    try:
        docs = [json.loads(text)]
    except json.JSONDecodeError:
        docs = [json.loads(line) for line in text.splitlines() if line.strip()]
    for doc in docs:
        entities = doc.get("entities", []) if isinstance(doc, dict) else (doc if isinstance(doc, list) else [doc])
        for e in entities:
            yield e.get("entity_id"), e.get("overall_quality_score", 0.0)


def main(argv=None):
    p = argparse.ArgumentParser(description="dedupe + floor entity_resolve exports -> entity_id CSV")
    p.add_argument("--exports", nargs="+", required=True,
                   help="entity_resolve exports: CSV (format='csv') or JSON/JSONL.")
    p.add_argument("--quality-floor", type=float, default=0.5)
    p.add_argument("--out", required=True, help="entity_id CSV path to write.")
    args = p.parse_args(argv)

    best = {}  # entity_id -> max overall_quality_score seen
    no_id = 0
    for path in args.exports:
        reader = rows_from_csv(path) if path.lower().endswith(".csv") else rows_from_json(path)
        for eid, raw_score in reader:
            if eid is None or eid == "":
                no_id += 1
                continue
            eid = str(eid)
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                score = 0.0
            if eid not in best or score > best[eid]:
                best[eid] = score

    kept = sorted((eid for eid, s in best.items() if s >= args.quality_floor),
                  key=lambda x: (len(x), x))
    below = sum(1 for s in best.values() if s < args.quality_floor)

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entity_id"])
        for eid in kept:
            w.writerow([eid])

    json.dump({
        "resolved_count": len(kept),
        "below_floor_count": below,
        "quality_floor": args.quality_floor,
        "out": args.out,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if no_id:
        print(f"dedupe_resolve_matches: skipped {no_id} rows with no entity_id", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
